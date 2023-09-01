import pytest
from sml_small.editing.thousand_pounds.thousand_pounds import Target_variable, Thousands_output, run

testdata = [
    pytest.param(
        "q100",
        50000000,  # principal value/variable
        50000,  # predictive
        15000,  # auxiliary
        1350,  # upper limit
        350,  # lower limitx
        [Target_variable("q101", 500), Target_variable("q102", 1000), Target_variable("q103", 12345), Target_variable("q104", 0)],
        Thousands_output(
            "q100",
            50000000,
            50000.0,
            [Target_variable("q101", 500, 0.5), Target_variable("q102", 1000, 1), Target_variable("q103", 12345, 12.35), Target_variable("q104", 0, 0)],
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
        Thousands_output("q400", 80000000, 80000000.0, [], None, "E", "Both predictive and auxiliary values are missing"),
        id="Given config(missing predictive and auxiliary) - default outputs and error indicated",
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
            [Target_variable("q451", 500, 500), Target_variable("q452", 1000, 1000)],
            None,
            "N",
            "",
        ),
        id="Given config(predictive and auxiliary are 0) - No error, not adjusted",
    ),
    pytest.param(
        "q450",
        8000,  # principal value/variable
        0,  # predictive
        None,  # auxiliary
        1350,
        350,
        [Target_variable("q451", 500), Target_variable("q452", 1000)],
        Thousands_output(
            "q450",
            8000,
            8000,
            [Target_variable("q451", 500, 500), Target_variable("q452", 1000, 1000)],
            None,
            "N",
            "",
        ),
        id="Given config(predictive 0 and auxiliary is None) - No error, not adjusted",
    ),
    pytest.param(
        "q500",
        None,  # principal value/variable
        10,  # predictive
        20,  # auxiliary
        1350,
        350,
        [Target_variable("q501", 500), Target_variable("q502", 1000)],
        Thousands_output(
            "q500", None, None, [Target_variable("q501", 500, 500), Target_variable("q502", 1000, 1000)], None, "E", "principal_variable is missing"
        ),
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
        0,  # principal
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
        0,  # principal
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
        "Cheese",  # principal
        1,  # predictive
        2,  # auxiliary
        3,  # upper limit
        4,  # lower limit
        [],
        Thousands_output("Ham", "Cheese", "Cheese", [], None, "E", "Attribute 'principal_variable' is missing or not a valid number"),
        id="Invalid format for principal variable",
    ),
    pytest.param(
        "Dummy",
        0,  # principal
        "12 34 56",  # predictive
        "2",  # auxiliary
        "3",  # upper limit
        "4",  # lower limit
        [],
        Thousands_output("Dummy", 0, 0, [], None, "E", "Attribute 'predictive' is missing or not a valid number"),
        id="Invalid format for predictive variable",
    ),
    pytest.param(
        "Dummy",
        10,  # principal
        "123456",  # predictive
        "",  # auxiliary
        "33 56 767",  # upper limit
        "4",  # lower limit
        [],
        Thousands_output("Dummy", 10, 10, [], None, "E", "Attribute 'upper_limit' is missing or not a valid number"),
        id="Invalid format for upper_limit variable",
    ),
    pytest.param(
        "Dummy",
        10,  # principal
        "123456",  # predictive
        "",  # auxiliary
        "1234",  # upper limit
        "98123x21",  # lower limit
        [],
        Thousands_output("Dummy", 10, 10, [], None, "E", "Attribute 'lower_limit' is missing or not a valid number"),
        id="Invalid format for lower_limit variable",
    ),
    pytest.param(
        "Dummy",
        10,  # principal
        56,  # predictive
        23,  # auxiliary
        350,  # upper limit
        351,  # lower limit
        [],
        Thousands_output("Dummy", 10, 10, [], None, "E", "Lower limit is larger than the upper limit (351:350)"),
        id="Lower limit is larger than the upper limit",
    ),
]


@pytest.mark.parametrize("principal_identifier, principal_variable, predictive, auxiliary, upper_limit, lower_limit, target_variables, expected", testdata)
def test__run__given_valid_config__returns_adjusted_figures(
    principal_identifier, principal_variable, predictive, auxiliary, upper_limit, lower_limit, target_variables, expected
):
    assert run(principal_identifier, principal_variable, predictive, auxiliary, upper_limit, lower_limit, target_variables) == expected
