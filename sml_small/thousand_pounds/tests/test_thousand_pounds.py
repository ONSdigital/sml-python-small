import pytest
from thousand_pounds import Target_variable, Thousands_output, run

testdata = [
    pytest.param(
        "q100",
        50000000,  # principal value/variable
        50000,  # predictive
        15000,  # auxiliary
        1350,  # upper limit
        350,  # lower limit
        [Target_variable("q101", 500), Target_variable("q102", 1000), Target_variable("q103", 1500), Target_variable("q104", None)],
        Thousands_output(
            "q100",
            50000000,
            50000.0,
            [Target_variable("q101", 500, 0.5), Target_variable("q102", 1000, 1), Target_variable("q103", 1500, 1.5), Target_variable("q104", None, None)],
            1000.0,
            "C",
        ),
        id="Given full config - outputs adjusted for all target variables",
    ),
    pytest.param(
        "q200",
        60000000,  # principal value/variable
        150000,  # predictive
        None,  # auxiliary
        1350,
        350,
        [],
        Thousands_output("q200", 60000000, 60000.0, [], 400.0, "C"),
        id="Given config(missing auxiliary) - outputs adjusted for all target variables",
    ),
    pytest.param(
        "q300",
        269980,  # principal value/variable
        None,  # predictive
        200,  # auxiliary
        1350,
        350,
        [],
        Thousands_output("q300", 269980, 269.980, [], 1349.9, "C"),
        id="Given config(missing predictive) - outputs adjusted for all target variables",
    ),
    pytest.param(
        "q400",
        80000000,  # principal value/variable
        None,  # predictive
        None,  # auxiliary
        1350,
        350,
        [],
        Thousands_output("q400", 80000000, 80000000.0, [], None, "E", "Both predictive and auxiliary values are missing/zero"),
        id="Given config(missing predictive and auxiliery) - default outputs and error indicated",
    ),
    pytest.param(
        "q450",
        8000,  # principal value/variable
        0,  # predictive
        0,  # auxiliary
        1350,
        350,
        [Target_variable("q451", 500), Target_variable("q452", 1000)],
        Thousands_output(
            "q450",
            8000,
            8000,
            [Target_variable("q451", 500), Target_variable("q452", 1000)],
            None,
            "E",
            "Both predictive and auxiliary values are missing/zero",
        ),
        id="Given config(predictive and auxiliery are 0) - default outputs and error indicated",
    ),
    pytest.param(
        "q500",
        None,  # principal value/variable
        10,  # predictive
        20,  # auxiliary
        1350,
        350,
        [Target_variable("q501", 500), Target_variable("q502", 1000)],
        Thousands_output("q500", None, None, [Target_variable("q501", 500), Target_variable("q502", 1000)], None, "E", "principal_variable is missing"),
        id="Given config(missing principal variable) - default outputs and error indicated",
    ),
    pytest.param(
        "q600",
        0,  # principal value/variable
        10,  # predictive
        20,  # auxiliary
        1350,
        350,
        [Target_variable("q601", 500), Target_variable("q602", 1000)],
        Thousands_output("q600", 0, 0, [Target_variable("q601", 500, 500), Target_variable("q602", 1000, 1000)], 0, "N", ""),
        id="Given config(principal variable of 0) - default outputs and error indicated",
    ),
    pytest.param(
        "q700",
        3500,  # principal value/variable
        10,  # predictive
        20,  # auxiliary
        1350,
        350,
        [Target_variable("q701", 500)],
        Thousands_output("q700", 3500, 3500, [Target_variable("q701", 500, 500)], 350, "N", ""),
        id="Given valid config but exactly on lower limit threshold - do not adjust",
    ),
    pytest.param(
        "q800",
        13500,  # principal value/variable
        10,  # predictive
        20,  # auxiliary
        1350,  # Upper limit
        350,  # lower limit
        [Target_variable("q801", 500)],
        Thousands_output("q800", 13500, 13500, [Target_variable("q801", 500, 500)], 1350, "N", ""),
        id="Given valid config but exactly on upper limit threshold - do not adjust",
    ),
    pytest.param(
        "",
        0,
        -1,  # predictive
        -1,  # auxiliary
        0,  # upper limit
        1,  # lower limit
        [],
        Thousands_output("", 0, 0, [], None, "E", "At least one of the lower or upper limits are 0 or missing"),
        id="Upper limit is 0 - default outputs and error indicated",
    ),
    pytest.param(
        "",
        0,
        -1,  # predictive
        -1,  # auxiliary
        1,  # upper limit
        0,  # lower limit
        [],
        Thousands_output("", 0, 0, [], None, "E", "At least one of the lower or upper limits are 0 or missing"),
        id="Lower limit is 0 - default outputs and error indicated",
    ),
    pytest.param(
        "Ham",
        "Cheese",
        "Toast",  # predictive
        "Jam",  # auxiliary
        "Rhubarb",  # upper limit
        "Custard",  # lower limit
        [],
        Thousands_output("Ham", "Cheese", "Cheese", [], None, "E", "unsupported operand type(s) for /: 'str' and 'str'"),
        id="Lower limit is 0 - default outputs and error indicated",
    ),
]


@pytest.mark.parametrize("principal_identifier, principal_variable, predictive, auxiliary, upper_limit, lower_limit, target_variables, expected", testdata)
def test__run__given_valid_config__returns_adjusted_figures(
    principal_identifier, principal_variable, predictive, auxiliary, upper_limit, lower_limit, target_variables, expected
):
    assert run(principal_identifier, principal_variable, predictive, auxiliary, upper_limit, lower_limit, target_variables) == expected
