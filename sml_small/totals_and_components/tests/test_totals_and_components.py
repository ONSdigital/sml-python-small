import random
from decimal import Decimal

import pytest

from sml_small.totals_and_components.totals_and_components import (ComponentPair, TACException, TccMarker,
                                                                   check_absolute_difference_threshold,
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
        "identifier, total, components, amend_total, predictive, "
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
                "100",
                [
                    ComponentPair(original_value=1, final_value=None),
                    ComponentPair(original_value=2, final_value=None),
                    ComponentPair(original_value=3, final_value=None),
                    ComponentPair(original_value=4, final_value=None),
                ],
                True,
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
                ),
                "Test 15: Total is a string of a number",
                # Test to ensure total number entered as a string passes
            ),
            (
                "P",
                100,
                [
                    ComponentPair(original_value=1, final_value=None),
                    ComponentPair(original_value=2, final_value=None),
                    ComponentPair(original_value=3, final_value=None),
                    ComponentPair(original_value=4, final_value=None),
                ],
                True,
                "100.0",
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
                ),
                "Test 16: predictive is a string of a number",
                # Test to ensure predictive number entered as a string passes
            ),
            (
                "Q",
                100,
                [
                    ComponentPair(original_value=1, final_value=None),
                    ComponentPair(original_value=2, final_value=None),
                    ComponentPair(original_value=3, final_value=None),
                    ComponentPair(original_value=4, final_value=None),
                ],
                True,
                100.0,
                "300.0",
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
                ),
                "Test 17: auxiliary is a string of a number",
                # Test to ensure auxiliary number entered as a string passes
            ),
            (
                "R",
                100,
                [
                    ComponentPair(original_value=1, final_value=None),
                    ComponentPair(original_value=2, final_value=None),
                    ComponentPair(original_value=3, final_value=None),
                    ComponentPair(original_value=4, final_value=None),
                ],
                True,
                100.0,
                300.0,
                "20",
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
                ),
                "Test 18: absolute difference threshold is a string of a number",
                # Test to ensure absolute difference threshold number entered as a string passes
            ),
            (
                "S",
                100,
                [
                    ComponentPair(original_value=1, final_value=None),
                    ComponentPair(original_value=2, final_value=None),
                    ComponentPair(original_value=3, final_value=None),
                    ComponentPair(original_value=4, final_value=None),
                ],
                True,
                100.0,
                300.0,
                20,
                "0.1",
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
                ),
                "Test 19: percentage difference threshold is a string of a number",
                # Test to ensure percentage difference threshold number entered as a string passes
            ),
            (
                "R",
                100,
                [
                    ComponentPair(original_value=1, final_value=None),
                    ComponentPair(original_value=2, final_value=None),
                    ComponentPair(original_value=3, final_value=None),
                    ComponentPair(original_value=4, final_value=None),
                ],
                True,
                100.0,
                300.0,
                20,
                0.1,
                "6",
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
                ),
                "Test 20: precision is a string of a number",
                # Test to ensure precision number entered as a string passes
            ),
        ],
    )
    def test_validate_input(
        self,
        identifier,
        total,
        components,
        amend_total,
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
                    auxiliary=auxiliary,
                    absolute_difference_threshold=absolute_difference_threshold,
                    percentage_difference_threshold=percentage_difference_threshold,
                    precision=precision,
                )
                print(exc_info.value)
            assert exc_info.type == expected_result


class TestSetPredictiveValue:
    @pytest.mark.parametrize(
        "predictive, auxiliary, expected_result, test_id",
        [
            (
                100.0,
                None,
                (100.0, TccMarker.METHOD_PROCEED),
                "Test 1: Predictive Only",
                # Test for when a predictive value is provided,
                # we would expect the predictive value to remain unchanged
            ),
            (
                None,
                50.0,
                (50.0, TccMarker.METHOD_PROCEED),
                "Test 2: Auxiliary Only"
                # Test for when a predictive value is not provided,
                # we would expect the auxiliary value to be used in
                # place of the predictive value
            ),
            (
                None,
                None,
                (None, TccMarker.STOP),
                "Test 3: Predictive and auxiliary are None",
                # Test for when a predictive and auxiliary value is not provided,
                # we would expect the method to stop
            ),
            (
                150.0,
                50.0,
                (150.0, TccMarker.METHOD_PROCEED),
                "Test 4: All Inputs"
                # Test for when a all values is are provided,
                # we would expect the predictive is not changed
            ),
        ],
    )
    def test_set_predictive_value(
        self,
        predictive,
        auxiliary,
        expected_result,
        test_id,
    ):
        try:
            result = set_predictive_value(
                predictive=predictive,
                auxiliary=auxiliary,
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
        "amend_total, components_sum, original_components, predictive, precision,"
        "expected_result, test_id",
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
            (
                False,
                82.0,
                [ComponentPair(8.2, None)] * 10,
                100.0,
                2,
                (100.0, [10.0] * 10, "C"),
                "Test 3: Test absolute difference",
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
                amend_total, components_sum, original_components, predictive, precision
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
        "components_sum, components, total, precision,"
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
        components,
        total,
        precision,
        expected_total,
        expected_component,
        test_id,
    ):
        try:
            result = correct_components(
                components_sum=components_sum,
                components=components,
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
        "identifier, total, components, amend_total, predictive, precision,"
        "auxiliary, absolute_difference_threshold, percentage_difference_threshold,"
        "expected_result, test_id",
        [
            (
                "A",
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
                None,
                11,
                None,
                (
                    "A",
                    0,
                    None,
                    None,
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
                None,
                11,
                None,
                (
                    "B",
                    6,
                    None,
                    None,
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
                None,
                None,
                0.1,
                (
                    "C",
                    None,
                    90,
                    110,
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
                None,
                25,
                0.1,
                (
                    "D",
                    339,
                    1462.5,
                    1787.5,
                    1964,
                    [632, 732, 99, 162],
                    "M",
                ),
                "Test 4 - Manual correction required TCC Marker M ",
                # This test that if the predictive is not within the threshold limits
                # then we get M tcc marker
            ),
            (
                "E",
                306,
                [
                    (240),
                    (0),
                    (30),
                    (10),
                ],
                True,
                306,
                28,
                None,
                25,
                0.1,
                (
                    "E",
                    26,
                    252,
                    308,
                    28,
                    280,
                    [240, 0, 30, 10],
                    "T",
                ),
                "Test 5 - Totals Corrected",
                # This test checks if totals gets corrected
            ),
            (
                "F",
                11,
                [
                    (0),
                    (0),
                    (0),
                    (0),
                ],
                True,
                11,
                1,
                None,
                11,
                None,
                (
                    "F",
                    None,
                    None,
                    None,
                    11,
                    [0, 0, 0, 0],
                    "S",
                ),
                "Test 6 - Predictive variable is None and sum of components is 0 (zero case)",
                # If the predictive is passed as a 11 and auxiliary is also None so total is not
                # used with but sum of components = 0 so we have S tcc marker
            ),
            (
                "H",
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
                None,
                11,
                0.1,
                TACException(
                    "('identifier: H', ValueError('component=InvalidString is missing or not a number'))"
                ),
                "Test 7 - Invalid component value entered by user",
                # An invalid component is passed to the method which is not allowed
                # hence we will throw an error
            ),
            (
                "I",
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
                None,
                11,
                0.1,
                TACException(
                    "('identifier: I', ValueError('predictive must not be a string'))"
                ),
                # An invalid predictive is passed to the method which is not allowed
                # hence we will throw an error
                "Test 8 - Invalid predictive value entered by user",
            ),
            (
                "J",
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
                "InvalidString",
                11,
                0.1,
                TACException(
                    "('identifier: J', ValueError('auxiliary is missing or not a number'))"
                ),
                # An invalid auxiliary is passed to the method which is not allowed
                # hence we will throw an error
                "Test 9 - Invalid auxiliary value entered by user",
            ),
            (
                "K",
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
                None,
                None,
                None,
                TACException(
                    "('identifier: K', ValueError('One or both of absolute/percentage difference thresholds must be specified'))"  # noqa: E501
                ),
                # An invalid ADT or PDT is passed to the method which is not allowed
                # hence we will throw an error
                "Test 10 - Absolute and percentage difference threshold None value entered by user",
            ),
            (
                "L",
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
                10817,
                11,
                None,
                (
                    "L",
                    6,
                    None,
                    None,
                    10811,
                    [9201, 866, 632, 112],
                    "T",
                ),
                "Test 11 - Auxiliary variable replaces the missing predictive variable",
                # If the predictive is None we trigger the check_auxiliary_value function
                # this will replace the predictive with the auxiliary
                #  as the auxiliary is not none
            ),
            (
                "M",
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
                None,
                11,
                None,
                (
                    "M",
                    0,
                    None,
                    None,
                    0,
                    [0, 0, 0, 0],
                    "N",
                ),
                "Test 12 - Predictive value is 0 and component sum is zero",
                # Special case where if both are zero we return N tcc marker
            ),
            (
                "N",
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
                None,
                11,
                None,
                (
                    "N",
                    6,
                    None,
                    None,
                    10811,
                    [9201, 866, 632, 112],
                    "T",
                ),
                "Test 13 - Absolute Difference Threshold only specified and satisfied",
                # Test checking ADT passes to totals correction and corrects the total
            ),
            (
                "O",
                5,
                [(1), (2), (3), (4)],
                True,
                5,
                1,
                None,
                4,
                None,
                (
                    "O",
                    5,
                    None,
                    None,
                    5,
                    [1, 2, 3, 4],
                    "M",
                ),
                "Test 14 - Absolute Difference Threshold only specified and not satisfied",
                # Test checking ADT fails to totals correction and returns M tcc marker
            ),
            (
                "P",
                9,
                [(1), (2), (3), (4)],
                True,
                9,
                28,
                None,
                None,
                0.1,
                (
                    "P",
                    None,
                    9,
                    11,
                    10,
                    [1, 2, 3, 4],
                    "T",
                ),
                "Test 15 - Percentage Difference Threshold only specified and satisfied",
                # Test checking PDT passes to component correction and corrects the components
            ),
            (
                "Q",
                5,
                [(1), (2), (3), (4)],
                True,
                5,
                28,
                None,
                None,
                0.1,
                (
                    "Q",
                    None,
                    9,
                    11,
                    5,
                    [1, 2, 3, 4],
                    "M",
                ),
                "Test 16 - Percentage Difference Threshold only specified and not satisfied",
                # Test checking PDT returns M marker
            ),
            (
                "R",
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
                None,
                11,
                0.1,
                (
                    "R",
                    6,
                    9729.9,
                    11892.1,
                    10811,
                    [9201, 866, 632, 112],
                    "T",
                ),
                "Test 17 - ADT and PDT specified and ADT satisfied",
                # Check that the T marker is returned when a happy path is provided
            ),
            (
                "S",
                9,
                [(1), (2), (3), (4)],
                False,
                9,
                2,
                None,
                4,
                0.1,
                (
                    "S",
                    1,
                    9,
                    11,
                    9,
                    [0.9, 1.8, 2.7, 3.6],
                    "C",
                ),
                "Test 18 - ADT and PDT specified and ADT not satisfied and PDT satisfied",
                # Test to check that PDT can still complete a component correction
            ),
            (
                "U",
                5,
                [(1), (2), (3), (4)],
                False,
                5,
                1,
                None,
                0,
                0,
                (
                    "U",
                    5,
                    None,
                    None,
                    5,
                    [1, 2, 3, 4],
                    "M",
                ),
                "Test 19 - Absolute and Percentage Difference Thresholds set to zero",
                # Test checking for a error exception thrown when we provide
                # zero values for ADT and PDT this is caught in validate input
            ),
            (
                "T",
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
                None,
                None,
                None,
                TACException(
                    "('identifier: T', ValueError('One or both of absolute/percentage difference thresholds must be specified'))"  # noqa: E501
                ),
                "Test 20 - Absolute and Percentage Difference Thresholds not specified",
                # Test checking for a error exception thrown when we provide
                # zero values for ADT or PDT this is caught in validate input
            ),
            (
                "U",
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
                None,
                11,
                None,
                (
                    "U",
                    None,
                    None,
                    None,
                    10817,
                    [0, 0, 0, 0],
                    "S",
                ),
                "Test 21 - Zero Case 1",
                # If target total > 0 and
                # components sum = 0 and amend total = TRUE:
                # No correction should be applied in this case.
                # A total only may be provided if the component
                # breakdown is unknown so would not want to remove true values.
            ),
            (
                "V",
                10817,
                [(0), (0), (0), (0)],
                False,
                10817,
                1,
                None,
                11,
                None,
                (
                    "V",
                    None,
                    None,
                    None,
                    10817,
                    [0, 0, 0, 0],
                    "S",
                ),
                "Test 22 - Zero Case 2",
                # If target total > 0 and components sum = 0 and
                # amend total = FALSE: In this case, the proportions
                # of the true components are unknown so the method
                # cannot apply a correction.
            ),
            (
                "W",
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
                None,
                11,
                None,
                (
                    "W",
                    10811,
                    None,
                    None,
                    0,
                    [9201, 866, 632, 112],
                    "M",
                ),
                "Test 23 - Zero Case 3",
                # If target total = 0 and components sum > 0
                # and amend total = TRUE: The total should be
                # corrected if the difference observed is
                # within the tolerances determined by the
                # detection method. Else, the difference
                # should be flagged for manual checking.
            ),
            (
                "X",
                0,
                [(10), (10), (10), (10)],
                False,
                0,
                1,
                None,
                45,
                None,
                (
                    "X",
                    40,
                    None,
                    None,
                    0,
                    [0, 0, 0, 0],
                    "C",
                ),
                "Test 24 - Zero Case 4 (where difference is within thresholds",
                # If target total = 0 and components > 0 and amend total = FALSE.
                # Apply correction to override the components with zeros if the
                # difference observed is within the tolerances determined by the
                # detection method. Else, the difference should be flagged for
                # manual checking.
            ),
            (
                "Y",
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
                None,
                None,
                0.1,
                (
                    "Y",
                    None,
                    9,
                    11,
                    0,
                    [1, 2, 3, 4],
                    "M",
                ),
                "Test 25 - Zero Case 4 (where difference are not within the threshold)",
                # If target total = 0 and components > 0 and amend total = FALSE.
                # Apply correction to override the components with zeros if the
                # difference observed is within the tolerances determined by the
                # detection method. Else, the difference should be flagged for
                # manual checking.
            ),
            (
                "Z",
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
                None,
                11,
                None,
                (
                    "Z",
                    7.9,
                    None,
                    None,
                    10.9,
                    [2.4, 2.6, 2.8, 3.1],
                    "T",
                ),
                "Test 26 - Amend Total True floating point components and floating point total",
                # Test to check if the floating point
                # components sum to equal a floating total value
                # when amend total is true.
            ),
            (
                "AA",
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
                None,
                16,
                None,
                (
                    "AA",
                    8.9,
                    None,
                    None,
                    2,
                    [
                        0.44036697247706424,
                        0.47706422018348627,
                        0.5137614678899083,
                        0.5688073394495413,
                    ],
                    "C",
                ),
                "Test 27 - Amend Total False floating point components and floating point total",
                # Test to check if the floating point
                # components sum to equal a floating total value
                # when amend total is false.
            ),
            (
                "AB",
                7,
                [(1), (2), (3), (4)],
                True,
                7,
                28,
                None,
                None,
                0.1,
                (
                    "AB",
                    None,
                    9,
                    11,
                    7,
                    [1, 2, 3, 4],
                    "M",
                ),
                "Test 28 - predictive is less than lower threshold",
                # Test to check the margins for the thresholds of the lower limit
            ),
            (
                "AC",
                10.5,
                [(1), (2), (3), (4)],
                True,
                10.5,
                28,
                None,
                None,
                0.1,
                (
                    "AC",
                    None,
                    9,
                    11,
                    10,
                    [1, 2, 3, 4],
                    "T",
                ),
                "Test 29 - predictive is greater than lower threshold",
                # Test to check the margins for the thresholds of the lower limit
            ),
            (
                "AD",
                9,
                [(1), (2), (3), (4)],
                False,
                9,
                2,
                None,
                None,
                0.1,
                (
                    "AD",
                    None,
                    9,
                    11,
                    9,
                    [0.9, 1.8, 2.7, 3.6],
                    "T",
                ),
                "Test 30 - predictive is equal to lower threshold and amend value is false",
                # Test to check the margins for the thresholds of the lower limit
            ),
            (
                "AE",
                10.9,
                [(1), (2), (3), (4)],
                True,
                10.9,
                28,
                None,
                None,
                0.1,
                (
                    "AE",
                    None,
                    9,
                    11,
                    10.0,
                    [1, 2, 3, 4],
                    "T",
                ),
                "Test 31 - predictive is less than upper threshold",
                # Test to check the margins for the thresholds of the upper limit
            ),
            (
                "AF",
                11,
                [(1), (2), (3), (4)],
                False,
                11,
                2,
                None,
                None,
                0.1,
                (
                    "AF",
                    None,
                    9,
                    11,
                    11,
                    [1.1, 2.2, 3.3, 4.4],
                    "T",
                ),
                "Test 32 - predictive is equal to than upper threshold",
                # Test to check the margins for the thresholds of the upper limit
            ),
            (
                "AG",
                12,
                [(1), (2), (3), (4)],
                True,
                12,
                28,
                None,
                None,
                0.1,
                (
                    "AG",
                    None,
                    9,
                    11,
                    12,
                    [1, 2, 3, 4],
                    "M",
                ),
                "Test 33 - predictive is greater than upper threshold",
                # Test to check the margins for the thresholds of the upper limit
            ),
            (
                "AH",
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
                0,
                11,
                None,
                TACException(
                    "('identifier: AH', ValueError('total is missing or not a number'))"
                ),
                "Test 34 - Invalid total value entered by user",
                # Test to ensure a TACException is thrown when a
                # user enters a None value for the total
            ),
            (
                None,
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
                None,
                None,
                0.1,
                TACException(
                    "('identifier: N/A', ValueError('identifier is a mandatory parameter and must be specified'))"
                ),
                "Test 35 - Missing identifier value",
                # Test to ensure a TACException is thrown when a
                # user enters a None value for the identifier
            ),
            (
                "AJ",
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
                None,
                11,
                0.1,
                TACException(
                    "('identifier: AJ', ValueError('amend_total is a mandatory parameter and must be specified as either True or False.'))"  # noqa: E501
                ),
                "Test 36 - Missing Amend total",
                # Test to ensure a TACException is thrown when a
                # user does not enter a value for the amend value
            ),
            (
                "AK",
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
                None,
                None,
                0.1,
                (
                    "AK",
                    None,
                    90,
                    110,
                    90,
                    [81, 0, 3.6, 5.4],
                    "C",
                ),
                "Test 37 - Testing precision value = 1",
                # Testing the accuracy of the components returned
                # when the entered precision value is equal to 1
            ),
            (
                "AL",
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
                None,
                None,
                0.1,
                (
                    "AL",
                    None,
                    9.81,
                    11.99,
                    10,
                    [
                        2.2018348623853212,
                        2.385321100917431,
                        2.5688073394495414,
                        2.8440366972477062,
                    ],
                    "C",
                ),
                "Test 38 - Testing precision value = 28",
                # Testing the accuracy of the components returned
                # when the entered precision value is equal to 28
            ),
            (
                "AM",
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
                None,
                11,
                None,
                TACException(
                    (
                        "identifier: AM",
                        ValueError(
                            "Precision range must be more than 0 and less than or equal to 28"
                        ),
                    )
                ),
                "Test 39 - Testing precision value = 29",
                # Testing the accuracy of the components returned
                # when the entered precision value is equal to 29
            ),
            (
                "AN",
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
                None,
                11,
                None,
                TACException(
                    (
                        "identifier: AN",
                        ValueError(
                            "Precision range must be more than 0 and less than or equal to 28"
                        ),
                    )
                ),
                "Test 40 - Testing precision value = 0",
                # Testing the accuracy of the components returned
                # when the entered precision value is equal to 0
            ),
            (
                "AO",
                11,
                [(1), (2), (3), (4)],
                False,
                11,
                2,
                None,
                None,
                0.1,
                (
                    "AO",
                    None,
                    9,
                    11,
                    11,
                    [1.1, 2.2, 3.3, 4.4],
                    "T",
                ),
                "Test 41 - Testing precision value = 2 with floating components sum to a floating total",
                # Testing the accuracy of the components returned
                # when the entered precision value is equal to 2
                # This test also checks floating components sum to a
                # floating total
            ),
            (
                "AP",
                0.6,
                [
                    (0.1),
                    (0.2),
                    (0.4),
                ],
                True,
                0.6,
                1,
                None,
                None,
                0.1,
                (
                    "AP",
                    None,
                    0.6,
                    0.8,
                    0.7,
                    [0.1, 0.2, 0.4],
                    "T",
                ),
                "Test 42 - Testing precision value = 1 with floating components sum to a floating total",
                # Testing the accuracy of the components returned
                # when the entered precision value is equal to 1
                # This test also checks floating components sum to a
                # floating total
            ),
            (
                "AQ",
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
                None,
                None,
                0.1,
                (
                    "AQ",
                    None,
                    9,
                    11,
                    10,
                    [1, 2, 3, 4],
                    "T",
                ),
                "Test 43 - Missing precision value (defaults to 28)",
                # Testing the accuracy of the components returned
                # when the precision value is missing and so defaults to 28
            ),
            (
                "AR",
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
                94,
                None,
                0.1,
                (
                    "AR",
                    None,
                    90,
                    110,
                    90,
                    [81, 0, 3.6, 5.4],
                    "C",
                ),
                "Test 44 - Auxiliary value is used  when predictive is none",
                # Predictive value is the Auxiliary value and is used to
                # determine if automatic correction can take place
            ),
            (
                "AS",
                None,
                [
                    (0),
                    (0),
                    (0),
                    (0),
                ],
                True,
                None,
                None,
                11,
                11,
                None,
                TACException(
                    (
                        "identifier: AS",
                        ValueError(
                            "total is a mandatory parameter and must be specified"
                        ),
                    )
                ),
                "Test 45 - Total is none value entered by user",
                # Test to ensure a TACException is thrown when a
                # user enters a None value for the total
            ),
            (
                "AT",
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
                None,
                0.1,
                (
                    "AT",
                    None,
                    None,
                    None,
                    90,
                    [90, 0, 4, 6],
                    "S",
                ),
                "Test 46 - method stops when predictive and auxiliary is none",
                # When total value is present, predictive value is None and
                # Auxiliary value is None then method stops
            ),
            (
                "AU",
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
                80,
                None,
                0.1,
                (
                    "AU",
                    None,
                    90,
                    110,
                    90,
                    [81, 0, 3.6, 5.4],
                    "C",
                ),
                "Test 47 - predictive value is used when predictive, auxiliary and total exist",
                # When total value is present, predictive value is present and Auxiliary value
                # is present then the decision whether an automatic correction can be made
                # will be based off of the predictive value and any recalculation of the
                # components will use the total value.
            ),
            (
                "AV",
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
                None,
                None,
                0.1,
                (
                    "AV",
                    None,
                    90,
                    110,
                    90,
                    [81, 0, 3.6, 5.4],
                    "C",
                ),
                "Test 48 - predictive value is used when auxiliary is none, predictive and total exists",
                # When total and predictive value exists
                # and Auxiliary value is none then the decision whether
                # an automatic correction can be made will be based off of the predictive value
                # and any recalculation of the components will use the total value.
            ),
            (
                "AW",
                90,
                [
                    ("90"),
                    ("0"),
                    ("4"),
                    ("6"),
                ],
                False,
                95,
                28,
                None,
                None,
                0.1,
                (
                    "AW",
                    None,
                    90,
                    110,
                    28,
                    90,
                    [81, 0, 3.6, 5.4],
                    "C",
                ),
                "Test 49 - test when components are string values",
                # When components are strings, we would expect
                # the method to still work
            ),
        ],
    )
    def test_totals_and_components(
        self,
        capfd,
        identifier,
        total,
        components,
        amend_total,
        predictive,
        precision,
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
                    total=total,
                    components=components,
                    amend_total=amend_total,
                    predictive=predictive,
                    precision=precision,
                    auxiliary=auxiliary,
                    absolute_difference_threshold=absolute_difference_threshold,
                    percentage_difference_threshold=percentage_difference_threshold,
                )

                # Capture the printed output and remove any leading or trailing whitespace
                captured = capfd.readouterr()
                printed_output = captured.out.strip()

                print(printed_output)

                assert results.identifier == expected_result[0]
                assert results.absolute_difference == expected_result[1]
                assert results.low_percent_threshold == expected_result[2]
                assert results.high_percent_threshold == expected_result[3]
                assert results.final_total == expected_result[4]
                assert results.final_components == expected_result[5]

                if results.tcc_marker == "T" or results.tcc_marker == "C":
                    sum_of_components = 0
                    for component in results.final_components:
                        sum_of_components += Decimal(str(component))

                    sum_of_components = float(sum_of_components)
                    assert sum_of_components == expected_result[4]

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
                    total=total,
                    components=components,
                    amend_total=amend_total,
                    predictive=predictive,
                    precision=precision,
                    auxiliary=auxiliary,
                    absolute_difference_threshold=absolute_difference_threshold,
                    percentage_difference_threshold=percentage_difference_threshold,
                )
            assert (str(exc_info.value)) == str(expected_result)
