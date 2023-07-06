import random
from decimal import Decimal, getcontext

import pytest

from sml_small.totals_and_components.totals_and_components import (ComponentPair, TACException, calculate_prior_period,
                                                                   check_absolute_difference_threshold,
                                                                   check_auxiliary_value,
                                                                   check_percentage_difference_threshold,
                                                                   check_sum_components_predictive, check_zero_errors,
                                                                   correct_components, correct_total,
                                                                   determine_error_detection, error_correction,
                                                                   set_predictive_value, sum_components,
                                                                   totals_and_components, validate_input)

EXCEPTION_FAIL_MESSAGE = (
    "{test_id} : Expected no exception, but got {exception_type}: {exception_msg}"
)


#  Class used to force str() cast during validation to fail as all standard library python types have
#  valid string conversions
class NoString:
    def __str__(self):
        pass


class TestValidateInput:
    @pytest.mark.parametrize(
        "identifier, total, components, amend_total, period, predictive_period, period_onset, predictive, "
        "auxiliary, absolute_difference_threshold, "
        "percentage_difference_threshold, precision, expected_result, test_id",
        [
            (
                "A",
                100,
                [
                    ComponentPair(original_value=1, final_value=None),
                    ComponentPair(original_value=2, final_value=None),
                    ComponentPair(original_value=3, final_value=None),
                    ComponentPair(original_value=4, final_value=None),
                ],
                True,
                "202203",
                "202201",
                1,
                100.0,
                300.0,
                20,
                0.1,
                6,
                (
                    100,
                    [
                        ComponentPair(original_value=1, final_value=None),
                        ComponentPair(original_value=2, final_value=None),
                        ComponentPair(original_value=3, final_value=None),
                        ComponentPair(original_value=4, final_value=None),
                    ],
                    100.0,
                    300.0,
                    20,
                    0.1,
                    6,
                    1,
                ),
                "Test 1: Correct values test",
                # Test to ensure we have a happy path walkthrough
            ),
            (
                "B",
                100.0,
                [
                    ComponentPair(original_value=1, final_value=None),
                    ComponentPair(original_value=2, final_value=None),
                    ComponentPair(original_value=3, final_value=None),
                    ComponentPair(original_value=4, final_value=None),
                ],
                False,
                "202303",
                "202202",
                1,
                100.0,
                104.0,
                105.0,
                None,
                28,
                (
                    100.0,
                    [
                        ComponentPair(original_value=1, final_value=None),
                        ComponentPair(original_value=2, final_value=None),
                        ComponentPair(original_value=3, final_value=None),
                        ComponentPair(original_value=4, final_value=None),
                    ],
                    100.0,
                    104.0,
                    105.0,
                    None,
                    28,
                    1,
                ),
                "Test 2: None value for percentage difference threshold",
                # Test to see what happens when a none value is entered by
                # the user for the percentage difference threshold
                # this will not trigger an error exception
            ),
            (
                "C",
                100.0,
                [
                    ComponentPair(original_value=1, final_value=None),
                    ComponentPair(original_value=2, final_value=None),
                    ComponentPair(original_value=3, final_value=None),
                    ComponentPair(original_value=4, final_value=None),
                ],
                True,
                "202109",
                "202207",
                1,
                100.0,
                104.0,
                None,
                20,
                28,
                (
                    100.0,
                    [
                        ComponentPair(original_value=1, final_value=None),
                        ComponentPair(original_value=2, final_value=None),
                        ComponentPair(original_value=3, final_value=None),
                        ComponentPair(original_value=4, final_value=None),
                    ],
                    100.0,
                    104.0,
                    None,
                    20,
                    28,
                    1,
                ),
                "Test 3: None value for absolute difference threshold",
                # Test to see what happens when a none value is entered by
                # the user for the absolute difference threshold
                # this will not trigger an error exception
            ),
            (
                "D",
                100,
                [
                    ComponentPair(original_value=1, final_value=None),
                    ComponentPair(original_value=2, final_value=None),
                    ComponentPair(original_value=3, final_value=None),
                    ComponentPair(original_value=4, final_value=None),
                ],
                False,
                "202003",
                "202006",
                1,
                None,  # missing predictive
                100.0,
                20,
                0.1,
                28,
                (
                    100,
                    [
                        ComponentPair(original_value=1, final_value=None),
                        ComponentPair(original_value=2, final_value=None),
                        ComponentPair(original_value=3, final_value=None),
                        ComponentPair(original_value=4, final_value=None),
                    ],
                    None,  # missing predictive does not trigger value error
                    100.0,
                    20,
                    0.1,
                    28,
                    1,
                ),
                "Test 4: Predictive is missing so method carries on",
                # Test to see what happens when a none value is entered by
                # the user for the predictive difference threshold
                # this will not trigger an error exception
            ),
            (
                "E",
                100.0,
                [],
                True,
                "202001",
                "202001",
                1,
                101.0,
                103.0,
                20,
                0.1,
                28,
                ValueError,
                "Test 5: Empty component list",
                # Test to see what happens when no component list is provided
                # we expect the appropriate value error to be raised.
            ),
            (
                "F",
                100.0,
                [
                    ComponentPair(original_value=None, final_value=None),
                    ComponentPair(original_value=2, final_value=None),
                    ComponentPair(original_value=3, final_value=None),
                    ComponentPair(original_value=4, final_value=None),
                ],
                True,
                "202002",
                "202001",
                1,
                101.0,
                103.0,
                20,
                0.1,
                28,
                ValueError,
                "Test 6: None in component list",
                # Test to see what happens when none value is within the
                # component list we expect the appropriate value error to be raised.
            ),
            (
                "G",
                "String",
                [
                    ComponentPair(original_value=1, final_value=None),
                    ComponentPair(original_value=2, final_value=None),
                    ComponentPair(original_value=3, final_value=None),
                    ComponentPair(original_value=4, final_value=None),
                ],
                False,
                "202203",
                "202203",
                1,
                102.0,
                104.0,
                20,
                0.1,
                28,
                ValueError,
                "Test 7: Invalid Total",
                # Test to see what happens when an invalid total
                # string value is provided
                # we expect the appropriate value error to be raised.
            ),
            (
                "H",
                100.0,
                [
                    ComponentPair(original_value=1, final_value=None),
                    ComponentPair(original_value=2, final_value=None),
                    ComponentPair(original_value=3, final_value=None),
                    ComponentPair(original_value=4, final_value=None),
                ],
                True,
                "2022005",
                "202204",
                1,
                "String",
                102.0,
                20,
                0.1,
                28,
                ValueError,
                "Test 8: Invalid predictive test",
                # Test to see what happens when an invalid predictive
                # string value is provided
                # we expect the appropriate value error to be raised.
            ),
            (
                "I",
                100.0,
                [
                    ComponentPair(original_value=1, final_value=None),
                    ComponentPair(original_value=2, final_value=None),
                    ComponentPair(original_value=3, final_value=None),
                    ComponentPair(original_value=4, final_value=None),
                ],
                False,
                "202202",
                "202201",
                1,
                101.0,
                "String",
                20,
                0.1,
                28,
                ValueError,
                "Test 9: Invalid auxiliary",
                # Test to see what happens when an invalid auxiliary
                # string value is provided
                # we expect the appropriate value error to be raised.
            ),
            (
                "J",
                100.0,
                [
                    ComponentPair(original_value=1, final_value=None),
                    ComponentPair(original_value=2, final_value=None),
                    ComponentPair(original_value=3, final_value=None),
                    ComponentPair(original_value=4, final_value=None),
                ],
                True,
                "202204",
                "202103",
                1,
                102.0,
                104.0,
                {20},
                0.1,
                28,
                ValueError,
                "Test 10: Invalid absolute difference threshold",
                # Test to see what happens when an invalid ABT
                # tuple value is provided
                # we expect the appropriate value error to be raised.
            ),
            (
                "K",
                100.0,
                [
                    ComponentPair(original_value=1, final_value=None),
                    ComponentPair(original_value=2, final_value=None),
                    ComponentPair(original_value=3, final_value=None),
                    ComponentPair(original_value=4, final_value=None),
                ],
                False,
                "201910",
                "201907",
                1,
                102.0,
                104.0,
                20,
                {2},
                28,
                ValueError,
                "Test 11: Invalid percentage difference threshold",
                # Test to see what happens when an invalid PDT
                # value is provided
                # we expect the appropriate value error to be raised.
            ),
            (
                "L",
                100.0,
                [
                    ComponentPair(original_value=1, final_value=None),
                    ComponentPair(original_value=2, final_value=None),
                    ComponentPair(original_value=3, final_value=None),
                    ComponentPair(original_value=4, final_value=None),
                ],
                True,
                "201896",
                "201893",
                1,
                102.0,
                89.0,
                None,
                None,
                28,
                ValueError,
                "Test 12: None value for percentage and absolute difference threshold",
                # Test to see what happens when an invalid PDT and ABT
                # values are provided
                # we expect the appropriate value error to be raised.
            ),
            (
                "M",
                100.0,
                [
                    ComponentPair(original_value=1, final_value=None),
                    ComponentPair(original_value=2, final_value=None),
                    ComponentPair(original_value=3, final_value=None),
                    ComponentPair(original_value=4, final_value=None),
                ],
                None,
                "201604",
                "201603",
                1,
                102.0,
                89.0,
                11,
                0.1,
                28,
                ValueError,
                "Test 13: None value for amend value",
                # Test to see what happens when an none amend total
                # value is provided
                # we expect the appropriate value error to be raised.
            ),
            (
                "N",
                None,
                [
                    ComponentPair(original_value=1, final_value=None),
                    ComponentPair(original_value=2, final_value=None),
                    ComponentPair(original_value=3, final_value=None),
                    ComponentPair(original_value=4, final_value=None),
                ],
                True,
                "201604",
                "201504",
                1,
                102.0,
                89.0,
                11,
                0.1,
                28,
                ValueError,
                "Test 14: None value for total",
                # Test to see what happens when an none
                # value for total value is provided
                # we expect the appropriate value error to be raised.
            ),
            (
                "O",
                100.0,
                [
                    ComponentPair(original_value=1, final_value=None),
                    ComponentPair(original_value=2, final_value=None),
                    ComponentPair(original_value=3, final_value=None),
                    ComponentPair(original_value=4, final_value=None),
                ],
                True,
                None,
                "201203",
                1,
                102.0,
                89.0,
                11,
                0.1,
                28,
                ValueError,
                "Test 15: None value for period",
                # Test to see what happens when an none
                # value for period value is provided
                # we expect the appropriate value error to be raised.
            ),
        ],
    )
    def test_validate_input(
        self,
        identifier,
        total,
        components,
        amend_total,
        period,
        predictive_period,
        period_onset,
        predictive,
        auxiliary,
        absolute_difference_threshold,
        percentage_difference_threshold,
        precision,
        expected_result,
        test_id,
    ):
        if isinstance(expected_result, tuple):
            try:
                result = validate_input(
                    identifier=identifier,
                    total=total,
                    components=components,
                    amend_total=amend_total,
                    predictive=predictive,
                    period=period,
                    predictive_period=predictive_period,
                    period_onset=period_onset,
                    auxiliary=auxiliary,
                    absolute_difference_threshold=absolute_difference_threshold,
                    percentage_difference_threshold=percentage_difference_threshold,
                    precision=precision,
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
            with pytest.raises(expected_result) as exc_info:
                validate_input(
                    identifier=identifier,
                    total=total,
                    components=components,
                    amend_total=amend_total,
                    predictive=predictive,
                    period=period,
                    predictive_period=predictive_period,
                    period_onset=period_onset,
                    auxiliary=auxiliary,
                    absolute_difference_threshold=absolute_difference_threshold,
                    percentage_difference_threshold=percentage_difference_threshold,
                    precision=precision,
                )
                print(exc_info.value)
            assert exc_info.type == expected_result


class TestSetPredictiveValue:
    @pytest.mark.parametrize(
        "predictive, auxiliary, total, predictive_period, period_onset, period, expected_result, test_id",
        [
            (
                100.0,
                None,
                10,
                "202301",
                1,
                "202302",
                100.0,
                "Test 1: Predictive Only",
                # Test for when a predictive value is provided,
                # we would not expect the check_auxiliary_value() function
                # to be triggered and the predictive value to remain unchanged
                # this is because the predictive period = prior period.
            ),
            (
                None,
                50.0,
                10,
                "202205",
                2,
                "202207",
                (50.0),
                "Test 2: Auxiliary Only"
                # Test for when a predictive value is not provided,
                # we would expect the check_auxiliary_value() function
                # to be triggered and the auxiliary value to be used in
                # place of the predictive value
            ),
            (
                None,
                None,
                10,
                "202101",
                12,
                "202201",
                10,
                "Test 3: Predictive and auxiliary are None",
                # Test for when a predictive and auxiliary value is not provided,
                # we would expect the check_auxiliary_value() function
                # to be triggered and the total value to be used in
                # place of the predictive value
            ),
            (
                100,
                90,
                10,
                "201907",
                12,
                "202106",
                90,
                "Test 4: Predictive and auxiliary exists but predictive period does not match prior period",
                # Test for when a predictive value is provided,
                # we would expect the check_auxiliary_value() function
                # to be triggered and the auxiliary value to be used in
                # place of the predictive value as predictive period != prior period
            ),
            (
                100,
                None,
                10,
                "202107",
                2,
                "202207",
                10,
                "Test 5: Predictive exists but period does not match prior period",
                # Test for when a predictive value is provided,
                # we would expect the check_auxiliary_value() function
                # to be triggered and the total value to be used in
                # place of the predictive value as predictive period != prior period
            ),
            (
                150.0,
                50.0,
                10,
                "202202",
                1,
                "202203",
                (150.0),
                "Test 6: All Inputs"
                # Test for when a all values is are provided,
                # we would not expect the check_auxiliary_value() function
                # to be triggered and the predictive is not changed as predictive period = prior period
            ),
            (
                100.0,
                None,
                10,
                "202201",
                24,
                "202305",
                10.0,
                "Test 7: Predictive and prior periods do not match and auxiliary is None so total is returned as predictive",
                # Test for when a predictive value is provided,
                # we would expect the check_auxiliary_value() function
                # to be triggered and the total value to be used in
                # place of the predictive value as predictive period != prior period
            ),
        ],
    )
    def test_set_predictive_value(
        self,
        predictive,
        auxiliary,
        total,
        predictive_period,
        period_onset,
        period,
        expected_result,
        test_id,
    ):
        try:
            result = set_predictive_value(
                predictive=predictive,
                auxiliary=auxiliary,
                total=total,
                predictive_period=predictive_period,
                period_onset=period_onset,
                period=period,
            )
            assert (
                result == expected_result
            ), f"Test {test_id} failed: Unexpected result. Result == {result}"
        except Exception as e:
            pytest.fail(
                EXCEPTION_FAIL_MESSAGE.format(
                    test_id=test_id,
                    exception_type=type(e).__name__,
                    exception_msg=str(e),
                )
            )


# Class to check if period_onset effects the predictive period to give the prior period
class TestCalculatePriorPeriod:
    @pytest.mark.parametrize(
        "period, period_onset, expected_result, test_id",
        [
            ("202203", 0, "202203", "Test 1: period_onset is 0"),
            ("202103", 1, "202102", "Test 2: period_onset is 1"),
            ("201903", 3, "201812", "Test 3: period_onset is 3"),
            ("202203", 4, "202111", "Test 4: period_onset is 4"),
            ("202004", 6, "201910", "Test 5: period_onset is 6"),
            ("201903", 12, "201803", "Test 6: period_onset is 12"),
            ("202203", 18, "202009", "Test 7: period_onset is 18"),
            ("201206", 24, "201006", "Test 8: period_onset is 24"),
            ("201705", 36, "201405", "Test 9: period_onset is 36"),
            ("201302", 48, "200902", "Test 10: period_onset is 48"),
            ("201503", 60, "201003", "Test 11: period_onset is 60"),
        ],
    )
    def test_calculate_prior_period(
        self, period, period_onset, expected_result, test_id
    ):
        try:
            result = calculate_prior_period(period=period, period_onset=period_onset)
            assert (
                result == expected_result
            ), f"Test {test_id} failed: Unexpected result. Result == {result}"
        except Exception as e:
            pytest.fail(
                EXCEPTION_FAIL_MESSAGE.format(
                    test_id=test_id,
                    exception_type=type(e).__name__,
                    exception_msg=str(e),
                )
            )


# Class to check if the auxiliary value is used for the predictive
class TestCheckAuxiliaryValue:
    @pytest.mark.parametrize(
        "auxiliary, total, expected_result, test_id",
        [
            (
                None,
                10,
                10,
                "Test 1: Auxiliary is None"
                # In this scenario we would expect the total to be returned
            ),
            (
                50.0,
                10,
                50.0,
                "Test 2: Auxiliary is not None"
                # In this scenario we would expect the test to return the auxiliary value
            ),
        ],
    )
    def test_check_auxiliary_value(self, auxiliary, total, expected_result, test_id):
        try:
            result = check_auxiliary_value(auxiliary=auxiliary, total=total)
            assert (
                result == expected_result
            ), f"Test {test_id} failed: Unexpected result. Result == {result}"
        except Exception as e:
            pytest.fail(
                EXCEPTION_FAIL_MESSAGE.format(
                    test_id=test_id,
                    exception_type=type(e).__name__,
                    exception_msg=str(e),
                )
            )


# Tests to check the zero error cases (see method spec for more details)
class TestCheckZeroErrors:
    @pytest.mark.parametrize(
        "test_components, predictive, precision, expected_result, test_id",
        [
            ([], 100.0, 28, "P", "Test 1: 12 RandomComponents, predictive positive"),
            (
                [
                    ComponentPair(original_value=0, final_value=None),
                    ComponentPair(original_value=0, final_value=None),
                ],
                150.0,
                28,
                "S",
                "Test 1: Components 0, predictive positive",
            ),
            (
                [
                    ComponentPair(original_value=5, final_value=None),
                    ComponentPair(original_value=32, final_value=None),
                ],
                0,
                28,
                "P",
                "Test 2: Predictive 0, predictive positive",
            ),
        ],
    )
    def test_check_zero_errors(
        self, test_components, predictive, precision, expected_result, test_id
    ):
        if "RandomComponents" in test_id:
            for _ in range(12):
                random_float = random.uniform(0, 12)
                component = ComponentPair(original_value=random_float, final_value=None)
                test_components.append(component)

        try:
            components_sum = sum_components(test_components, precision)
            marker = check_zero_errors(
                predictive=predictive, components_sum=components_sum
            )
            assert (
                marker.value == expected_result
            ), f"Test {test_id} failed: Unexpected result. Result == {marker}"
        except Exception as e:
            pytest.fail(
                EXCEPTION_FAIL_MESSAGE.format(
                    test_id=test_id,
                    exception_type=type(e).__name__,
                    exception_msg=str(e),
                )
            )


class TestCheckSumComponentsPredictive:
    @pytest.mark.parametrize(
        "test_components, predictive, precision, expected_result, test_id",
        [
            (
                [
                    ComponentPair(original_value=3.5, final_value=None),
                    ComponentPair(original_value=6.5, final_value=None),
                    ComponentPair(original_value=8.0, final_value=None),
                    ComponentPair(original_value=2.0, final_value=None),
                    ComponentPair(original_value=4.5, final_value=None),
                    ComponentPair(original_value=5.5, final_value=None),
                    ComponentPair(original_value=2.8, final_value=None),
                    ComponentPair(original_value=7.2, final_value=None),
                    ComponentPair(original_value=1.0, final_value=None),
                    ComponentPair(original_value=9.0, final_value=None),
                    ComponentPair(original_value=0.3, final_value=None),
                    ComponentPair(original_value=9.7, final_value=None),
                ],
                60.0,
                28,
                0,  # This is the returned stored absolute_difference value
                "Test 1: Component Sum Matches Predictive",
                # For this test we are summing the components values and taking the
                # absolute value of the predictive minus the sum in this test
                # we would expect zero to be the absolute difference
            ),
            (
                [
                    ComponentPair(original_value=3.2, final_value=None),
                    ComponentPair(original_value=5.1, final_value=None),
                    ComponentPair(original_value=2.4, final_value=None),
                    ComponentPair(original_value=1.5, final_value=None),
                    ComponentPair(original_value=0.8, final_value=None),
                    ComponentPair(original_value=4.6, final_value=None),
                    ComponentPair(original_value=2.7, final_value=None),
                    ComponentPair(original_value=3.9, final_value=None),
                    ComponentPair(original_value=1.2, final_value=None),
                    ComponentPair(original_value=0.5, final_value=None),
                    ComponentPair(original_value=4.3, final_value=None),
                    ComponentPair(original_value=2.0, final_value=None),
                ],
                100.0,
                28,
                67.8,  # This is the returned stored absolute_difference value
                "Test 2: Component Sum Does NOT Match Predictive and returns absolute_difference",
                # For this test we are summing the components values and taking the
                # absolute value of the predictive minus the sum in this test
                # we would expect 67.8 to be the absolute difference
            ),
        ],
    )
    def test_check_sum_components_predictive(
        self,
        test_components,
        predictive,
        precision,
        expected_result,
        test_id,
    ):
        try:
            components_sum = sum_components(test_components, precision)
            absolute_difference = check_sum_components_predictive(
                predictive, components_sum, precision
            )
            assert absolute_difference == expected_result
        except Exception as e:
            pytest.fail(
                EXCEPTION_FAIL_MESSAGE.format(
                    test_id=test_id,
                    exception_type=type(e).__name__,
                    exception_msg=str(e),
                )
            )


class TestDetermineErrorDetection:
    @pytest.mark.parametrize(
        "absolute_difference_threshold, percentage_difference_threshold, absolute_difference, predictive,"
        "low_threshold, high_threshold, expected_result, test_id",
        [
            (
                20,
                None,
                10,
                None,
                None,
                None,
                "P",
                "Test 1: Absolute Difference Only - Satisfied",
                # Test to check if ADT is satisfied and goes to the error correction
            ),
            (
                5,
                None,
                10,
                None,
                None,
                None,
                "M",
                "Test 2: Absolute Difference Only - NOT Satisfied",
                # Test to check if ADT is not satisfied meaning we would
                #  need to check the percentage difference.
            ),
            (
                None,
                10,
                None,
                15,
                10,
                20,
                "P",
                "Test 3: Percentage Difference Only - Satisfied",
                # Test to check if PDT is satisfied and goes to the error correction
            ),
            (
                None,
                10,
                None,
                15,
                16,
                20,
                "M",
                "Test 4: Percentage Difference Only - NOT Satisfied (lower)",
                # Test to check if PDT lower threshold is not satisfied
                #  this would result in an M TCC marker
            ),
            (
                None,
                10,
                None,
                15,
                10,
                13,
                "M",
                "Test 5: Percentage Difference Only - NOT Satisfied (upper)",
                # Test to check if PDT upper threshold is not satisfied
                #  this would result in an M TCC marker
            ),
            (
                20,
                10,
                10,
                15,
                16,
                20,
                "P",
                "Test 6: Both Input - Absolute Difference Satisfied",
                # Test to check if ADT is satisfied and moves onto the
                # error correction stage
            ),
            (
                5,
                10,
                10,
                15,
                10,
                20,
                "P",
                "Test 7: Both Input - Percentage Difference Satisfied",
                # Test to check if PDT is satisfied and moves onto the
                # error correction stage
            ),
            (
                5,
                10,
                10,
                15,
                16,
                20,
                "M",
                "Test 8: Both Input - Neither Satisfied",
                # Test to check if ADT and PDT thresholds are not satisfied
                #  this would result in an M TCC marker
            ),
        ],
    )
    def test_determine_error_detection(
        self,
        absolute_difference_threshold,
        percentage_difference_threshold,
        absolute_difference,
        predictive,
        low_threshold,
        high_threshold,
        expected_result,
        test_id,
    ):
        try:
            result = determine_error_detection(
                absolute_difference_threshold=absolute_difference_threshold,
                percentage_difference_threshold=percentage_difference_threshold,
                absolute_difference=absolute_difference,
                predictive=predictive,
                low_threshold=low_threshold,
                high_threshold=high_threshold,
            )

            assert result == expected_result, f"Test failed: {test_id}"
        except Exception as e:
            pytest.fail(
                EXCEPTION_FAIL_MESSAGE.format(
                    test_id=test_id,
                    exception_type=type(e).__name__,
                    exception_msg=str(e),
                )
            )


# Tests to check if ABT threshold values are returning the correct boolean
class TestCheckAbsoluteDifferenceThreshold:
    @pytest.mark.parametrize(
        "absolute_difference_threshold, absolute_difference, expected_result, test_id",
        [
            (9, 10, False, "Case 1: Absolute difference is greater than threshold"),
            (10, 10, True, "Case 2: Absolute difference equals threshold"),
            (11, 10, True, "Case 3: Absolute difference is less than threshold"),
        ],
    )
    def test_check_absolute_difference_threshold(
        self,
        absolute_difference_threshold,
        absolute_difference,
        expected_result,
        test_id,
    ):
        try:
            result = check_absolute_difference_threshold(
                absolute_difference_threshold=absolute_difference_threshold,
                absolute_difference=absolute_difference,
            )

            assert result == expected_result, f"Test failed: {test_id}"
        except Exception as e:
            pytest.fail(
                EXCEPTION_FAIL_MESSAGE.format(
                    test_id=test_id,
                    exception_type=type(e).__name__,
                    exception_msg=str(e),
                )
            )


# Tests to check if ABT threshold values are returning the correct boolean
class TestCheckPercentageDifferenceThreshold:
    @pytest.mark.parametrize(
        "predictive, low_threshold, high_threshold, expected_result, test_id",
        [
            (
                110.0,
                100.0,
                110.0,
                True,
                "Test 1: Predictive total equals upper threshold",
            ),
            (
                120.0,
                100.0,
                110.0,
                False,
                "Test 2: Predictive total is greater than upper threshold",
            ),
            (
                110.0,
                105.0,
                115.0,
                True,
                "Test 3: Predictive total is less than upper threshold and greater than lower threshold",
            ),
            (
                79.5,
                105.0,
                115.0,
                False,
                "Test 4: Predictive total is less than lower threshold",
            ),
        ],
    )
    def test_check_percentage_difference_threshold(
        self, predictive, low_threshold, high_threshold, expected_result, test_id
    ):
        try:
            result = check_percentage_difference_threshold(
                predictive, low_threshold, high_threshold
            )
            assert result == expected_result, f"{test_id} - Unexpected result"

        except Exception as e:
            pytest.fail(
                EXCEPTION_FAIL_MESSAGE.format(
                    test_id=test_id,
                    exception_type=type(e).__name__,
                    exception_msg=str(e),
                )
            )


# Test to ensure the amend total determines the correct correction path and outputs the right tcc marker
class TestErrorCorrection:
    @pytest.mark.parametrize(
        "amend_total, components_sum, original_components, predictive, precision,  expected_result, test_id",
        [
            (
                True,
                100.0,
                [ComponentPair(10.0, None)] * 10,
                100.0,
                16,
                (100.0, [10.0] * 10, "T"),
                "Test 1: Amend total",
            ),
            (
                False,
                82.0,
                [ComponentPair(8.2, None)] * 10,
                100.0,
                2,
                (100.0, [10.0] * 10, "C"),
                "Test 2: Amend components",
            ),
        ],
    )
    def test_error_correction(
        self,
        amend_total,
        components_sum,
        original_components,
        predictive,
        precision,
        expected_result,
        test_id,
    ):
        try:
            result = error_correction(
                amend_total,
                components_sum,
                original_components,
                predictive,
                precision,
            )
            assert result == expected_result, f"{test_id} - Unexpected result"

        except Exception as e:
            pytest.fail(
                EXCEPTION_FAIL_MESSAGE.format(
                    test_id=test_id,
                    exception_type=type(e).__name__,
                    exception_msg=str(e),
                )
            )


# Test to ensure the total is corrected and the expected marker is returned
class TestCorrectTotal:
    @pytest.mark.parametrize(
        "components_sum, original_components, expected_result, test_id",
        [
            (
                100.0,
                [ComponentPair(10.0, None)] * 10,
                (100.0, [ComponentPair(10.0, 10.0)] * 10, "T"),
                "Test 1: Final total is sum of received components",
            ),
            (
                30.0,
                [ComponentPair(10.0, None)] * 10,
                (30.0, [ComponentPair(10.0, 10.0)] * 10, "T"),
                "Test 2: Final total is not sum of received components",
            ),
        ],
    )
    def test_correct_total(
        self, components_sum, original_components, expected_result, test_id
    ):
        try:
            output = correct_total(
                components_sum=components_sum, original_components=original_components
            )
            print(output)
            assert (
                output == expected_result
            ), f"Test {test_id} failed: Unexpected result"
        except Exception as e:
            pytest.fail(
                EXCEPTION_FAIL_MESSAGE.format(
                    test_id=test_id,
                    exception_type=type(e).__name__,
                    exception_msg=str(e),
                )
            )


# Test to ensure the component is corrected and the expected marker is returned
class TestCorrectComponents:
    @pytest.mark.parametrize(
        "components_sum, original_components, total, precision,"
        "expected_total, expected_component, test_id",
        [
            (
                90.0,
                [ComponentPair(9.0, None)] * 10,
                100.0,
                18,
                100.0,
                [10.0] * 10,
                "Test 1: Component = 90, " "predictive = 100",
            ),
            (
                130.0,
                [
                    ComponentPair(75.0, None),
                    ComponentPair(25.0, None),
                    ComponentPair(30.0, None),
                ],
                200.0,
                18,
                200.0,
                [115.38, 38.46, 46.15],
                "Test 2: Component sum = 130, Total = 200",
            ),
            (
                100.0,
                [ComponentPair(10.0, None)] * 10,
                0,
                1,
                0,
                [0.0] * 10,
                "Test 3: Component = 100, " "predictive = 0",
            ),
        ],
    )
    def test_correct_components(
        self,
        components_sum,
        original_components,
        total,
        precision,
        expected_total,
        expected_component,
        test_id,
    ):
        try:
            result = correct_components(
                components_sum=components_sum,
                original_components=original_components,
                total=total,
                precision=precision,
            )

            assert (
                result[0] == expected_total
            ), f"Test {test_id} failed: Unexpected result"
            for index, component in enumerate(result[1]):
                # Rounding to 2 decimal places for testing purposes
                value = round(component.final_value, 2)
                assert (
                    value == expected_component[index]
                ), f"Test {test_id} failed: Unexpected result"
        except Exception as e:
            pytest.fail(
                EXCEPTION_FAIL_MESSAGE.format(
                    test_id=test_id,
                    exception_type=type(e).__name__,
                    exception_msg=str(e),
                )
            )


class TestTotalsAndComponents:
    @pytest.mark.parametrize(
        "identifier, period, total, components, amend_total, predictive, precision, predictive_period,"
        "period_onset, auxiliary, absolute_difference_threshold, percentage_difference_threshold,"
        "expected_result, test_id",
        [
            (
                "A",
                "202302",
                1625,
                [
                    (632),
                    (732),
                    (99),
                    (162),
                ],
                True,
                1625,
                28,
                "202301",
                1,
                None,
                11,
                None,
                (
                    "A",
                    "202302",
                    0,
                    None,
                    None,
                    28,
                    1625,
                    [632, 732, 99, 162],
                    "N",
                ),
                "Test 1 - Totals matches components TCC Marker N",
                # This test checks if the predictive = sum of components
                # this is not the case so the tcc marker N is returned
            ),
            (
                "B",
                "202205",
                10817,
                [
                    (9201),
                    (866),
                    (632),
                    (112),
                ],
                True,
                10817,
                28,
                "202201",
                4,
                None,
                11,
                None,
                (
                    "B",
                    "202205",
                    6,
                    None,
                    None,
                    28,
                    10811,
                    [9201, 866, 632, 112],
                    "T",
                ),
                "Test 2 - Totals corrected with non zero component values TCC Marker T",
                # This test checks if the total is corrected
                # by using a true amend value
            ),
            (
                "C",
                "201601",
                90,
                [
                    (90),
                    (0),
                    (4),
                    (6),
                ],
                False,
                90,
                2,
                "201512",
                1,
                None,
                None,
                0.1,
                (
                    "C",
                    "201601",
                    10,
                    90,
                    110,
                    2,
                    90,
                    [81, 0, 3.6, 5.4],
                    "C",
                ),
                "Test 3 - Components corrected - TCC Marker C",
                # This test checks if the component is
                # corrected by using a true amend value
            ),
            (
                "D",
                "201307",
                1964,
                [
                    (632),
                    (732),
                    (99),
                    (162),
                ],
                True,
                1964,
                28,
                "201306",
                1,
                None,
                1,
                0.1,
                (
                    "D",
                    "201307",
                    339,
                    1462.5,
                    1787.5,
                    28,
                    1964,
                    [632, 732, 99, 162],
                    "M",
                ),
                "Test 4 - Manual correction required TCC Marker M ",
                # This test that if the predictive is not within the threshold limits
                # then we get M tcc marker
            ),
            (
                "F",
                "201606",
                11,
                [
                    (0),
                    (0),
                    (0),
                    (0),
                ],
                True,
                None,
                1,
                "201601",
                5,
                None,
                11,
                None,
                (
                    "F",
                    "201606",
                    None,
                    None,
                    None,
                    1,
                    11,
                    [0, 0, 0, 0],
                    "S",
                ),
                "Test 5 - Predictive variable is None",
                # If the predictive is passed as a None value by the use the auxiliary or total
                # this depends on the prior calculate_prior_period
                # In this case auxiliary is also None
                # the prior period is equal to the predictive so we have S tcc marker
            ),
            (
                "H",
                "202101",
                1625,
                [
                    ("InvalidString"),
                    (732),
                    (99),
                    (162),
                ],
                True,
                1625,
                1,
                "202012",
                1,
                None,
                11,
                0.1,
                TACException("component=InvalidString is missing or not a number"),
                "Test 6 - Invalid component value entered by user",
                # An invalid component is passed to the method which is not allowed
                # hence we will throw an error
            ),
            (
                "I",
                "201603",
                1625,
                [
                    (632),
                    (732),
                    (99),
                    (162),
                ],
                True,
                "InvalidString",
                1,
                "201603",
                0,
                None,
                11,
                0.1,
                TACException("predictive must not be a string"),
                # An invalid predictive is passed to the method which is not allowed
                # hence we will throw an error
                "Test 7 - Invalid predictive value entered by user",
            ),
            (
                "J",
                "201505",
                1625,
                [
                    (632),
                    (732),
                    (99),
                    (162),
                ],
                True,
                1625,
                1,
                "201505",
                0,
                "InvalidString",
                11,
                0.1,
                TACException("auxiliary is missing or not a number"),
                # An invalid auxiliary is passed to the method which is not allowed
                # hence we will throw an error
                "Test 8 - Invalid auxiliary value entered by user",
            ),
            (
                "K",
                "201203",
                1625,
                [
                    (632),
                    (732),
                    (99),
                    (162),
                ],
                True,
                1625,
                1,
                "201203",
                0,
                None,
                None,
                None,
                TACException(
                    "One or both of absolute/percentage difference thresholds must be specified and non-zero"
                ),
                # An invalid ADT or PDT is passed to the method which is not allowed
                # hence we will throw an error
                "Test 9 - Absolute and percentage difference threshold None value entered by user",
            ),
            (
                "L",
                "201104",
                10817,
                [
                    (9201),
                    (866),
                    (632),
                    (112),
                ],
                True,
                None,
                28,
                "201103",
                1,
                10817,
                11,
                None,
                (
                    "L",
                    "201104",
                    6,
                    None,
                    None,
                    28,
                    10811,
                    [9201, 866, 632, 112],
                    "T",
                ),
                "Test 10 - Auxiliary variable replaces the missing predictive variable",
                # If the predictive is None we trigger the check_auxiliary_value function
                # this will replace the predictive with the auxiliary
                #  as the auxiliary is not none
            ),
            (
                "M",
                "201009",
                0,
                [
                    (0),
                    (0),
                    (0),
                    (0),
                ],
                True,
                0,
                28,
                "201008",
                1,
                None,
                11,
                None,
                (
                    "M",
                    "201009",
                    0,
                    None,
                    None,
                    28,
                    0,
                    [0, 0, 0, 0],
                    "N",
                ),
                "Test 11 - Predictive value is 0 and component sum is zero",
                # Special case where if both are zero we return N tcc marker
            ),
            (
                "N",
                "201908",
                10817,
                [
                    (9201),
                    (866),
                    (632),
                    (112),
                ],
                True,
                10817,
                28,
                "201907",
                0,
                None,
                11,
                None,
                (
                    "N",
                    "201908",
                    6,
                    None,
                    None,
                    28,
                    10811,
                    [9201, 866, 632, 112],
                    "T",
                ),
                "Test 12 - Absolute Difference Threshold only specified and satisfied",
                # Test checking ADT passes to totals correction and corrects the total
            ),
            (
                "O",
                "200702",
                5,
                [(1), (2), (3), (4)],
                True,
                5,
                1,
                "200701",
                1,
                None,
                4,
                None,
                (
                    "O",
                    "200702",
                    5,
                    None,
                    None,
                    1,
                    5,
                    [1, 2, 3, 4],
                    "M",
                ),
                "Test 13 - Absolute Difference Threshold only specified and not satisfied",
                # Test checking ADT fails to totals correction and returns M tcc marker
            ),
            (
                "P",
                "200606",
                9,
                [(1), (2), (3), (4)],
                True,
                9,
                28,
                "200606",
                1,
                None,
                None,
                0.1,
                (
                    "P",
                    "200606",
                    1,
                    9,
                    11,
                    28,
                    10,
                    [1, 2, 3, 4],
                    "T",
                ),
                "Test 14 - Percentage Difference Threshold only specified and satisfied",
                # Test checking PDT passes to component correction and corrects the components
            ),
            (
                "Q",
                "200502",
                5,
                [(1), (2), (3), (4)],
                True,
                5,
                28,
                "200501",
                1,
                None,
                None,
                0.1,
                (
                    "Q",
                    "200502",
                    5,
                    9,
                    11,
                    28,
                    5,
                    [1, 2, 3, 4],
                    "M",
                ),
                "Test 15 - Percentage Difference Threshold only specified and not satisfied",
                # Test checking PDT returns M marker
            ),
            (
                "R",
                "200403",
                10817,
                [
                    (9201),
                    (866),
                    (632),
                    (112),
                ],
                True,
                10817,
                28,
                "200402",
                1,
                None,
                11,
                0.1,
                (
                    "R",
                    "200403",
                    6,
                    9729.9,
                    11892.1,
                    28,
                    10811,
                    [9201, 866, 632, 112],
                    "T",
                ),
                "Test 16 - ADT and PDT specified and ADT satisfied",
                # Check that the T marker is returned when a happy path is provided
            ),
            (
                "S",
                "200102",
                9,
                [(1), (2), (3), (4)],
                False,
                9,
                2,
                "200101",
                1,
                None,
                4,
                0.1,
                (
                    "S",
                    "200102",
                    1,
                    9,
                    11,
                    2,
                    9,
                    [0.9, 1.8, 2.7, 3.6],
                    "C",
                ),
                "Test 17 - ADT and PDT specified and ADT not satisfied and PDT satisfied",
                # Test to check that PDT can still complete a component correction
            ),
            (
                "U",
                "200003",
                5,
                [(1), (2), (3), (4)],
                False,
                5,
                1,
                "200002",
                1,
                None,
                0,
                0,
                TACException(
                    "One or both of absolute/percentage difference thresholds must be specified and non-zero"
                ),
                "Test 18 - Absolute and Percentage Difference Thresholds set to zero",
                # Test checking for a error exception thrown when we provide
                # zero values for ADT and PDT this is caught in validate input
            ),
            (
                "T",
                "200108",
                5,
                [
                    (0),
                    (0),
                    (0),
                    (0),
                ],
                True,
                5,
                1,
                "200107",
                1,
                None,
                None,
                None,
                TACException(
                    "One or both of absolute/percentage difference thresholds must be specified and non-zero"
                ),
                "Test 19 - Absolute and Percentage Difference Thresholds not specified",
                # Test checking for a error exception thrown when we provide
                # zero values for ADT or PDT this is caught in validate input
            ),
            (
                "U",
                "200704",
                10817,
                [
                    (0),
                    (0),
                    (0),
                    (0),
                ],
                True,
                10817,
                1,
                "200703",
                1,
                None,
                11,
                None,
                (
                    "U",
                    "200704",
                    None,
                    None,
                    None,
                    1,
                    10817,
                    [0, 0, 0, 0],
                    "S",
                ),
                "Test 20 - Zero Case 1",
                # If target total > 0 and
                # components sum = 0 and amend total = TRUE:
                # No correction should be applied in this case.
                # A total only may be provided if the component
                # breakdown is unknown so would not want to remove true values.
            ),
            (
                "V",
                "200109",
                10817,
                [(0), (0), (0), (0)],
                False,
                10817,
                1,
                "200108",
                1,
                None,
                11,
                None,
                (
                    "V",
                    "200109",
                    None,
                    None,
                    None,
                    1,
                    10817,
                    [0, 0, 0, 0],
                    "S",
                ),
                "Test 21 - Zero Case 2",
                # If target total > 0 and components sum = 0 and
                # amend total = FALSE: In this case, the proportions
                # of the true components are unknown so the method
                # cannot apply a correction.
            ),
            (
                "W",
                "201803",
                0,
                [
                    (9201),
                    (866),
                    (632),
                    (112),
                ],
                True,
                0,
                28,
                "201802",
                1,
                None,
                11,
                None,
                (
                    "W",
                    "201803",
                    10811,
                    None,
                    None,
                    28,
                    0,
                    [9201, 866, 632, 112],
                    "M",
                ),
                "Test 22 - Zero Case 3",
                # If target total = 0 and components sum > 0
                # and amend total = TRUE: The total should be
                # corrected if the difference observed is
                # within the tolerances determined by the
                # detection method. Else, the difference
                # should be flagged for manual checking.
            ),
            (
                "X",
                "200201",
                0,
                [(10), (10), (10), (10)],
                False,
                0,
                1,
                "200112",
                1,
                None,
                45,
                None,
                (
                    "X",
                    "200201",
                    40,
                    None,
                    None,
                    1,
                    0,
                    [0, 0, 0, 0],
                    "C",
                ),
                "Test 23 - Zero Case 4 (where difference is within thresholds",
                # If target total = 0 and components > 0 and amend total = FALSE.
                # Apply correction to override the components with zeros if the
                # difference observed is within the tolerances determined by the
                # detection method. Else, the difference should be flagged for
                # manual checking.
            ),
            (
                "Y",
                "200201",
                0,
                [
                    (1),
                    (2),
                    (3),
                    (4),
                ],
                False,
                0,
                28,
                "200112",
                1,
                None,
                None,
                0.1,
                (
                    "Y",
                    "200201",
                    10,
                    9,
                    11,
                    28,
                    0,
                    [1, 2, 3, 4],
                    "M",
                ),
                "Test 24 - Zero Case 4 (where difference are not within the threshold)",
                # If target total = 0 and components > 0 and amend total = FALSE.
                # Apply correction to override the components with zeros if the
                # difference observed is within the tolerances determined by the
                # detection method. Else, the difference should be flagged for
                # manual checking.
            ),
            (
                "Z",
                "200402",
                3,
                [
                    (2.4),
                    (2.6),
                    (2.8),
                    (3.1),
                ],
                True,
                3,
                28,
                "200401",
                1,
                None,
                11,
                None,
                (
                    "Z",
                    "200402",
                    7.9,
                    None,
                    None,
                    28,
                    10.9,
                    [2.4, 2.6, 2.8, 3.1],
                    "T",
                ),
                "Test 25 - Amend Total True floating point components and floating point total",
                # Test to check if the floating point
                # components sum to equal a floating total value
                # when amend total is true.
            ),
            (
                "AA",
                "200911",
                2,
                [
                    (2.4),
                    (2.6),
                    (2.8),
                    (3.1),
                ],
                False,
                2,
                28,
                "200910",
                1,
                None,
                16,
                None,
                (
                    "AA",
                    "200911",
                    8.9,
                    None,
                    None,
                    28,
                    2,
                    [
                        0.44036697247706424,
                        0.47706422018348627,
                        0.5137614678899083,
                        0.5688073394495413,
                    ],
                    "C",
                ),
                "Test 26 - Amend Total False floating point components and floating point total",
                # Test to check if the floating point
                # components sum to equal a floating total value
                # when amend total is false.
            ),
            (
                "AB",
                "202103",
                7,
                [(1), (2), (3), (4)],
                True,
                7,
                28,
                "202102",
                1,
                None,
                None,
                0.1,
                (
                    "AB",
                    "202103",
                    3,
                    9,
                    11,
                    28,
                    7,
                    [1, 2, 3, 4],
                    "M",
                ),
                "Test 27 - predictive is less than lower threshold",
                # Test to check the margins for the thresholds of the lower limit
            ),
            (
                "AC",
                "200406",
                10.5,
                [(1), (2), (3), (4)],
                True,
                10.5,
                28,
                "200405",
                1,
                None,
                None,
                0.1,
                (
                    "AC",
                    "200406",
                    0.5,
                    9,
                    11,
                    28,
                    10,
                    [1, 2, 3, 4],
                    "T",
                ),
                "Test 28 - predictive is greater than lower threshold",
                # Test to check the margins for the thresholds of the lower limit
            ),
            (
                "AD",
                "200908",
                9,
                [(1), (2), (3), (4)],
                False,
                9,
                2,
                "200907",
                1,
                None,
                None,
                0.1,
                (
                    "AD",
                    "200908",
                    1,
                    9,
                    11,
                    2,
                    9,
                    [0.9, 1.8, 2.7, 3.6],
                    "T",
                ),
                "Test 29 - predictive is equal to lower threshold and amend value is false",
                # Test to check the margins for the thresholds of the lower limit
            ),
            (
                "AE",
                "201903",
                10.9,
                [(1), (2), (3), (4)],
                True,
                10.9,
                28,
                "201902",
                1,
                None,
                None,
                0.1,
                (
                    "AE",
                    "201903",
                    0.9,
                    9,
                    11,
                    28,
                    10.0,
                    [1, 2, 3, 4],
                    "T",
                ),
                "Test 30 - predictive is less than upper threshold",
                # Test to check the margins for the thresholds of the upper limit
            ),
            (
                "AF",
                "201706",
                11,
                [(1), (2), (3), (4)],
                False,
                11,
                2,
                "201705",
                1,
                None,
                None,
                0.1,
                (
                    "AF",
                    "201706",
                    1,
                    9,
                    11,
                    2,
                    11,
                    [1.1, 2.2, 3.3, 4.4],
                    "T",
                ),
                "Test 31 - predictive is equal to than upper threshold",
                # Test to check the margins for the thresholds of the upper limit
            ),
            (
                "AG",
                "200406",
                12,
                [(1), (2), (3), (4)],
                True,
                12,
                28,
                "200405",
                1,
                None,
                None,
                0.1,
                (
                    "AG",
                    "200406",
                    2.0,
                    9,
                    11,
                    28,
                    12,
                    [1, 2, 3, 4],
                    "M",
                ),
                "Test 32 - predictive is greater than upper threshold",
                # Test to check the margins for the thresholds of the upper limit
            ),
            (
                "AH",
                "200103",
                "InvalidString",
                [
                    (0),
                    (0),
                    (0),
                    (0),
                ],
                True,
                11,
                1,
                "200103",
                None,
                0,
                11,
                None,
                TACException("total is missing or not a number"),
                "Test 33 - Invalid total value entered by user",
                # Test to ensure a TACException is thrown when a
                # user enters a None value for the total
            ),
            (
                None,
                "204602",
                10.9,
                [
                    (1),
                    (2),
                    (3),
                    (4),
                ],
                True,
                10.9,
                28,
                "204602",
                0,
                None,
                None,
                0.1,
                TACException("The identifier is not populated"),
                "Test 34 - Missing identifier value",
                # Test to ensure a TACException is thrown when a
                # user enters a None value for the identifier
            ),
            (
                "AI",
                "",
                10.9,
                [
                    (1),
                    (2),
                    (3),
                    (4),
                ],
                True,
                10.9,
                28,
                "200803",
                0,
                None,
                None,
                0.1,
                ValueError("time data '' does not match format '%Y%m'"),
                "Test 35 - Missing period value",
                # Test to ensure a TACException is thrown when a
                # user does not enter a value for the period
            ),
            (
                "AJ",
                "200907",
                10.9,
                [
                    (1),
                    (2),
                    (3),
                    (4),
                ],
                None,
                10.9,
                1,
                "200907",
                1,
                None,
                11,
                0.1,
                TACException("Amend total needs to be True or False"),
                "Test 36 - Missing Amend total",
                # Test to ensure a TACException is thrown when a
                # user does not enter a value for the amend value
            ),
            (
                "AP",
                "200103",
                90,
                [
                    (90),
                    (0),
                    (4),
                    (6),
                ],
                False,
                90,
                28,
                "200102",
                1,
                None,
                None,
                0.1,
                (
                    "AP",
                    "200103",
                    10,
                    90,
                    110,
                    28,
                    90,
                    [81, 0, 3.6, 5.4],
                    "C",
                ),
                "Test 42 - Testing precision value = 1",
                # Testing the accuracy of the components returned
                # when the entered precision value is equal to 1
            ),
            (
                "AQ",
                "200203",
                10,
                [
                    (2.4),
                    (2.6),
                    (2.8),
                    (3.1),
                ],
                False,
                10,
                28,
                "200202",
                1,
                None,
                None,
                0.1,
                (
                    "AQ",
                    "200203",
                    0.9,
                    9.81,
                    11.99,
                    28,
                    10,
                    [
                        2.2018348623853212,
                        2.385321100917431,
                        2.5688073394495414,
                        2.8440366972477062,
                    ],
                    "C",
                ),
                "Test 43 - Testing precision value = 28",
                # Testing the accuracy of the components returned
                # when the entered precision value is equal to 28
            ),
            (
                "AR",
                "200405",
                2,
                [
                    (2.4),
                    (2.6),
                    (2.8),
                    (3.1),
                ],
                False,
                2,
                29,
                "200405",
                1,
                None,
                11,
                None,
                TACException(
                    "Precision range must be more than 0 and less than or equal to 28"
                ),
                "Test 44 - Testing precision value = 29",
                # Testing the accuracy of the components returned
                # when the entered precision value is equal to 29
            ),
            (
                "AS",
                "199502",
                2,
                [
                    (2.4),
                    (2.6),
                    (2.8),
                    (3.1),
                ],
                False,
                2,
                0,
                "199502",
                1,
                None,
                11,
                None,
                TACException(
                    "Precision range must be more than 0 and less than or equal to 28"
                ),
                "Test 45 - Testing precision value = 0",
                # Testing the accuracy of the components returned
                # when the entered precision value is equal to 0
            ),
            (
                "AT",
                "199706",
                11,
                [(1), (2), (3), (4)],
                False,
                11,
                2,
                "199705",
                1,
                None,
                None,
                0.1,
                (
                    "AT",
                    "199706",
                    1,
                    9,
                    11,
                    2,
                    11,
                    [1.1, 2.2, 3.3, 4.4],
                    "T",
                ),
                "Test 46 - Testing precision value = 2 with floating components sum to a floating total",
                # Testing the accuracy of the components returned
                # when the entered precision value is equal to 2
                # This test also checks floating components sum to a
                # floating total
            ),
            (
                "AU",
                "199809",
                0.6,
                [
                    (0.1),
                    (0.2),
                    (0.4),
                ],
                True,
                0.6,
                1,
                "199808",
                1,
                None,
                None,
                0.1,
                (
                    "AU",
                    "199809",
                    0.1,
                    0.6,
                    0.8,
                    1,
                    0.7,
                    [0.1, 0.2, 0.4],
                    "T",
                ),
                "Test 47 - Testing precision value = 1 with floating components sum to a floating total",
                # Testing the accuracy of the components returned
                # when the entered precision value is equal to 1
                # This test also checks floating components sum to a
                # floating total
            ),
            (
                "AW",
                "199502",
                10.5,
                [
                    (1),
                    (2),
                    (3),
                    (4),
                ],
                True,
                10.5,
                None,
                "199501",
                1,
                None,
                None,
                0.1,
                (
                    "AW",
                    "199502",
                    0.5,
                    9,
                    11,
                    28,
                    10,
                    [1, 2, 3, 4],
                    "T",
                ),
                "Test 48 - Missing precision value (defaults to 28)",
                # Testing the accuracy of the components returned
                # when the precision value is missing and so defaults to 28
            ),
            (
                "AX",
                "202001",
                90,
                [
                    (90),
                    (0),
                    (4),
                    (6),
                ],
                False,
                95,
                28,
                "201901",
                3,
                None,
                None,
                0.1,
                (
                    "AX",
                    "202001",
                    10,
                    90,
                    110,
                    28,
                    90,
                    [81, 0, 3.6, 5.4],
                    "C",
                ),
                "Test 49 - Predictive total and predictive period are different to period and total",
                # This test is to check the set_predictive_value() function
                # The period_onset is 3
                # The prior period would be calculated out to three months before the period
                # which does not match the predictive calculate_prior_period
                # Hence the check_auxiliary_value function is called and the predictive value
                # is replaced with the total value because the auxiliary is none
            ),
            (
                "AY",
                "201809",
                90,
                [
                    (90),
                    (0),
                    (4),
                    (6),
                ],
                False,
                None,
                28,
                "201709",
                14,
                95,
                None,
                0.1,
                (
                    "AY",
                    "201809",
                    5,
                    90,
                    110,
                    28,
                    90,
                    [81, 0, 3.6, 5.4],
                    "C",
                ),
                "Test 50 - Use auxiliary when predictive is not specified",
                # This test is to check the set_predictive_value() function
                # The predictive value is none
                # Hence the check_auxiliary_value function is called and the predictive value
                # is replaced with the auxiliary value
            ),
            (
                "AZ",
                "200304",
                90,
                [
                    (90),
                    (0),
                    (4),
                    (6),
                ],
                False,
                None,
                28,
                "200204",
                3,
                95,
                None,
                0.1,
                (
                    "AZ",
                    "200304",
                    5,
                    90,
                    110,
                    28,
                    90,
                    [81, 0, 3.6, 5.4],
                    "C",
                ),
                "Test 51 - Use auxiliary when predictive is none and predictive period is not the prior period",
                # This test is to check the set_predictive_value() function
                # The predictive value is none
                # The period_onset is 3
                # The prior period would be calculated out to three months before the period
                # which does not match the predictive calculate_prior_period
                # Hence the check_auxiliary_value function is called and the predictive value
                # is replaced with the auxiliary
            ),
            (
                "BA",
                "202501",
                90,
                [
                    (90),
                    (0),
                    (4),
                    (6),
                ],
                False,
                None,
                28,
                "202401",
                6,
                None,
                None,
                0.1,
                (
                    "BA",
                    "202501",
                    10,
                    90,
                    110,
                    28,
                    90,
                    [81, 0, 3.6, 5.4],
                    "C",
                ),
                "Test 52 - Use total when predictive and auxiliary is none",
                # This test is to check the set_predictive_value() function
                # The period_onset is 6
                # The prior period would be calculated out to 6 months before the period
                # The predictive value is none
                # which does not match the predictive calculate_prior_period
                # Hence the check_auxiliary_value function is called and the predictive value
                # is replaced with the total value because the auxiliary is none
            ),
            (
                "BB",
                "202201",
                10000,
                [
                    (9201),
                    (866),
                    (632),
                    (112),
                ],
                True,
                10817,
                28,
                "202201",
                13,
                None,
                11,
                0.1,
                (
                    "BB",
                    "202201",
                    811,
                    9729.9,
                    11892.1,
                    28,
                    10811,
                    [9201, 866, 632, 112],
                    "T",
                ),
                "Test 53 - Predictive total and prior period are different",
                # This test is to check the set_predictive_value() function
                # The predictive exists but the predictive period
                #  does not equal the prior
                # Hence the function is applied and we use the total value as the predictive
            ),
            (
                "BC",
                "200405",
                10817,
                [
                    (9201),
                    (866),
                    (632),
                    (112),
                ],
                True,
                10,
                28,
                "200212",
                10,
                10817,
                11,
                0.1,
                (
                    "BC",
                    "200405",
                    6,
                    9729.9,
                    11892.1,
                    28,
                    10811,
                    [9201, 866, 632, 112],
                    "T",
                ),
                "Test 54 - Auxiliary is new predictive when predictive total and prior period are different",
                # This test is to check the set_predictive_value() function
                # The period_onset is 10
                # The prior period would be calculated out to 10 months before the period
                # The predictive value is not none
                # which does not match the predictive calculate_prior_period
                # Hence the check_auxiliary_value function is called and the predictive value
                # is replaced with the auxiliary value
            ),
            (
                "BD",
                "201409",
                10817,
                [
                    (9201),
                    (866),
                    (632),
                    (112),
                ],
                True,
                60,
                28,
                "201402",
                3,
                10817,
                11,
                0.1,
                (
                    "BD",
                    "201409",
                    6,
                    9729.9,
                    11892.1,
                    28,
                    10811,
                    [9201, 866, 632, 112],
                    "T",
                ),
                "Test 55 - Use auxiliary when predictive is none and predictive period != the prior period",
                # This test is to check the set_predictive_value() function
                # The period_onset is 3
                # The prior period would be calculated out to 3 months before the period
                # The predictive value is none
                # which does not match the predictive calculate_prior_period
                # Hence the check_auxiliary_value function is called and the predictive value
                # is replaced with the auxiliary value
            ),
            (
                "BE",
                "201807",
                10817,
                [
                    (9201),
                    (866),
                    (632),
                    (112),
                ],
                True,
                60,
                28,
                "201805",
                2,
                None,
                11,
                0.1,
                (
                    "BE",
                    "201807",
                    10751.0,
                    9729.9,
                    11892.1,
                    28,
                    10817,
                    [9201, 866, 632, 112],
                    "T",
                ),
                "Test 56 - Predictive and prior periods match and total is new predictive",
                # This test is to check the set_predictive_value() function
                # The predictive is None and the period_onset is 2
                # The prior period matches the predictive period
                # we apply the check_auxiliary_value() function
                # and the predictive does not change
            ),
            (
                "BF",
                "201701",
                90,
                [
                    (90),
                    (0),
                    (4),
                    (6),
                ],
                False,
                95,
                28,
                "201612",
                1,
                None,
                None,
                0.1,
                (
                    "BF",
                    "201701",
                    5,
                    90,
                    110,
                    28,
                    90,
                    [81, 0, 3.6, 5.4],
                    "C",
                ),
                "Test 57 - Predictive exists and period_onset = 1, expect periods to match",
                # This test is to check the set_predictive_value() function
                # The period_onset is 1
                # The prior period would be calculated out to 1 months before the period
                # The predictive period matches the predictive calculate_prior_period
                # Hence the predictive is not changed
            ),
            (
                "BG",
                "201503",
                90,
                [
                    (90),
                    (0),
                    (4),
                    (6),
                ],
                False,
                95,
                28,
                "201501",
                2,
                None,
                None,
                0.1,
                (
                    "BG",
                    "201503",
                    5,
                    90,
                    110,
                    28,
                    90,
                    [81, 0, 3.6, 5.4],
                    "C",
                ),
                "Test 58 - Predictive exists and period_onset = 2, expect periods to match",
                # This test is to check the set_predictive_value() function
                # The period_onset is 2
                # The prior period would be calculated out to 2 months before the period
                # The predictive value is not none
                # which does match the predictive calculate_prior_period
                # Hence the check_auxiliary_value function is not called and the predictive value
                # not changed
            ),
            (
                "BH",
                "201604",
                90,
                [
                    (90),
                    (0),
                    (4),
                    (6),
                ],
                False,
                95,
                28,
                "201601",
                3,
                None,
                None,
                0.1,
                (
                    "BH",
                    "201604",
                    5,
                    90,
                    110,
                    28,
                    90,
                    [81, 0, 3.6, 5.4],
                    "C",
                ),
                "Test 59 - Predictive exists and period_onset = 3, expect periods to match",
                # This test is to check the set_predictive_value() function
                # The period_onset is 3
                # The prior period would be calculated out to 3 months before the period
                # The predictive value is not none
                # which does match the predictive calculate_prior_period
                # Hence the check_auxiliary_value function is not called and the predictive value
                # not changed
            ),
            (
                "BI",
                "201403",
                90,
                [
                    (90),
                    (0),
                    (4),
                    (6),
                ],
                False,
                95,
                28,
                "201311",
                4,
                None,
                None,
                0.1,
                (
                    "BI",
                    "201403",
                    5,
                    90,
                    110,
                    28,
                    90,
                    [81, 0, 3.6, 5.4],
                    "C",
                ),
                "Test 60 - Predictive exists and period_onset = 4, expect periods to match",
                # This test is to check the set_predictive_value() function
                # The period_onset is 4
                # The prior period would be calculated out to 4 months before the period
                # The predictive value is not none
                # which does match the predictive calculate_prior_period
                # Hence the check_auxiliary_value function is not called and the predictive value
                # not changed
            ),
            (
                "BJ",
                "201207",
                90,
                [
                    (90),
                    (0),
                    (4),
                    (6),
                ],
                False,
                95,
                28,
                "201201",
                6,
                None,
                None,
                0.1,
                (
                    "BJ",
                    "201207",
                    5,
                    90,
                    110,
                    28,
                    90,
                    [81, 0, 3.6, 5.4],
                    "C",
                ),
                "Test 61 - Predictive exists and period_onset = 6, expect periods to match",
                # This test is to check the set_predictive_value() function
                # The period_onset is 6
                # The prior period would be calculated out to 6 months before the period
                # The predictive value is not none
                # which does match the predictive calculate_prior_period
                # Hence the check_auxiliary_value function is not called and the predictive value
                # not changed
            ),
            (
                "BK",
                "200201",
                90,
                [
                    (90),
                    (0),
                    (4),
                    (6),
                ],
                False,
                95,
                28,
                "200101",
                12,
                None,
                None,
                0.1,
                (
                    "BK",
                    "200201",
                    5,
                    90,
                    110,
                    28,
                    90,
                    [81, 0, 3.6, 5.4],
                    "C",
                ),
                "Test 62 - Predictive exists and period_onset = 12, expect periods to match",
                # This test is to check the set_predictive_value() function
                # The period_onset is 12
                # The prior period would be calculated out to 12 months before the period
                # The predictive value is not none
                # which does match the predictive calculate_prior_period
                # Hence the check_auxiliary_value function is not called and the predictive value
                # not changed
            ),
            (
                "BL",
                "202206",
                90,
                [
                    (90),
                    (0),
                    (4),
                    (6),
                ],
                False,
                95,
                28,
                "202012",
                18,
                None,
                None,
                0.1,
                (
                    "BL",
                    "202206",
                    5,
                    90,
                    110,
                    28,
                    90,
                    [81, 0, 3.6, 5.4],
                    "C",
                ),
                "Test 63 - Predictive exists and period_onset = 18, expect periods to match",
                # This test is to check the set_predictive_value() function
                # The period_onset is 18
                # The prior period would be calculated out to 18 months before the period
                # The predictive value is not none
                # which does match the predictive calculate_prior_period
                # Hence the check_auxiliary_value function is not called and the predictive value
                # not changed
            ),
            (
                "BM",
                "201903",
                90,
                [
                    (90),
                    (0),
                    (4),
                    (6),
                ],
                False,
                95,
                28,
                "201703",
                24,
                None,
                None,
                0.1,
                (
                    "BM",
                    "201903",
                    5,
                    90,
                    110,
                    28,
                    90,
                    [81, 0, 3.6, 5.4],
                    "C",
                ),
                "Test 64 - Predictive exists and period_onset = 24, expect periods to match",
                # This test is to check the set_predictive_value() function
                # The period_onset is 24
                # The prior period would be calculated out to 24 months before the period
                # The predictive value is not none
                # which does match the predictive calculate_prior_period
                # Hence the check_auxiliary_value function is not called and the predictive value
                # not changed
            ),
            (
                "BN",
                "202102",
                90,
                [
                    (90),
                    (0),
                    (4),
                    (6),
                ],
                False,
                95,
                28,
                "201802",
                36,
                None,
                None,
                0.1,
                (
                    "BN",
                    "202102",
                    5,
                    90,
                    110,
                    28,
                    90,
                    [81, 0, 3.6, 5.4],
                    "C",
                ),
                "Test 65 - Predictive exists and period_onset = 36, expect periods to match",
                # This test is to check the set_predictive_value() function
                # The period_onset is 36
                # The prior period would be calculated out to 36 months before the period
                # The predictive value is not none
                # which does match the predictive calculate_prior_period
                # Hence the check_auxiliary_value function is not called and the predictive value
                # not changed
            ),
            (
                "BO",
                "200908",
                90,
                [
                    (90),
                    (0),
                    (4),
                    (6),
                ],
                False,
                95,
                28,
                "200508",
                48,
                None,
                None,
                0.1,
                (
                    "BO",
                    "200908",
                    5,
                    90,
                    110,
                    28,
                    90,
                    [81, 0, 3.6, 5.4],
                    "C",
                ),
                "Test 66 - Predictive exists and period_onset = 48, expect periods to match",
                # This test is to check the set_predictive_value() function
                # The period_onset is 48
                # The prior period would be calculated out to 48 months before the period
                # The predictive value is not none
                # which does match the predictive calculate_prior_period
                # Hence the check_auxiliary_value function is not called and the predictive value
                # not changed
            ),
            (
                "BP",
                "201304",
                90,
                [
                    (90),
                    (0),
                    (4),
                    (6),
                ],
                False,
                95,
                28,
                "200804",
                60,
                None,
                None,
                0.1,
                (
                    "BP",
                    "201304",
                    5,
                    90,
                    110,
                    28,
                    90,
                    [81, 0, 3.6, 5.4],
                    "C",
                ),
                "Test 67 - Predictive exists and period_onset = 60, expect periods to match",
                # This test is to check the set_predictive_value() function
                # The period_onset is 60
                # The prior period would be calculated out to 60 months before the period
                # The predictive value is not none
                # which does match the predictive calculate_prior_period
                # Hence the check_auxiliary_value function is not called and the predictive value
                # not changed
            ),
            (
                "BQ",
                "201607",
                90,
                [
                    (90),
                    (0),
                    (4),
                    (6),
                ],
                False,
                None,
                28,
                None,
                60,
                None,
                None,
                0.1,
                (
                    "BQ",
                    "201607",
                    10,
                    90,
                    110,
                    28,
                    90,
                    [81, 0, 3.6, 5.4],
                    "C",
                ),
                "Test 68 - Predictive period is None so auxiliary value is used.",
                # This test is to check the set_predictive_value() function
                # The period_onset is 60
                # The prior period would be calculated out to 60 months before the period
                # The predictive value is not none
                # which does match the predictive calculate_prior_period
                # Hence the check_auxiliary_value function is called and the predictive value
                # is replaced by the auxiliary value
            ),
        ],
    )
    def test_totals_and_components(
        self,
        capfd,
        identifier,
        period,
        total,
        components,
        amend_total,
        predictive,
        precision,
        predictive_period,
        period_onset,
        auxiliary,
        absolute_difference_threshold,
        percentage_difference_threshold,
        expected_result,
        test_id,
    ):
        if isinstance(expected_result, tuple):
            try:
                results = totals_and_components(
                    identifier=identifier,
                    period=period,
                    total=total,
                    components=components,
                    amend_total=amend_total,
                    predictive=predictive,
                    precision=precision,
                    predictive_period=predictive_period,
                    period_onset=period_onset,
                    auxiliary=auxiliary,
                    absolute_difference_threshold=absolute_difference_threshold,
                    percentage_difference_threshold=percentage_difference_threshold,
                )

                # Capture the printed output and remove any leading or trailing whitespace
                captured = capfd.readouterr()
                printed_output = captured.out.strip()

                print(printed_output)

                assert results.identifier == expected_result[0]
                assert results.period == expected_result[1]
                assert results.absolute_difference == expected_result[2]
                assert results.low_percent_threshold == expected_result[3]
                assert results.high_percent_threshold == expected_result[4]
                assert results.precision == expected_result[5]
                assert results.final_total == expected_result[6]
                assert results.final_components == expected_result[7]

                getcontext().prec = results.precision
                if results.tcc_marker == "T" or results.tcc_marker == "C":
                    sum_of_components = Decimal("0")
                    for component in results.final_components:
                        sum_of_components += Decimal(str(component))

                    sum_of_components = float(sum_of_components)
                    assert sum_of_components == expected_result[6]

            except Exception as e:
                pytest.fail(
                    EXCEPTION_FAIL_MESSAGE.format(
                        test_id=test_id,
                        exception_type=type(e).__name__,
                        exception_msg=str(e.args),
                    )
                )
        else:
            with pytest.raises(Exception) as exc_info:
                totals_and_components(
                    identifier=identifier,
                    period=period,
                    total=total,
                    components=components,
                    amend_total=amend_total,
                    predictive=predictive,
                    precision=precision,
                    predictive_period=predictive_period,
                    period_onset=period_onset,
                    auxiliary=auxiliary,
                    absolute_difference_threshold=absolute_difference_threshold,
                    percentage_difference_threshold=percentage_difference_threshold,
                )
                print(str(exc_info.value))
            assert (str(exc_info.value)) == str(expected_result)
