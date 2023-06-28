import random

import pytest
from decimal import Decimal
from decimal import getcontext

from sml_small.totals_and_components.totals_and_components import (
    ComponentPair,
    TACException,
    check_absolute_difference_threshold,
    check_percentage_difference_threshold,
    check_predictive_value,
    check_sum_components_predictive,
    check_zero_errors,
    correct_components,
    correct_total,
    determine_error_detection,
    error_correction,
    sum_components,
    totals_and_components,
    validate_input,
)

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
        "identifier, total, components, amend_total, period, predictive, "
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
                102.0,
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
                    102.0,
                    300.0,
                    20,
                    0.1,
                    6,
                ),
                "Test 1: Correct values test",
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
                "202203",
                102.0,
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
                    102.0,
                    104.0,
                    105.0,
                    None,
                    28,
                ),
                "Test 2: None value for percentage difference threshold",
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
                "202203",
                102.0,
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
                    102.0,
                    104.0,
                    None,
                    20,
                    28,
                ),
                "Test 3: None value for absolute difference threshold",
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
                "202203",
                None,  # missing predictive
                300.0,
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
                    300.0,
                    20,
                    0.1,
                    28,
                ),
                "Test 4: Predictive is missing so method carries on",
            ),
            (
                "E",
                100.0,
                [],
                True,
                "202203",
                101.0,
                103.0,
                20,
                0.1,
                28,
                ValueError,
                "Test 5: Empty component list",
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
                "202203",
                101.0,
                103.0,
                20,
                0.1,
                28,
                ValueError,
                "Test 6: None in component list",
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
                102.0,
                104.0,
                20,
                0.1,
                28,
                ValueError,
                "Test 7: Invalid Total",
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
                "202203",
                "String",
                102.0,
                20,
                0.1,
                28,
                ValueError,
                "Test 8: Invalid predictive test",
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
                "202203",
                101.0,
                "String",
                20,
                0.1,
                28,
                ValueError,
                "Test 9: Invalid auxiliary",
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
                "202203",
                102.0,
                104.0,
                {20},
                0.1,
                28,
                ValueError,
                "Test 10: Invalid absolute difference threshold",
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
                "202203",
                102.0,
                104.0,
                20,
                {2},
                28,
                ValueError,
                "Test 11: Invalid percentage difference threshold",
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
                "202203",
                102.0,
                89.0,
                None,
                None,
                28,
                ValueError,
                "Test 12: None value for percentage and absolute difference threshold",
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
                "202203",
                102.0,
                89.0,
                11,
                0.1,
                28,
                ValueError,
                "Test 13: None value for amend value",
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
                    auxiliary=auxiliary,
                    absolute_difference_threshold=absolute_difference_threshold,
                    percentage_difference_threshold=percentage_difference_threshold,
                    precision=precision,
                )
                print(exc_info.value)
            assert exc_info.type == expected_result


class TestCheckPredictiveValue:
    @pytest.mark.parametrize(
        "predictive, auxiliary, expected_result, test_id",
        [
            (100.0, None, (100.0, "P"), "Test 1: Predictive Only"),
            (None, 50.0, (50.0, "P"), "Test 2: Auxiliary Only"),
            (None, None, (None, "S"), "Test 3: No Inputs"),
            (150.0, 50.0, (150.0, "P"), "Test 4: All Inputs"),
            (0, 0, (0, "P"), "Test 5: All 0"),
        ],
    )
    def test_check_predictive_value(
        self, predictive, auxiliary, expected_result, test_id
    ):
        try:
            result = check_predictive_value(predictive=predictive, auxiliary=auxiliary)
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
                0,
                "Test 1: Component Sum Matches Predictive",
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


class TestCorrectComponents:
    @pytest.mark.parametrize(
        "components_sum, original_components, predictive, precision, expected_total, expected_component, test_id",
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
        predictive,
        precision,
        expected_total,
        expected_component,
        test_id,
    ):
        try:
            result = correct_components(
                components_sum=components_sum,
                original_components=original_components,
                predictive=predictive,
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
        "identifier, period, total, components, amend_total, predictive, precision, predictive_period, auxiliary,"
        "absolute_difference_threshold, percentage_difference_threshold, expected_result, test_id",
        [
            (
                "A",
                "202301",
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
                None,
                11,
                None,
                (
                    "A",
                    "202301",
                    0,
                    None,
                    None,
                    28,
                    1625,
                    [632, 732, 99, 162],
                    "N",
                ),
                "Test 1 - Totals matches components TCC Marker N",
            ),
            (
                "B",
                "202301",
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
                "202301",
                None,
                11,
                None,
                (
                    "B",
                    "202301",
                    6,
                    None,
                    None,
                    28,
                    10811,
                    [9201, 866, 632, 112],
                    "T",
                ),
                "Test 2 - Totals corrected with non zero component values TCC Marker T",
            ),
            (
                "C",
                "202301",
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
                "202301",
                None,
                None,
                0.1,
                (
                    "C",
                    "202301",
                    10,
                    90,
                    110,
                    2,
                    90,
                    [81, 0, 3.6, 5.4],
                    "C",
                ),
                "Test 3 - Components corrected - TCC Marker C",
            ),
            (
                "D",
                "202312",
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
                "202312",
                None,
                1,
                0.1,
                (
                    "D",
                    "202312",
                    339,
                    1462.5,
                    1787.5,
                    28,
                    1964,
                    [632, 732, 99, 162],
                    "M",
                ),
                "Test 4 - Manual correction required TCC Marker M ",
            ),
            (
                "F",
                "202312",
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
                "202312",
                None,
                11,
                None,
                (
                    "F",
                    "202312",
                    None,
                    None,
                    None,
                    1,
                    11,
                    [0, 0, 0, 0],
                    "S",
                ),
                "Test 5 - Predictive variable is None",
            ),
            (
                "H",
                "202301",
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
                "202301",
                None,
                11,
                0.1,
                TACException("component=InvalidString is missing or not a number"),
                "Test 6 - Invalid component value entered by user",
            ),
            (
                "I",
                "202301",
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
                "202301",
                None,
                11,
                0.1,
                TACException("predictive must not be a string"),
                "Test 7 - Invalid predictive value entered by user",
            ),
            (
                "J",
                "202301",
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
                "202301",
                "InvalidString",
                11,
                0.1,
                TACException("auxiliary is missing or not a number"),
                "Test 8 - Invalid auxiliary value entered by user",
            ),
            (
                "K",
                "202301",
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
                "202301",
                None,
                None,
                None,
                TACException("One or both of absolute/percentage difference thresholds must be specified and non-zero"),
                "Test 9 - Absolute and percentage difference threshold None value entered by user",
            ),
            (
                "L",
                "202301",
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
                "202301",
                10817,
                11,
                None,
                (
                    "L",
                    "202301",
                    6,
                    None,
                    None,
                    28,
                    10811,
                    [9201, 866, 632, 112],
                    "T",
                ),
                "Test 10 - Auxiliary variable replaces the missing predictive variable",
            ),
            (
                "M",
                "202301",
                10817,
                [
                    (0),
                    (0),
                    (0),
                    (0),
                ],
                True,
                0,
                28,
                "202301",
                None,
                11,
                None,
                (
                    "M",
                    "202301",
                    0,
                    None,
                    None,
                    28,
                    10817,
                    [0, 0, 0, 0],
                    "N",
                ),
                "Test 11 - Predictive value is 0 and component sum is zero",
            ),
            (
                "N",
                "202301",
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
                "202301",
                None,
                11,
                None,
                (
                    "N",
                    "202301",
                    6,
                    None,
                    None,
                    28,
                    10811,
                    [9201, 866, 632, 112],
                    "T",
                ),
                "Test 12 - Absolute Difference Threshold only specified and satisfied",
            ),
            (
                "O",
                "202301",
                15,
                [(1), (2), (3), (4)],
                True,
                5,
                1,
                "202301",
                None,
                4,
                None,
                (
                    "O",
                    "202301",
                    5,
                    None,
                    None,
                    1,
                    15,
                    [1, 2, 3, 4],
                    "M",
                ),
                "Test 13 - Absolute Difference Threshold only specified and not satisfied",
            ),
            (
                "P",
                "202301",
                9,
                [(1), (2), (3), (4)],
                True,
                9,
                28,
                "202301",
                None,
                None,
                0.1,
                (
                    "P",
                    "202301",
                    1,
                    9,
                    11,
                    28,
                    10,
                    [1, 2, 3, 4],
                    "T",
                ),
                "Test 14 - Percentage Difference Threshold only specified and satisfied",
            ),
            (
                "Q",
                "202301",
                15,
                [(1), (2), (3), (4)],
                True,
                5,
                28,
                "202301",
                None,
                None,
                0.1,
                (
                    "Q",
                    "202301",
                    5,
                    9,
                    11,
                    28,
                    15,
                    [1, 2, 3, 4],
                    "M",
                ),
                "Test 15 - Percentage Difference Threshold only specified and not satisfied",
            ),
            (
                "R",
                "202301",
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
                "202301",
                None,
                11,
                0.1,
                (
                    "R",
                    "202301",
                    6,
                    9729.9,
                    11892.1,
                    28,
                    10811,
                    [9201, 866, 632, 112],
                    "T",
                ),
                "Test 16 - ADT and PDT specified and ADT satisfied",
            ),
            (
                "S",
                "202301",
                15,
                [(1), (2), (3), (4)],
                False,
                9,
                2,
                "202301",
                None,
                4,
                0.1,
                (
                    "S",
                    "202301",
                    1,
                    9,
                    11,
                    2,
                    9,
                    [0.9, 1.8, 2.7, 3.6],
                    "C",
                ),
                "Test 17 - ADT and PDT specified and ADT not satisfied and PDT satisfied",
            ),
            (
                "U",
                "202301",
                15,
                [(1), (2), (3), (4)],
                False,
                5,
                1,
                "202301",
                None,
                0,
                0,
                TACException("One or both of absolute/percentage difference thresholds must be specified and non-zero"),
                "Test 18 - Absolute and Percentage Difference Thresholds set to zero",
            ),
            (
                "T",
                "202301",
                15,
                [
                    (0),
                    (0),
                    (0),
                    (0),
                ],
                True,
                5,
                1,
                "202301",
                None,
                None,
                None,
                TACException("One or both of absolute/percentage difference thresholds must be specified and non-zero"),
                "Test 19 - Absolute and Percentage Difference Thresholds not specified",
            ),
            (
                "U",
                "202301",
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
                "202301",
                None,
                11,
                None,
                (
                    "U",
                    "202301",
                    None,
                    None,
                    None,
                    1,
                    10817,
                    [0, 0, 0, 0],
                    "S",
                ),
                "Test 20 - Zero Case 1",
            ),
            (
                "V",
                "202301",
                10817,
                [(0), (0), (0), (0)],
                False,
                10817,
                1,
                "202301",
                None,
                11,
                None,
                (
                    "V",
                    "202301",
                    None,
                    None,
                    None,
                    1,
                    10817,
                    [0, 0, 0, 0],
                    "S",
                ),
                "Test 21 - Zero Case 2",
            ),
            (
                "W",
                "202301",
                10817,
                [
                    (9201),
                    (866),
                    (632),
                    (112),
                ],
                True,
                0,
                28,
                "202301",
                None,
                11,
                None,
                (
                    "W",
                    "202301",
                    10811,
                    None,
                    None,
                    28,
                    10817,
                    [9201, 866, 632, 112],
                    "M",
                ),
                "Test 22 - Zero Case 3",
            ),
            (
                "X",
                "202301",
                40,
                [(10), (10), (10), (10)],
                False,
                0,
                1,
                "202301",
                None,
                45,
                None,
                (
                    "X",
                    "202301",
                    40,
                    None,
                    None,
                    1,
                    0,
                    [0, 0, 0, 0],
                    "C",
                ),
                "Test 23 - Zero Case 4 (where difference is within thresholds",
            ),
            (
                "Y",
                "202301",
                10817,
                [
                    (9201),
                    (866),
                    (632),
                    (112),
                ],
                False,
                0,
                28,
                "202301",
                None,
                11,
                None,
                (
                    "Y",
                    "202301",
                    10811,
                    None,
                    None,
                    28,
                    10817,
                    [9201, 866, 632, 112],
                    "M",
                ),
                "Test 24 - Zero Case 4 (where difference are not within the threshold)",
            ),
            (
                "Z",
                "202301",
                10817,
                [
                    (2.4),
                    (2.6),
                    (2.8),
                    (3.1),
                ],
                True,
                3,
                28,
                "202301",
                None,
                11,
                None,
                (
                    "Z",
                    "202301",
                    7.9,
                    None,
                    None,
                    28,
                    10.9,
                    [2.4, 2.6, 2.8, 3.1],
                    "T",
                ),
                "Test 25 - Amend Total True floating point components and floating point total",
            ),
            (
                "AA",
                "202301",
                10817,
                [
                    (2.4),
                    (2.6),
                    (2.8),
                    (3.1),
                ],
                False,
                2,
                28,
                "202301",
                None,
                16,
                None,
                (
                    "AA",
                    "202301",
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
            ),
            (
                "AB",
                "202301",
                15,
                [(1), (2), (3), (4)],
                True,
                7,
                28,
                "202301",
                None,
                None,
                0.1,
                (
                    "AB",
                    "202301",
                    3,
                    9,
                    11,
                    28,
                    15,
                    [1, 2, 3, 4],
                    "M",
                ),
                "Test 27 - predictive is less than lower threshold",
            ),
            (
                "AC",
                "202301",
                15,
                [(1), (2), (3), (4)],
                True,
                10.5,
                28,
                "202301",
                None,
                None,
                0.1,
                (
                    "AC",
                    "202301",
                    0.5,
                    9,
                    11,
                    28,
                    10,
                    [1, 2, 3, 4],
                    "T",
                ),
                "Test 28 - predictive is greater than lower threshold",
            ),
            (
                "AD",
                "202301",
                15,
                [(1), (2), (3), (4)],
                False,
                9,
                2,
                "202301",
                None,
                None,
                0.1,
                (
                    "AD",
                    "202301",
                    1,
                    9,
                    11,
                    2,
                    9,
                    [0.9, 1.8, 2.7, 3.6],
                    "T",
                ),
                "Test 29 - predictive is equal to lower threshold and amend value is false",
            ),
            (
                "AE",
                "202301",
                15,
                [(1), (2), (3), (4)],
                True,
                10.9,
                28,
                "202301",
                None,
                None,
                0.1,
                (
                    "AE",
                    "202301",
                    0.9,
                    9,
                    11,
                    28,
                    10.0,
                    [1, 2, 3, 4],
                    "T",
                ),
                "Test 30 - predictive is less than upper threshold",
            ),
            (
                "AF",
                "202301",
                15,
                [(1), (2), (3), (4)],
                False,
                11,
                2,
                "202301",
                None,
                None,
                0.1,
                (
                    "AF",
                    "202301",
                    1,
                    9,
                    11,
                    2,
                    11,
                    [1.1, 2.2, 3.3, 4.4],
                    "T",
                ),
                "Test 31 - predictive is equal to than upper threshold",
            ),
            (
                "AG",
                "202301",
                15,
                [(1), (2), (3), (4)],
                True,
                12,
                28,
                "202301",
                None,
                None,
                0.1,
                (
                    "AG",
                    "202301",
                    2.0,
                    9,
                    11,
                    28,
                    15,
                    [1, 2, 3, 4],
                    "M",
                ),
                "Test 32 - predictive is greater than upper threshold",
            ),
            (
                "AH",
                "202312",
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
                "202312",
                None,
                11,
                None,
                TACException("total is missing or not a number"),
                "Test 33 - Invalid total value entered by user",
            ),
            (
                None,
                "202301",
                15,
                [
                    (1),
                    (2),
                    (3),
                    (4),
                ],
                True,
                10.9,
                28,
                "202301",
                None,
                None,
                0.1,
                TACException("The identifier is not populated"),
                "Test 34 - Missing identifier value",
            ),
            (
                "AI",
                "202301",
                15,
                [
                    (1),
                    (2),
                    (3),
                    (4),
                ],
                True,
                10.9,
                28,
                "",
                None,
                None,
                0.1,
                (
                    "AI",
                    "202301",
                    0.9,
                    9,
                    11,
                    28,
                    10,
                    [1, 2, 3, 4],
                    "T",
                ),
                "Test 35 - Missing period value",
            ),
            (
                "AJ",
                "202301",
                15,
                [
                    (1),
                    (2),
                    (3),
                    (4),
                ],
                None,
                10.9,
                1,
                "202301",
                None,
                11,
                0.1,
                TACException("Amend total needs to be True or False"),
                "Test 36 - Missing Amend total",
            ),
            (
                "AP",
                "202301",
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
                "202301",
                None,
                None,
                0.1,
                (
                    "AP",
                    "202301",
                    10,
                    90,
                    110,
                    28,
                    90,
                    [81, 0, 3.6, 5.4],
                    "C",
                ),
                "Test 42 - Testing precision value = 1",
            ),
            (
                "AQ",
                "202301",
                10817,
                [
                    (2.4),
                    (2.6),
                    (2.8),
                    (3.1),
                ],
                False,
                10,
                28,
                "202301",
                None,
                None,
                0.1,
                (
                    "AQ",
                    "202301",
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
            ),
            (
                "AR",
                "202301",
                10817,
                [
                    (2.4),
                    (2.6),
                    (2.8),
                    (3.1),
                ],
                False,
                2,
                29,
                "202301",
                None,
                11,
                None,
                TACException("Precision range must be more than 0 and less than or equal to 28"),
                "Test 44 - Testing precision value = 29",
            ),
            (
                "AS",
                "202301",
                10817,
                [
                    (2.4),
                    (2.6),
                    (2.8),
                    (3.1),
                ],
                False,
                2,
                0,
                "202301",
                None,
                11,
                None,
                TACException("Precision range must be more than 0 and less than or equal to 28"),
                "Test 45 - Testing precision value = 0",
            ),
            (
                "AT",
                "202301",
                15,
                [(1), (2), (3), (4)],
                False,
                11,
                2,
                "202301",
                None,
                None,
                0.1,
                (
                    "AT",
                    "202301",
                    1,
                    9,
                    11,
                    2,
                    11,
                    [1.1, 2.2, 3.3, 4.4],
                    "T",
                ),
                "Test 46 - Testing precision value = 2 with floating components sum to a floating total",
            ),
            (
                "AU",
                "202301",
                10817,
                [
                    (0.1),
                    (0.2),
                    (0.4),
                ],
                True,
                0.6,
                1,
                "202301",
                None,
                None,
                0.1,
                (
                    "AU",
                    "202301",
                    0.1,
                    0.6,
                    0.8,
                    1,
                    0.7,
                    [0.1, 0.2, 0.4],
                    "T",
                ),
                "Test 47 - Testing precision value = 1 with floating components sum to a floating total",
            ),
            (
                "AW",
                "202301",
                15,
                [
                    (1),
                    (2),
                    (3),
                    (4),
                ],
                True,
                10.9,
                None,
                "202101",
                None,
                None,
                0.1,
                (
                    "AW",
                    "202301",
                    0.9,
                    9,
                    11,
                    28,
                    10,
                    [1, 2, 3, 4],
                    "T",
                ),
                "Test 48 - Missing precision value (defaults to 28)",
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
                    auxiliary=auxiliary,
                    absolute_difference_threshold=absolute_difference_threshold,
                    percentage_difference_threshold=percentage_difference_threshold,
                )
                print(str(exc_info.value))
            assert (str(exc_info.value)) == str(expected_result)
