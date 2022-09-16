import pytest
from pounds_thousands import Target_variable, Thousands_output, run

testdata = [
    pytest.param(
        "q100",
        50000000,  # principle value/variable
        50000,  # predicted
        15000,  # auxiliary
        1350,  # upper limit
        350,  # lower limit
        [Target_variable("q101", 500), Target_variable("q102", 1000), Target_variable("q103", 1500), Target_variable("q104", None)],
        Thousands_output(
            "q100",
            50000.0,
            [Target_variable("q101", 0.5), Target_variable("q102", 1), Target_variable("q103", 1.5), Target_variable("q104", None)],
            1000.0,
            "C",
        ),
        id="Given full config - outputs djusted for all target variables",
    ),
    pytest.param(
        "q200",
        60000000,  # principle value/variable
        150000,  # predicted
        None,  # auxiliary
        1350,
        350,
        [],
        Thousands_output("q200", 60000.0, [], 400.0, "C"),
        id="Given config(missing auxiliary) - outputs djusted for all target variables",
    ),
    pytest.param(
        "q300",
        269980,  # principle value/variable
        None,  # predicted
        200,  # auxiliary
        1350,
        350,
        [],
        Thousands_output("q300", 269.980, [], 1349.9, "C"),
        id="Given config(missing predicted) - outputs djusted for all target variables",
    ),
    pytest.param(
        "q400",
        80000000,  # principle value/variable
        None,  # predicted
        None,  # auxiliary
        1350,
        350,
        [],
        Thousands_output("q400", 80000000.0, [], None, "E", "Both predicted and auxiliary values are missing/zero"),
        id="Given config(missing predicted and auxiliery) - default outputs and error indicated",
    ),
    pytest.param(
        "q450",
        8000,  # principle value/variable
        0,  # predicted
        0,  # auxiliary
        1350,
        350,
        [Target_variable("q451", 500), Target_variable("q452", 1000)],
        Thousands_output(
            "q450", 8000, [Target_variable("q451", 500), Target_variable("q452", 1000)], None, "E", "Both predicted and auxiliary values are missing/zero"
        ),
        id="Given config(predicted and auxiliery are 0) - default outputs and error indicated",
    ),
    pytest.param(
        "q500",
        None,  # principle value/variable
        10,  # predicted
        20,  # auxiliary
        1350,
        350,
        [Target_variable("q501", 500), Target_variable("q502", 1000)],
        Thousands_output("q500", None, [Target_variable("q501", 500), Target_variable("q502", 1000)], None, "E", "Principle_variable is missing"),
        id="Given config(missing principle variable) - default outputs and error indicated",
    ),
    pytest.param(
        "q600",
        0,  # principle value/variable
        10,  # predicted
        20,  # auxiliary
        1350,
        350,
        [Target_variable("q601", 500), Target_variable("q602", 1000)],
        Thousands_output("q600", 0, [Target_variable("q601", 500), Target_variable("q602", 1000)], 0, "N", ""),
        id="Given config(principle variable of 0) - default outputs and error indicated",
    ),
    pytest.param(
        "q700",
        3500,  # principle value/variable
        10,  # predicted
        20,  # auxiliary
        1350,
        350,
        [Target_variable("q701", 500)],
        Thousands_output("q700", 3500, [Target_variable("q701", 500)], 350, "N", ""),
        id="Given valid config but exactly on lower limit threshold - do not adjust",
    ),
    pytest.param(
        "",
        0,
        -1,  # predicted
        -1,  # auxiliary
        0,
        0,
        [],
        Thousands_output("", 0, [], None, "E", "The lower and upper limits are both 0"),
        id="Upper and lower limits are 0 - default outputs and error indicated",
    ),
]


@pytest.mark.parametrize("principle_identifier, principle_variable, predicted, auxiliary, upper_limit, lower_limit, target_variables, expected", testdata)
def test__run__given_valid_config__returns_adjusted_figures(
    principle_identifier, principle_variable, predicted, auxiliary, upper_limit, lower_limit, target_variables, expected
):
    assert run(principle_identifier, principle_variable, predicted, auxiliary, upper_limit, lower_limit, target_variables) == expected
