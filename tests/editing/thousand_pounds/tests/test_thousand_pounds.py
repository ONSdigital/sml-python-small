import pytest

from sml_small.editing.thousand_pounds.thousand_pounds import (Target_variable, Thousands_output,
                                                               adjust_target_variables, adjust_value,
                                                               calculate_error_ratio, determine_predictive_value,
                                                               determine_tpc_marker, is_within_threshold, run,
                                                               validate_input, TPException)
from sml_small.utils.error_utils import (get_boundary_error, get_mandatory_param_error,
                                         get_one_of_params_mandatory_error, get_params_is_not_a_number_error)

EXCEPTION_FAIL_MESSAGE = (
    "{test_id} : Expected no exception, but got {exception_type}: {exception_msg}"
)


class TestRun:
    @pytest.mark.parametrize(
        "principal_identifier, principal_variable, predictive, auxiliary, upper_limit, lower_limit, target_variables, "
        "expected, test_id",
        [
            (
                "q100",
                50000000,  # principal value/variable
                50000,  # predictive
                15000,  # auxiliary
                1350,  # upper limit
                350,  # lower limit
                [
                    Target_variable("q101", 500),
                    Target_variable("q102", 1000),
                    Target_variable("q103", 12345),
                    Target_variable("q104", 0),
                ],
                Thousands_output(
                    "q100",
                    50000000,
                    50000.0,
                    [
                        Target_variable("q101", 500, 0.5),
                        Target_variable("q102", 1000, 1),
                        Target_variable("q103", 12345, 12.35),
                        Target_variable("q104", 0, 0),
                    ],
                    1000.0,
                    "C",
                ),
                "Given full config - outputs adjusted for all target variables",
            ),
            (
                "q200",
                60000000,  # principal value/variable
                150000,  # predictive
                None,  # auxiliary
                1350,
                350,
                [],
                Thousands_output("q200", 60000000, 60000.0, [], 400.0, "C"),
                "Given config(missing auxiliary) - outputs adjusted for all target variables"
            ),
            (
                "q300",
                269980,  # principal value/variable
                None,  # predictive
                200,  # auxiliary
                1350,
                350,
                [],
                Thousands_output("q300", 269980, 269.980, [], 1349.9, "C"),
                "Given config(missing predictive) - outputs adjusted for all target variables",
            ),
            (
                "q400",
                80000000,  # principal value/variable
                None,  # predictive
                None,  # auxiliary
                1350,
                350,
                [],
                TPException(
                    "identifier: q400",
                    ValueError(
                        get_one_of_params_mandatory_error(["predictive", "auxiliary"])
                    )
                ),
                "Given config(missing predictive and auxiliary) - default outputs and error indicated",
            ),
            (
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
                ),
                "Given config(predictive and auxiliary are 0) - No error, not adjusted",
            ),
            (
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
                ),
                "Given config(predictive 0 and auxiliary is None) - No error, not adjusted",
            ),
            (
                "q500",
                None,  # principal value/variable
                10,  # predictive
                20,  # auxiliary
                1350,
                350,
                [Target_variable("q501", 500), Target_variable("q502", 1000)],
                TPException(
                    "identifier: q500",
                    ValueError(
                        get_mandatory_param_error("principal_variable")
                    )
                ),
                "Given config(missing principal variable) - default outputs and error indicated",
            ),
            (
                "q600",
                0,  # principal value/variable
                10,  # predictive
                20,  # auxiliary
                1350,
                350,
                [Target_variable("q601", 500), Target_variable("q602", 1000)],
                Thousands_output(
                    "q600",
                    0,
                    0,
                    [Target_variable("q601", 500, 500), Target_variable("q602", 1000, 1000)],
                    0,
                    "N",
                ),
                "Given config(principal variable of 0) - default outputs and error indicated",
            ),
            (
                "q700",
                3500,  # principal value/variable
                10,  # predictive
                20,  # auxiliary
                1350,
                350,
                [Target_variable("q701", 500)],
                Thousands_output(
                    "q700", 3500, 3500, [Target_variable("q701", 500, 500)], 350, "N",
                ),
                "Given valid config but exactly on lower limit threshold - do not adjust",
            ),
            (
                "q800",
                13500,  # principal value/variable
                10,  # predictive
                20,  # auxiliary
                1350,  # Upper limit
                350,  # lower limit
                [Target_variable("q801", 500)],
                Thousands_output(
                    "q800", 13500, 13500, [Target_variable("q801", 500, 500)], 1350, "N",
                ),
                "Given valid config but exactly on upper limit threshold - do not adjust",
            ),
            (
                "q900",
                0,  # principal
                -1,  # predictive
                -1,  # auxiliary
                0,  # upper limit
                1,  # lower limit
                [],
                TPException(
                    "identifier: q900",
                    ValueError(get_mandatory_param_error("upper_limit"))
                ),
                "Upper limit is 0 - default outputs and error indicated",
            ),
            (
                "q1000",
                0,  # principal
                -1,  # predictive
                -1,  # auxiliary
                1,  # upper limit
                0,  # lower limit
                [],
                TPException(
                    "identifier: q1000",
                    ValueError(get_mandatory_param_error("lower_limit"))
                ),
                "Lower limit is 0 - default outputs and error indicated",
            ),
            (
                "q1100",
                "Cheese",  # principal
                1,  # predictive
                2,  # auxiliary
                3,  # upper limit
                4,  # lower limit
                [],
                TPException(
                    "identifier: q1100",
                    ValueError(get_params_is_not_a_number_error("principal_variable")),
                ),

                "Invalid format for principal variable",
            ),
            (
                "q1200",
                0,  # principal
                "12 34 56",  # predictive
                "2",  # auxiliary
                "3",  # upper limit
                "4",  # lower limit
                [],
                TPException(
                    "identifier: q1200",
                    ValueError(get_params_is_not_a_number_error("predictive")),
                ),
                "Invalid format for predictive variable",
            ),
            (
                "q1300",
                10,  # principal
                "123456",  # predictive
                "",  # auxiliary
                "33 56 767",  # upper limit
                "4",  # lower limit
                [],
                TPException(
                    "identifier: q1300",
                    ValueError(get_params_is_not_a_number_error("upper_limit")),
                ),
                "Invalid format for upper_limit variable",
            ),
            (
                "q1400",
                10,  # principal
                "123456",  # predictive
                "",  # auxiliary
                "1234",  # upper limit
                "98123x21",  # lower limit
                [],
                TPException(
                    "identifier: q1400",
                    ValueError(get_params_is_not_a_number_error("lower_limit")),
                ),
                "Invalid format for lower_limit variable",
            ),
            (
                "q1500",
                10,  # principal
                56,  # predictive
                23,  # auxiliary
                350,  # upper limit
                351,  # lower limit
                [],
                TPException(
                    "identifier: q1500",
                    ValueError(get_boundary_error([351.0, 350.0])),
                ),
                "Lower limit is larger than the upper limit",
            ),
        ]
    )
    def test__run__given_valid_config__returns_adjusted_figures(
        self,
        principal_identifier,
        principal_variable,
        predictive,
        auxiliary,
        upper_limit,
        lower_limit,
        target_variables,
        expected,
        test_id
    ):
        if isinstance(expected, Thousands_output):
            try:
                result = run(
                    principal_identifier,
                    principal_variable,
                    predictive,
                    auxiliary,
                    upper_limit,
                    lower_limit,
                    target_variables,
                )
                assert result == expected

            except Exception as e:
                pytest.fail(
                    EXCEPTION_FAIL_MESSAGE.format(
                        test_id=test_id,
                        exception_type=type(e).__name__,
                        exception_msg=str(e),
                    )
                )
        else:
            with pytest.raises(Exception) as exc_info:
                run(
                    principal_identifier,
                    principal_variable,
                    predictive,
                    auxiliary,
                    upper_limit,
                    lower_limit,
                    target_variables,
                )
            assert (str(exc_info.value)) == str(expected)


class TestValidateInput:
    @pytest.mark.parametrize(
        "predictive, auxiliary, principal_variable, lower_limit, upper_limit, target_variables, expected_result, "
        "test_id",
        [
            (
                "500",
                None,
                200,
                50,
                100,
                [Target_variable("q501", 500), Target_variable("q502", 1000)],
                (
                    500.0,
                    None,
                    200.0,
                    50.0,
                    100.0,
                    [Target_variable("q501", 500.0), Target_variable("q502", 1000.0)],
                ),
                "Test 1: Predictive as an interpretable string",
            ),
            (
                "five hundred",
                None,
                200,
                50,
                100,
                [Target_variable("q501", 500), Target_variable("q502", 1000)],
                ValueError(get_params_is_not_a_number_error("predictive")),
                "Test 2: Predictive as a non-interpretable string",
            ),
            (
                None,
                "500",
                200,
                50,
                100,
                [Target_variable("q501", 500), Target_variable("q502", 1000)],
                (
                    None,
                    500.0,
                    200.0,
                    50.0,
                    100.0,
                    [Target_variable("q501", 500.0), Target_variable("q502", 1000.0)],
                ),
                "Test 3: Auxiliary as an interpretable string",
            ),
            (
                None,
                "five hundred",
                200,
                50,
                100,
                [Target_variable("q501", 500), Target_variable("q502", 1000)],
                ValueError(get_params_is_not_a_number_error("auxiliary")),
                "Test 4: Auxiliary as a non-interpretable string",
            ),
            (
                None,
                None,
                200,
                50,
                100,
                [Target_variable("q501", 500), Target_variable("q502", 1000)],
                ValueError(
                    get_one_of_params_mandatory_error(["predictive", "auxiliary"])
                ),
                "Test 5: Predictive and Auxiliary not input",
            ),
            (
                500,
                600,
                None,
                50,
                100,
                [Target_variable("q501", 500), Target_variable("q502", 1000)],
                ValueError(get_mandatory_param_error("principal_variable")),
                "Test 6: Principal Variable not input",
            ),
            (
                500,
                600,
                "200",
                50,
                100,
                [Target_variable("q501", 500), Target_variable("q502", 1000)],
                (
                    500.0,
                    600.0,
                    200.0,
                    50.0,
                    100.0,
                    [Target_variable("q501", 500.0), Target_variable("q502", 1000.0)],
                ),
                "Test 7: Principal Variable is an interpretable string",
            ),
            (
                500,
                600,
                "two hundred",
                50,
                100,
                [Target_variable("q501", 500), Target_variable("q502", 1000)],
                ValueError(get_params_is_not_a_number_error("principal_variable")),
                "Test 8: Principal Variable is a non-interpretable string",
            ),
            (
                500,
                600,
                200,
                None,
                100,
                [Target_variable("q501", 500), Target_variable("q502", 1000)],
                ValueError(get_mandatory_param_error("lower_limit")),
                "Test 9: Lower Limit not input",
            ),
            (
                500,
                600,
                200,
                "50",
                100,
                [Target_variable("q501", 500), Target_variable("q502", 1000)],
                (
                    500.0,
                    600.0,
                    200.0,
                    50.0,
                    100.0,
                    [Target_variable("q501", 500.0), Target_variable("q502", 1000.0)],
                ),
                "Test 10: Lower Limit is an interpretable string",
            ),
            (
                500,
                600,
                200,
                "fifty",
                100,
                [Target_variable("q501", 500), Target_variable("q502", 1000)],
                ValueError(get_params_is_not_a_number_error("lower_limit")),
                "Test 11: Lower Limit is a non-interpretable string",
            ),
            (
                500,
                600,
                200,
                50,
                None,
                [Target_variable("q501", 500), Target_variable("q502", 1000)],
                ValueError(get_mandatory_param_error("upper_limit")),
                "Test 12: Upper Limit not input",
            ),
            (
                500,
                600,
                200,
                50,
                "100",
                [Target_variable("q501", 500), Target_variable("q502", 1000)],
                (
                    500.0,
                    600.0,
                    200.0,
                    50.0,
                    100.0,
                    [Target_variable("q501", 500.0), Target_variable("q502", 1000.0)],
                ),
                "Test 13: Upper Limit is an interpretable string",
            ),
            (
                500,
                600,
                200,
                50,
                "one hundred",
                [Target_variable("q501", 500), Target_variable("q502", 1000)],
                ValueError(get_params_is_not_a_number_error("upper_limit")),
                "Test 14: Upper Limit is a non-interpretable string",
            ),
            (
                500,
                600,
                200,
                100,
                50,
                [Target_variable("q501", 500), Target_variable("q502", 1000)],
                ValueError(get_boundary_error([100.0, 50.0])),
                "Test 15: Lower Limit is greater than Upper Limit",
            ),
            (
                500,
                600,
                200,
                50,
                100,
                [Target_variable("q501", "500"), Target_variable("q502", 1000)],
                (
                    500.0,
                    600.0,
                    200.0,
                    50.0,
                    100.0,
                    [Target_variable("q501", 500.0), Target_variable("q502", 1000.0)],
                ),
                "Test 16: Target Variable is an interpretable string",
            ),
            (
                500,
                600,
                200,
                50,
                100,
                [
                    Target_variable("q501", "five hundred"),
                    Target_variable("q502", 1000),
                ],
                ValueError(get_params_is_not_a_number_error("q501")),
                "Test 17: Target Variable is a non-interpretable string",
            ),
        ],
    )
    def test_validate_input(
        self,
        predictive,
        auxiliary,
        principal_variable,
        lower_limit,
        upper_limit,
        target_variables,
        expected_result,
        test_id,
    ):
        if isinstance(expected_result, tuple):
            try:
                result = validate_input(
                    predictive=predictive,
                    auxiliary=auxiliary,
                    principal_variable=principal_variable,
                    lower_limit=lower_limit,
                    upper_limit=upper_limit,
                    target_variables=target_variables,
                )
                assert result == expected_result
            except Exception as e:
                pytest.fail(
                    EXCEPTION_FAIL_MESSAGE.format(
                        test_id=test_id,
                        exception_type=type(e).__name__,
                        exception_msg=str(e),
                    )
                )
        else:
            with pytest.raises(Exception) as exc_info:
                validate_input(
                    predictive=predictive,
                    auxiliary=auxiliary,
                    principal_variable=principal_variable,
                    lower_limit=lower_limit,
                    upper_limit=upper_limit,
                    target_variables=target_variables,
                )
                print(exc_info.value)
            assert (str(exc_info.value)) == str(expected_result)


class TestDetermineTpcMarker:
    @pytest.mark.parametrize(
        "do_adjustment, expected_result, test_id",
        [
            (True, "C", "Test 1: do_adjustment is True"),
            (False, "N", "Test 1: do_adjustment is False"),
            (None, "N", "Test 1: do_adjustment is None"),
        ],
    )
    def test_determine_tpc_marker(
        self,
        do_adjustment,
        expected_result,
        test_id,
    ):
        try:
            result = determine_tpc_marker(do_adjustment)
            assert result == expected_result
        except Exception as e:
            pytest.fail(
                EXCEPTION_FAIL_MESSAGE.format(
                    test_id=test_id,
                    exception_type=type(e).__name__,
                    exception_msg=str(e),
                )
            )


class TestDeterminePredictiveValue:
    @pytest.mark.parametrize(
        "predictive, auxiliary, expected_result, test_id",
        [
            (50, 100, 50, "Test 1: Both input, Predictive Output"),
            (None, 100, 100, "Test 2: Predictive missing, auxiliary Output"),
            (50, None, 50, "Test 3: Auxiliary missing, Predictive Output"),
            (0, None, 0, "Test 4: Predictive = 0, Auxiliary missing, 0 Output"),
        ],
    )
    def test_determine_predictive_value(
        self,
        predictive,
        auxiliary,
        expected_result,
        test_id,
    ):
        try:
            result = determine_predictive_value(predictive, auxiliary)
            assert result == expected_result
        except Exception as e:
            pytest.fail(
                EXCEPTION_FAIL_MESSAGE.format(
                    test_id=test_id,
                    exception_type=type(e).__name__,
                    exception_msg=str(e),
                )
            )


class TestCalculateErrorRatio:
    @pytest.mark.parametrize(
        "principal_variable, predictive_value, expected_result, test_id",
        [
            (10.0, 5.0, 2.0, "Test 1: Both values are float"),
        ],
    )
    def test_calculate_error_ratio(
        self,
        principal_variable,
        predictive_value,
        expected_result,
        test_id,
    ):
        try:
            result = calculate_error_ratio(principal_variable, predictive_value)
            assert result == expected_result
        except Exception as e:
            pytest.fail(
                EXCEPTION_FAIL_MESSAGE.format(
                    test_id=test_id,
                    exception_type=type(e).__name__,
                    exception_msg=str(e),
                )
            )


class TestIsWithinThreshold:
    @pytest.mark.parametrize(
        "error_ratio, lower_limit, upper_limit, expected_result, test_id",
        [
            (50, 25, 100, True, "Test 1: error ratio within boundary"),
            (150, 25, 100, False, "Test 2: error ratio above boundary"),
            (10, 25, 100, False, "Test 3: error ratio below boundary"),
            (25, 25, 100, False, "Test 4: error ratio == lower boundary"),
            (50, 100, 100, False, "Test 5: error ratio == upper boundary"),
        ],
    )
    def test_is_within_threshold(
        self,
        error_ratio,
        lower_limit,
        upper_limit,
        expected_result,
        test_id,
    ):
        try:
            result = is_within_threshold(error_ratio, lower_limit, upper_limit)
            assert result == expected_result
        except Exception as e:
            pytest.fail(
                EXCEPTION_FAIL_MESSAGE.format(
                    test_id=test_id,
                    exception_type=type(e).__name__,
                    exception_msg=str(e),
                )
            )


class TestAdjustValue:
    @pytest.mark.parametrize(
        "value, expected_result, test_id",
        [
            (10000, 10, "Test 1: Perform adjustment"),
            (None, None, "Test 2: value is None"),
        ],
    )
    def test_adjust_value(
        self,
        value,
        expected_result,
        test_id,
    ):
        try:
            result = adjust_value(value)
            assert result == expected_result
        except Exception as e:
            pytest.fail(
                EXCEPTION_FAIL_MESSAGE.format(
                    test_id=test_id,
                    exception_type=type(e).__name__,
                    exception_msg=str(e),
                )
            )


class TestAdjustTargetVariables:
    @pytest.mark.parametrize(
        "do_adjustment, target_variables, expected_result, test_id",
        [
            (
                True,
                [Target_variable("q501", 500000.4332), Target_variable("q502", 1000)],
                [
                    Target_variable("q501", 500000.4332, 500.0),
                    Target_variable("q502", 1000, 1.0),
                ],
                "Test 1: do_adjustment == True, Target variable is appropriately rounded down",
            ),
            (
                True,
                [Target_variable("q501", 999999.99999), Target_variable("q502", 1000)],
                [
                    Target_variable("q501", 999999.99999, 1000.0),
                    Target_variable("q502", 1000, 1.0),
                ],
                "Test 2: Target variable is appropriately rounded up",
            ),
            (
                False,
                [Target_variable("q501", 500), Target_variable("q502", 1000)],
                [
                    Target_variable("q501", 500, 500),
                    Target_variable("q502", 1000, 1000),
                ],
                "Test 3: do_adjustment == False Target variable is not rounded",
            ),
        ],
    )
    def test_adjust_target_variables(
        self, do_adjustment, target_variables, expected_result, test_id
    ):
        try:
            result = adjust_target_variables(do_adjustment, target_variables)
            assert result == expected_result
        except Exception as e:
            pytest.fail(
                EXCEPTION_FAIL_MESSAGE.format(
                    test_id=test_id,
                    exception_type=type(e).__name__,
                    exception_msg=str(e),
                )
            )
