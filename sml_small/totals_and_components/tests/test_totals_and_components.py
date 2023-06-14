import random

import pytest

from sml_small.totals_and_components.totals_and_components import (Component_list, TACException, check_absolute_difference_threshold,
                                                                   check_percentage_difference_threshold,
                                                                   check_predictive_value,
                                                                   check_sum_components_predictive, check_zero_errors,
                                                                   correct_components, correct_total,
                                                                   determine_error_detection, error_correction,
                                                                   sum_components, totals_and_components,
                                                                   validate_input)

EXCEPTION_FAIL_MESSAGE = (
    "{test_id} : Expected no exception, but got {exception_type}: {exception_msg}"
)


class TestValidateInput:
    @pytest.mark.parametrize(
        "identifier, period, total, components, amend_total, predictive, "
        "predictive_period, auxiliary, absolute_difference_threshold, "
        "percentage_difference_threshold, expected_result, test_id",
        [
            (
                "A",
                "202312",
                100,
                [
                    Component_list(original_value=1, final_value=None),
                    Component_list(original_value=2, final_value=None),
                    Component_list(original_value=3, final_value=None),
                    Component_list(original_value=4, final_value=None),
                ],
                101.0,
                102.0,
                "202312",
                300.0,
                20,
                0.1,
                (
                    100,
                    [
                        Component_list(original_value=1, final_value=None),
                        Component_list(original_value=2, final_value=None),
                        Component_list(original_value=3, final_value=None),
                        Component_list(original_value=4, final_value=None),
                    ],
                    102.0,
                    300.0,
                    20,
                    0.1,
                ),
                "Test 1: Correct values test",
            ),
            (
                "B",
                "202312",
                100.0,
                [
                    Component_list(original_value=1, final_value=None),
                    Component_list(original_value=2, final_value=None),
                    Component_list(original_value=3, final_value=None),
                    Component_list(original_value=4, final_value=None),
                ],
                102.0,
                103.0,
                "202312",
                104.0,
                105.0,
                None,
                (
                    100.0,
                    [
                        Component_list(original_value=1, final_value=None),
                        Component_list(original_value=2, final_value=None),
                        Component_list(original_value=3, final_value=None),
                        Component_list(original_value=4, final_value=None),
                    ],
                    103.0,
                    104.0,
                    105.0,
                    None,
                ),
                "Test 2: None value for percentage difference threshold",
            ),
            (
                "C",
                "202312",
                100.0,
                [
                    Component_list(original_value=1, final_value=None),
                    Component_list(original_value=2, final_value=None),
                    Component_list(original_value=3, final_value=None),
                    Component_list(original_value=4, final_value=None),
                ],
                102.0,
                103.0,
                "202312",
                104.0,
                None,
                20,
                (
                    100.0,
                    [
                        Component_list(original_value=1, final_value=None),
                        Component_list(original_value=2, final_value=None),
                        Component_list(original_value=3, final_value=None),
                        Component_list(original_value=4, final_value=None),
                    ],
                    103.0,
                    104.0,
                    None,
                    20,
                ),
                "Test 3: None value for absolute difference threshold",
            ),
            (
                "D",
                "202312",
                100,
                [
                    Component_list(original_value=1, final_value=None),
                    Component_list(original_value=2, final_value=None),
                    Component_list(original_value=3, final_value=None),
                    Component_list(original_value=4, final_value=None),
                ],
                101.0,
                None,  # missing predictive
                "202312",
                300.0,
                20,
                0.1,
                (
                    100,
                    [
                        Component_list(original_value=1, final_value=None),
                        Component_list(original_value=2, final_value=None),
                        Component_list(original_value=3, final_value=None),
                        Component_list(original_value=4, final_value=None),
                    ],
                    None,  # missing predictive does not trigger value error
                    300.0,
                    20,
                    0.1,
                ),
                "Test 4: Predictive is missing so method carries on",
            ),
            (
                "E",
                "202312",
                100.0,
                [],
                101.0,
                102.0,
                "202312",
                103.0,
                20,
                0.1,
                ValueError,
                "Test 5: Empty component list",
            ),
            (
                "F",
                "202312",
                100.0,
                [
                    Component_list(original_value=None, final_value=None),
                    Component_list(original_value=2, final_value=None),
                    Component_list(original_value=3, final_value=None),
                    Component_list(original_value=4, final_value=None),
                ],
                101.0,
                102.0,
                "202312",
                103.0,
                20,
                0.1,
                ValueError,
                "Test 6: None in component list",
            ),
            (
                "G",
                "202312",
                "String",
                [
                    Component_list(original_value=1, final_value=None),
                    Component_list(original_value=2, final_value=None),
                    Component_list(original_value=3, final_value=None),
                    Component_list(original_value=4, final_value=None),
                ],
                102.0,
                103.0,
                "202312",
                104.0,
                20,
                0.1,
                ValueError,
                "Test 7: Invalid Total",
            ),
            (
                "H",
                "202312",
                100.0,
                [
                    Component_list(original_value=1, final_value=None),
                    Component_list(original_value=2, final_value=None),
                    Component_list(original_value=3, final_value=None),
                    Component_list(original_value=4, final_value=None),
                ],
                101.0,
                "String",
                "202312",
                102.0,
                20,
                0.1,
                ValueError,
                "Test 8: Invalid predictive test",
            ),
            (
                "I",
                "202312",
                100.0,
                [
                    Component_list(original_value=1, final_value=None),
                    Component_list(original_value=2, final_value=None),
                    Component_list(original_value=3, final_value=None),
                    Component_list(original_value=4, final_value=None),
                ],
                101.0,
                102.0,
                "202312",
                "String",
                20,
                0.1,
                ValueError,
                "Test 9: Invalid auxiliary",
            ),
            (
                "J",
                "202312",
                100.0,
                [
                    Component_list(original_value=1, final_value=None),
                    Component_list(original_value=2, final_value=None),
                    Component_list(original_value=3, final_value=None),
                    Component_list(original_value=4, final_value=None),
                ],
                102.0,
                103.0,
                "202312",
                104.0,
                {20},
                0.1,
                ValueError,
                "Test 10: Invalid absolute difference threshold",
            ),
            (
                "K",
                "202312",
                100.0,
                [
                    Component_list(original_value=1, final_value=None),
                    Component_list(original_value=2, final_value=None),
                    Component_list(original_value=3, final_value=None),
                    Component_list(original_value=4, final_value=None),
                ],
                102.0,
                103.0,
                "202312",
                104.0,
                20,
                {2},
                ValueError,
                "Test 11: Invalid percentage difference threshold",
            ),
            (
                "L",
                "202312",
                100.0,
                [
                    Component_list(original_value=1, final_value=None),
                    Component_list(original_value=2, final_value=None),
                    Component_list(original_value=3, final_value=None),
                    Component_list(original_value=4, final_value=None),
                ],
                102.0,
                101.0,
                "202312",
                89.0,
                None,
                None,
                ValueError,
                "Test 12: None value for percentage and absolute difference threshold",
            ),
        ],
    )
    def test_validate_input(
        self,
        identifier,
        period,
        total,
        components,
        amend_total,
        predictive,
        predictive_period,
        auxiliary,
        absolute_difference_threshold,
        percentage_difference_threshold,
        expected_result,
        test_id,
    ):
        if isinstance(expected_result, tuple):
            try:
                result = validate_input(
                    identifier=identifier,
                    period=period,
                    total=total,
                    components=components,
                    amend_total=amend_total,
                    predictive=predictive,
                    predictive_period=predictive_period,
                    auxiliary=auxiliary,
                    absolute_difference_threshold=absolute_difference_threshold,
                    percentage_difference_threshold=percentage_difference_threshold,
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
                    period=period,
                    total=total,
                    components=components,
                    amend_total=amend_total,
                    predictive=predictive,
                    predictive_period=predictive_period,
                    auxiliary=auxiliary,
                    absolute_difference_threshold=absolute_difference_threshold,
                    percentage_difference_threshold=percentage_difference_threshold,
                )
                print(exc_info.value)
            assert exc_info.type == expected_result


class TestCheckPredictiveValue:
    @pytest.mark.parametrize(
        "predictive, auxiliary, expected_result, test_id",
        [
            (100.0, None, (100.0, "P"), "Test 1: Predictive only"),
            (None, 50.0, (50.0, "P"), "Test 2: Auxiliary only"),
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
        "test_components, predictive, expected_result, test_id",
        [
            ([], 100.0, "P", "Test 1: 12 RandomComponents, predictive positive"),
            (
                [
                    Component_list(original_value=0, final_value=None),
                    Component_list(original_value=0, final_value=None),
                ],
                150.0,
                "S",
                "Test 2: Components 0, predictive positive",
            ),
            (
                [
                    Component_list(original_value=5, final_value=None),
                    Component_list(original_value=32, final_value=None),
                ],
                0,
                "P",
                "Test 3: Predictive 0, predictive positive",
            ),
        ],
    )
    def test_check_zero_errors(
        self, test_components, predictive, expected_result, test_id
    ):
        if "RandomComponents" in test_id:
            for _ in range(12):
                random_float = random.uniform(0, 12)
                component = Component_list(
                    original_value=random_float, final_value=None
                )
                test_components.append(component)

        try:
            components_sum = sum_components(test_components)
            marker = check_zero_errors(
                predictive=predictive, components_sum=components_sum
            )
            assert (
                marker == expected_result
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
        "test_components, predictive, expected_result, test_id",
        [
            (
                [
                    Component_list(original_value=3.5, final_value=None),
                    Component_list(original_value=6.5, final_value=None),
                    Component_list(original_value=8.0, final_value=None),
                    Component_list(original_value=2.0, final_value=None),
                    Component_list(original_value=4.5, final_value=None),
                    Component_list(original_value=5.5, final_value=None),
                    Component_list(original_value=2.8, final_value=None),
                    Component_list(original_value=7.2, final_value=None),
                    Component_list(original_value=1.0, final_value=None),
                    Component_list(original_value=9.0, final_value=None),
                    Component_list(original_value=0.3, final_value=None),
                    Component_list(original_value=9.7, final_value=None),
                ],
                60.0,
                0,
                "Test 1: Component Sum Matches Predictive",
            ),
            (
                [
                    Component_list(original_value=3.2, final_value=None),
                    Component_list(original_value=5.1, final_value=None),
                    Component_list(original_value=2.4, final_value=None),
                    Component_list(original_value=1.5, final_value=None),
                    Component_list(original_value=0.8, final_value=None),
                    Component_list(original_value=4.6, final_value=None),
                    Component_list(original_value=2.7, final_value=None),
                    Component_list(original_value=3.9, final_value=None),
                    Component_list(original_value=1.2, final_value=None),
                    Component_list(original_value=0.5, final_value=None),
                    Component_list(original_value=4.3, final_value=None),
                    Component_list(original_value=2.0, final_value=None),
                ],
                100.0,
                67.8,  # This is the returned stored absolute_difference value
                "Test 2: Component Sum Does NOT Match Predictive and returns absolute_difference",
            ),
        ],
    )
    def test_check_sum_components_predictive(
        self, test_components, predictive, expected_result, test_id
    ):
        try:
            components_sum = sum_components(test_components)
            absolute_difference = check_sum_components_predictive(
                predictive=predictive, components_sum=components_sum
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
        "absolute_difference_threshold, percentage_difference_threshold, absolute_difference, predictive, thresholds,"
        "expected_result, test_id",
        [
            (
                20,
                None,
                10,
                None,
                (None, None),
                ("P", 10),
                "Test 1: Absolute Difference only - Satisfied",
            ),
            (
                5,
                None,
                10,
                None,
                (None, None),
                ("M", 10),
                "Test 2: Absolute Difference only - NOT Satisfied",
            ),
            (
                None,
                10,
                None,
                15,
                (10, 20),
                ("P", None),
                "Test 3: Percentage Difference only - Satisfied",
            ),
            (
                None,
                10,
                None,
                15,
                (16, 20),
                ("M", None),
                "Test 4: Percentage Difference only - NOT Satisfied (lower)",
            ),
            (
                None,
                10,
                None,
                15,
                (10, 13),
                ("M", None),
                "Test 5: Percentage Difference only - NOT Satisfied (upper)",
            ),
            (
                20,
                10,
                10,
                15,
                (16, 20),
                ("P", 10),
                "Test 6: Both Input - Absolute Difference Satisfied",
            ),
            (
                5,
                10,
                10,
                15,
                (10, 20),
                ("P", 10),
                "Test 7: Both Input - Percentage Difference Satisfied",
            ),
            (
                5,
                10,
                10,
                15,
                (16, 20),
                ("M", 10),
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
        thresholds,
        expected_result,
        test_id,
    ):
        try:
            result = determine_error_detection(
                absolute_difference_threshold=absolute_difference_threshold,
                percentage_difference_threshold=percentage_difference_threshold,
                absolute_difference=absolute_difference,
                predictive=predictive,
                thresholds=thresholds,
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
        "predictive, thresholds, expected_result, test_id",
        [
            (
                110.0,
                (100.0, 110.0),
                True,
                "Test 1: Predictive total equals upper threshold",
            ),
            (
                120.0,
                (100.0, 110.0),
                False,
                "Test 2: Predictive total is greater than upper threshold",
            ),
            (
                110.0,
                (105.0, 115.0),
                True,
                "Test 3: Predictive total is less than upper threshold and greater than lower threshold",
            ),
            (
                79.5,
                (105.0, 115.0),
                False,
                "Test 4: Predictive total is less than lower threshold",
            ),
        ],
    )
    def test_check_percentage_difference_threshold(
        self, predictive, thresholds, expected_result, test_id
    ):
        try:
            result = check_percentage_difference_threshold(predictive, thresholds)
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
        "amend_total, components_sum, original_components, predictive, expected_total, expected_components,\
        expected_tcc_marker, test_id",
        [
            (
                True,
                100.0,
                [Component_list(10.0, None)] * 10,
                100.0,
                100.0,
                [10.0] * 10,
                "T",
                "Test 1: Amend total",
            ),
            (
                False,
                82.0,
                [Component_list(8.2, None)] * 10,
                100.0,
                100.0,
                [10.0] * 10,
                "C",
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
        expected_total,
        expected_components,
        expected_tcc_marker,
        test_id,
    ):
        try:
            result = error_correction(
                amend_total, components_sum, original_components, predictive
            )
            assert (
                result[0] == expected_total
            ), f"{test_id} - Unexpected result, Incorrect Total"
            for index, component in enumerate(result[1]):
                assert (
                    component.final_value == expected_components[index]
                ), f"{test_id} - Unexpected result, Incorrect Components"
            assert (
                result[2] == expected_tcc_marker
            ), f"{test_id} - Unexpected result, Incorrect tcc_marker"

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
                [Component_list(10.0, None)] * 10,
                100.0,
                "Test 1: Final total is sum of received components",
            ),
            (
                30.0,
                [Component_list(10.0, None)] * 10,
                30.0,
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
            assert (
                output[0] == expected_result
            ), f"Test {test_id} failed: Unexpected result"
            for component in output[1]:
                assert component.original_value == component.final_value, (
                    f"Test {test_id} failed: Final Component " f"outputs dont match"
                )
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
        "components_sum, original_components, predictive, expected_total, expected_component, test_id",
        [
            (
                90.0,
                [Component_list(9.0, None)] * 10,
                100.0,
                100.0,
                [10.0] * 10,
                "Test 1: Component = 90, " "predictive = 100",
            ),
            (
                130.0,
                [
                    Component_list(75.0, None),
                    Component_list(25.0, None),
                    Component_list(30.0, None),
                ],
                200.0,
                200.0,
                [115.38, 38.46, 46.15],
                "Test 2: Component sum = 130, Total = 200",
            ),
            (
                100.0,
                [Component_list(10.0, None)] * 10,
                0,
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
        expected_total,
        expected_component,
        test_id,
    ):
        try:
            result = correct_components(
                components_sum=components_sum,
                original_components=original_components,
                predictive=predictive,
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
        "identifier, period, total, components, amend_total, predictive, predictive_period, auxiliary,"
        "absolute_difference_threshold, percentage_difference_threshold, expected_result, test_id",
        [
            (
                "A",
                "202301",
                1625,
                [
                    Component_list(632, None),
                    Component_list(732, None),
                    Component_list(99, None),
                    Component_list(162, None),
                ],
                True,
                1625,
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
                    1625,
                    [
                        Component_list(632, 632),
                        Component_list(732, 732),
                        Component_list(99, 99),
                        Component_list(162, 162),
                    ],
                    "N",
                ),
                "Test 1 - Totals matches components TCC Marker N",
            ),
            (
                "B",
                "202301",
                10817,
                [
                    Component_list(9201, None),
                    Component_list(866, None),
                    Component_list(632, None),
                    Component_list(112, None),
                ],
                True,
                10817,
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
                    10811,
                    [
                        Component_list(9201, 9201),
                        Component_list(866, 866),
                        Component_list(632, 632),
                        Component_list(112, 112),
                    ],
                    "T",
                ),
                "Test 2 - Totals corrected with non zero component values TCC Marker T",
            ),
            (
                "C",
                "202301",
                90,
                [
                    Component_list(90, None),
                    Component_list(0, None),
                    Component_list(4, None),
                    Component_list(6, None),
                ],
                False,
                90,
                "202301",
                None,
                None,
                0.1,
                (
                "C",
                "202301",
                    None,
                    90,
                    110,
                    90,
                    [
                        Component_list(90, 81),
                        Component_list(0, 0),
                        Component_list(4, 3.6),
                        Component_list(6, 5.4),
                    ],
                    "C",
                ),
                "Test 3 - Components corrected - TCC Marker C",
            ),
            (
                "D",
                "202312",
                1964,
                [
                    Component_list(632, None),
                    Component_list(732, None),
                    Component_list(99, None),
                    Component_list(162, None),
                ],
                True,
                1964,
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
                    1964,
                    [
                        Component_list(632, 632),
                        Component_list(732, 732),
                        Component_list(99, 99),
                        Component_list(162, 162),
                    ],
                    "M",
                ),
                "Test 4 - Manual correction required TCC Marker M ",
            ),
            (
                "F",
                "202312",
                11,
                [
                    Component_list(0, None),
                    Component_list(0, None),
                    Component_list(0, None),
                    Component_list(0, None),
                ],
                True,
                11,
                "202312",
                None,
                11,
                None,
                (
                "F",
                "202312",
                    11,
                    None,
                    None,
                    11,
                    [
                        Component_list(0, 0),
                        Component_list(0, 0),
                        Component_list(0, 0),
                        Component_list(0, 0),
                    ],
                    "S",
                ),
                "Test 5 - Totals corrected with zeros as components TCC Marker T",
            ),
            (
                "H",
                "202301",
                1625,
                [
                    Component_list("InvalidString", None),
                    Component_list(732, None),
                    Component_list(99, None),
                    Component_list(162, None),
                ],
                True,
                1625,
                "202301",
                None,
                11,
                0.1,
                "component is missing or not a number",
                "Test 6 - Invalid component value entered by user",
            ),(
                "I",
                "202301",
                1625,
                [
                    Component_list(632, None),
                    Component_list(732, None),
                    Component_list(99, None),
                    Component_list(162, None),
                ],
                True,
                "InvalidString",
                "202301",
                None,
                11,
                0.1,
                "predictive must not be a string",
                "Test 7 - Invalid predictive value entered by user",
            ),(
                "J",
                "202301",
                1625,
                [
                    Component_list(632, None),
                    Component_list(732, None),
                    Component_list(99, None),
                    Component_list(162, None),
                ],
                True,
                1625,
                "202301",
                "InvalidString",
                11,
                0.1,
                "auxiliary is missing or not a number",
                "Test 8 - Invalid auxiliary value entered by user",
            ),
            (
                "K",
                "202301",
                1625,
                [
                    Component_list(632, None),
                    Component_list(732, None),
                    Component_list(99, None),
                    Component_list(162, None),
                ],
                True,
                1625,
                "202301",
                None,
                None,
                None,
                "One or both of absolute/percentage difference thresholds must be specified and non-zero",
                "Test 9 - Absolute and percentage difference threshold None value entered by user",
            ),
            (
                "L",
                "202301",
                10817,
                [
                    Component_list(9201, None),
                    Component_list(866, None),
                    Component_list(632, None),
                    Component_list(112, None),
                ],
                True,
                None,
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
                    10811,
                    [
                        Component_list(9201, 9201),
                        Component_list(866, 866),
                        Component_list(632, 632),
                        Component_list(112, 112),
                    ],
                    "T",
                ),
                "Test 10 - Auxiliary variable replaces the missing predictive variable",
            ),
            (
                "M",
                "202301",
                10817,
                [
                    Component_list(0, None),
                    Component_list(0, None),
                    Component_list(0, None),
                    Component_list(0, None),
                ],
                True,
                0,
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
                    10817,
                    [
                        Component_list(0, 0),
                        Component_list(0, 0),
                        Component_list(0, 0),
                        Component_list(0, 0),
                    ],
                    "N",
                ),
                "Test 11 - Predictive value is 0 and component sum is zero",
            ),
            (
                "N",
                "202301",
                10817,
                [
                    Component_list(9201, None),
                    Component_list(866, None),
                    Component_list(632, None),
                    Component_list(112, None),
                ],
                True,
                10817,
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
                    10811,
                    [
                        Component_list(9201, 9201),
                        Component_list(866, 866),
                        Component_list(632, 632),
                        Component_list(112, 112),
                    ],
                    "T",
                ),
                "Test 12 - Absolute Difference Threshold only specified and satisfied",
            ),
            (
                "O",
                "202301",
                15,
                [
                    Component_list(1, None),
                    Component_list(2, None),
                    Component_list(3, None),
                    Component_list(4, None),
                ],
                True,
                5,
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
                    15,
                    [
                        Component_list(1, 1),
                        Component_list(2, 2),
                        Component_list(3, 3),
                        Component_list(4, 4),
                    ],
                    "M",
                ),
                "Test 13 - Absolute Difference Threshold only specified and not satisfied",
            ),
            (
                "P",
                "202301",
                9,
                [
                    Component_list(1, None),
                    Component_list(2, None),
                    Component_list(3, None),
                    Component_list(4, None),
                ],
                True,
                9,
                "202301",
                None,
                None,
                0.1,
                (
                "P",
                "202301",
                    None,
                    9,
                    11,
                    10,
                    [
                        Component_list(1, 1),
                        Component_list(2, 2),
                        Component_list(3, 3),
                        Component_list(4, 4),
                    ],
                    "T",
                ),
                "Test 14 - Percentage Difference Threshold only specified and satisfied",
            ),
            (
                "Q",
                "202301",
                15,
                [
                    Component_list(1, None),
                    Component_list(2, None),
                    Component_list(3, None),
                    Component_list(4, None),
                ],
                True,
                5,
                "202301",
                None,
                None,
                0.1,
                (
                "Q",
                "202301",
                    None,
                    9,
                    11,
                    15,
                    [
                        Component_list(1, 1),
                        Component_list(2, 2),
                        Component_list(3, 3),
                        Component_list(4, 4),
                    ],
                    "M",
                ),
                "Test 15 - Percentage Difference Threshold only specified and not satisfied",
            ),
            (
                "R",
                "202301",
                10817,
                [
                    Component_list(9201, None),
                    Component_list(866, None),
                    Component_list(632, None),
                    Component_list(112, None),
                ],
                True,
                10817,
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
                    10811,
                    [
                        Component_list(9201, 9201),
                        Component_list(866, 866),
                        Component_list(632, 632),
                        Component_list(112, 112),
                    ],
                    "T",
                ),
                "Test 16 - Absolute and Percentage Difference Thresholds specified and Absolute Difference Threshold satisfied",
            ),
            (
                "S",
                "202301",
                15,
                [
                    Component_list(1, None),
                    Component_list(2, None),
                    Component_list(3, None),
                    Component_list(4, None),
                ],
                False,
                9,
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
                    9,
                    [
                        Component_list(1, 0.9),
                        Component_list(2, 1.8),
                        Component_list(3, 2.7),
                        Component_list(4, 3.6),
                    ],
                    "C",
                ),
                "Test 17 - Absolute and Percentage Difference Thresholds specified and Absolute Difference Threshold not satisfied and Percentage Difference Threshold satisfied",
            ),
            (
                "U",
                "202301",
                15,
                [
                    Component_list(1, None),
                    Component_list(2, None),
                    Component_list(3, None),
                    Component_list(4, None),
                ],
                False,
                5,
                "202301",
                None,
                0,
                0,
                "One or both of absolute/percentage difference thresholds must be specified and non-zero",
                "Test 18 - Absolute and Percentage Difference Thresholds set to zero",
            ),
            (
                "T",
                "202301",
                15,
                [
                    Component_list(0, 0),
                    Component_list(0, 0),
                    Component_list(0, 0),
                    Component_list(0, 0),
                ],
                True,
                5,
                "202301",
                None,
                None,
                None,
                "One or both of absolute/percentage difference thresholds must be specified and non-zero",
                "Test 19 - Absolute and Percentage Difference Thresholds not specified",
            ),
            (
                "U",
                "202301",
                10817,
                [
                    Component_list(0, 0),
                    Component_list(0, 0),
                    Component_list(0, 0),
                    Component_list(0, 0),
                ],
                True,
                10817,
                "202301",
                None,
                11,
                None,
                (
                "U",
                "202301",
                    10817,
                    None,
                    None,
                    10817,
                [
                    Component_list(0, 0),
                    Component_list(0, 0),
                    Component_list(0, 0),
                    Component_list(0, 0),
                ],
                    "S",
                ),
                "Test 20 - Zero Case 1",
            ),
            (
                "V",
                "202301",
                10817,
                [
                    Component_list(0, 0),
                    Component_list(0, 0),
                    Component_list(0, 0),
                    Component_list(0, 0),
                ],
                False,
                10817,
                "202301",
                None,
                11,
                None,
                (
                "V",
                "202301",
                    10817,
                    None,
                    None,
                    10817,
                [
                    Component_list(0, 0),
                    Component_list(0, 0),
                    Component_list(0, 0),
                    Component_list(0, 0),
                ],
                    "S",
                ),
                "Test 21 - Zero Case 2",
            ),
            (
                
                "W",
                "202301",
                10817,
                [
                    Component_list(9201, None),
                    Component_list(866, None),
                    Component_list(632, None),
                    Component_list(112, None),
                ],
                True,
                0,
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
                    10817,
                    [
                        Component_list(9201, 9201),
                        Component_list(866, 866),
                        Component_list(632, 632),
                        Component_list(112, 112),
                    ],
                    "M",
                ),
                "Test 22 - Zero Case 3",
            ),
            (
                "X",
                "202301",
                40,
                [
                    Component_list(10, None),
                    Component_list(10, None),
                    Component_list(10, None),
                    Component_list(10, None),
                ],
                False,
                0,
                "202301",
                None,
                45,
                None,
                (
                "X",
                "202301",
                    40,
                    40,
                    40,
                    0,
                    [
                        Component_list(10, 0),
                        Component_list(10, 0),
                        Component_list(10, 0),
                        Component_list(10, 0),
                    ],
                    "C",
                ),
                "Test 23 - Zero Case 4 (where difference is within thresholds",
            ),
            (
                "Y",
                "202301",
                10817,
                [
                    Component_list(9201, None),
                    Component_list(866, None),
                    Component_list(632, None),
                    Component_list(112, None),
                ],
                False,
                0,
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
                    10817,
                    [
                        Component_list(9201, 9201),
                        Component_list(866, 866),
                        Component_list(632, 632),
                        Component_list(112, 112),
                    ],
                    "M",
                ),
                "Test 24 - Zero Case 4 (where difference are not within the threshold)",
            ),
            (
                "Z",
                "202301",
                10817,
                [
                    Component_list(2.4, None),
                    Component_list(2.6, None),
                    Component_list(2.8, None),
                    Component_list(3.1, None),
                ],
                True,
                3,
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
                    10.9,
                    [
                        Component_list(2.4, 2.4),
                        Component_list(2.6, 2.6),
                        Component_list(2.8, 2.8),
                        Component_list(3.1, 3.1),
                    ],
                    "T",
                ),
                "Test 25 - Amend True scenario with floating point components and total",
            ),
            (
                "ZA",
                "202301",
                10817,
                [
                    Component_list(2.4, None),
                    Component_list(2.6, None),
                    Component_list(2.8, None),
                    Component_list(3.1, None),
                ],
                False,
                2,
                "202301",
                None,
                11,
                None,
                (
                "ZA",
                "202301",
                    8.9,
                    None,
                    None,
                    2,
                    [
                        Component_list(2.4, 0.4403669724770642),
                        Component_list(2.6, 0.47706422018348627),
                        Component_list(2.8, 0.5137614678899082),
                        Component_list(3.1, 0.5688073394495413),
                    ],
                    "C",
                ),
                "Test 25 - Amend False scenario with floating point components and total",
            ),
            (
                "ZB",
                "202301",
                15,
                [
                    Component_list(1, None),
                    Component_list(2, None),
                    Component_list(3, None),
                    Component_list(4, None),
                ],
                True,
                7,
                "202301",
                None,
                None,
                0.1,
                (
                "ZB",
                "202301",
                    3,
                    9,
                    11,
                    15,
                    [
                        Component_list(1, 1),
                        Component_list(2, 2),
                        Component_list(3, 3),
                        Component_list(4, 4),
                    ],
                    "M",
                ),
                "Test 26 - predictive is less than lower threshold",
            ),
            (
                "ZC",
                "202301",
                15,
                [
                    Component_list(1, None),
                    Component_list(2, None),
                    Component_list(3, None),
                    Component_list(4, None),
                ],
                True,
                10.5,
                "202301",
                None,
                None,
                0.1,
                (
                "ZC",
                "202301",
                    0.5,
                    9,
                    11,
                    10,
                    [
                        Component_list(1, 1),
                        Component_list(2, 2),
                        Component_list(3, 3),
                        Component_list(4, 4),
                    ],
                    "T",
                ),
                "Test 27 - predictive is greater than lower threshold",
            ),
            (
                "ZD",
                "202301",
                15,
                [
                    Component_list(1, None),
                    Component_list(2, None),
                    Component_list(3, None),
                    Component_list(4, None),
                ],
                False,
                9,
                "202301",
                None,
                None,
                0.1,
                (
                "ZD",
                "202301",
                    1,
                    9,
                    11,
                    10,
                    [
                        Component_list(1, 0.9),
                        Component_list(2, 1.8),
                        Component_list(3, 2.7),
                        Component_list(4, 3.6),
                    ],
                    "T",
                ),
                "Test 28 - predictive is equal to lower threshold and amend value is false",
            ),
            (
                "ZE",
                "202301",
                15,
                [
                    Component_list(1, None),
                    Component_list(2, None),
                    Component_list(3, None),
                    Component_list(4, None),
                ],
                False,
                10.9,
                "202301",
                None,
                None,
                0.1,
                (
                "ZE",
                "202301",
                    0.9,
                    9,
                    11,
                    10.9,
                    [
                        Component_list(1, 1.09),
                        Component_list(2, 2.18),
                        Component_list(3, 3.27),
                        Component_list(4, 4.36),
                    ],
                    "T",
                ),
                "Test 29 - predictive is less than upper threshold",
            ),
            (
                "ZF",
                "202301",
                15,
                [
                    Component_list(1, None),
                    Component_list(2, None),
                    Component_list(3, None),
                    Component_list(4, None),
                ],
                False,
                11,
                "202301",
                None,
                None,
                0.1,
                (
                "ZF",
                "202301",
                    1,
                    9,
                    11,
                    11,
                    [
                        Component_list(1, 1.1),
                        Component_list(2, 2.2),
                        Component_list(3, 3.2),
                        Component_list(4, 4.4),
                    ],
                    "T",
                ),
                "Test 30 - predictive is equal to than upper threshold",
            ),
            (
                "ZG",
                "202301",
                15,
                [
                    Component_list(1, None),
                    Component_list(2, None),
                    Component_list(3, None),
                    Component_list(4, None),
                ],
                True,
                12,
                "202301",
                None,
                None,
                0.1,
                (
                "ZG",
                "202301",
                    2,
                    9,
                    11,
                    15,
                    [
                        Component_list(1, 1),
                        Component_list(2, 2),
                        Component_list(3, 3),
                        Component_list(4, 4),
                    ],
                    "M",
                ),
                "Test 31 - predictive is greater than upper threshold",
            ),
            (
                "ZH",
                "202312",
                "InvalidString",
                [
                    Component_list(0, None),
                    Component_list(0, None),
                    Component_list(0, None),
                    Component_list(0, None),
                ],
                True,
                11,
                "202312",
                None,
                11,
                None,
                "total is missing or not a number",
                "Test 32 - Invalid total value entered by user",
            ),
            (
                "",
                "202301",
                15,
                [
                    Component_list(1, None),
                    Component_list(2, None),
                    Component_list(3, None),
                    Component_list(4, None),
                ],
                True,
                10.9,
                "202301",
                None,
                None,
                0.1,
                (
                "",
                "202301",
                    0.9,
                    9,
                    11,
                    10,
                    [
                        Component_list(1, 1),
                        Component_list(2, 2),
                        Component_list(3, 3),
                        Component_list(4, 4),
                    ],
                    "T",
                ),
                "Test 33 - Missing identifier value",
            ),
            (
                "ZI",
                "202301",
                15,
                [
                    Component_list(1, None),
                    Component_list(2, None),
                    Component_list(3, None),
                    Component_list(4, None),
                ],
                True,
                10.9,
                "",
                None,
                None,
                0.1,
                (
                "ZI",
                "202301",
                    0.9,
                    9,
                    11,
                    10,
                    [
                        Component_list(1, 1),
                        Component_list(2, 2),
                        Component_list(3, 3),
                        Component_list(4, 4),
                    ],
                    "T",
                ),
                "Test 33 - Missing period value",
            ),
            (
                "ZJ",
                "202301",
                15,
                [
                    Component_list(1, None),
                    Component_list(2, None),
                    Component_list(3, None),
                    Component_list(4, None),
                ],
                None,
                10.9,
                "202301",
                None,
                None,
                0.1,
                "Amend total needs to be True or False",
                "Test 33 - Missing Amend total",
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
                    predictive_period=predictive_period,
                    auxiliary=auxiliary,
                    absolute_difference_threshold=absolute_difference_threshold,
                    percentage_difference_threshold=percentage_difference_threshold,
                )

                # Capture the printed output and remove any leading or trailing whitespace
                captured = capfd.readouterr()
                printed_output = captured.out.strip()
                sum_of_components  = results.final_components[0].final_value + results.final_components[1].final_value + results.final_components[2].final_value + results.final_components[3].final_value
                # this will be a for loop once jason's component list removal takes place
                
                print(printed_output)

                assert results.identifier == expected_result[0]
                assert results.period == expected_result[1]
                assert results.absolute_difference == expected_result[2]
                assert results.low_percent_threshold == expected_result[3]
                assert results.high_percent_threshold == expected_result[4]
                assert results.final_total == expected_result[5]
                assert results.final_components[0].original_value == expected_result[6][0].original_value
                assert results.final_components[0].final_value == expected_result[6][0].final_value
                assert results.final_components[1].original_value == expected_result[6][1].original_value
                assert results.final_components[1].final_value == expected_result[6][1].final_value
                assert results.final_components[2].original_value == expected_result[6][2].original_value
                assert results.final_components[2].final_value == expected_result[6][2].final_value
                assert results.final_components[3].original_value == expected_result[6][3].original_value
                assert results.final_components[3].final_value == expected_result[6][3].final_value
                # this will be a one liner once jason's component list removal takes place
                if results.tcc_marker != "M" and results.tcc_marker != "S":
                    assert sum_of_components == expected_result[5]
                assert results.tcc_marker == expected_result[7]

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
                    predictive_period=predictive_period,
                    auxiliary=auxiliary,
                    absolute_difference_threshold=absolute_difference_threshold,
                    percentage_difference_threshold=percentage_difference_threshold,
                )
                print(str(exc_info.value))
            assert str(exc_info.value) == expected_result
