import random

import pytest

from sml_small.totals_and_components.totals_and_components import (Component_list, check_absolute_difference_threshold,
                                                                   check_percentage_difference_threshold,
                                                                   check_predictive_value,
                                                                   check_sum_components_predictive, check_zero_errors,
                                                                   correct_components, correct_total,
                                                                   determine_error_detection, error_correction,
                                                                   sum_components, totals_and_components,
                                                                   validate_input)

EXCEPTION_FAIL_MESSAGE = "{test_id} : Expected no exception, but got {exception_type}: {exception_msg}"


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
                [1, 2, 3, 4],
                101.0,
                102.0,
                "202312",
                300.0,
                20,
                0.1,
                (100, [1, 2, 3, 4], 102.0, 300.0, 20, 0.1),
                "Test 1: Correct values test",
            ),
            (
                "A",
                "202312",
                100.0,
                [1, 2, 3, 4],
                102.0,
                103.0,
                "202312",
                104.0,
                105.0,
                None,
                (100.0, [1, 2, 3, 4], 103.0, 104.0, 105.0, None),
                "Test 2: None value for percentage difference threshold",
            ),
            (
                "A",
                "202312",
                100.0,
                [1, 2, 3, 4],
                102.0,
                103.0,
                "202312",
                104.0,
                None,
                20,
                (100.0, [1, 2, 3, 4], 103.0, 104.0, None, 20),
                "Test 3: None value for absolute difference threshold",
            ),(
                "A",
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
                "Test 4: Empty component list",
            ),
            (
                "A",
                "202312",
                100.0,
                [None,2 ,3, 4],
                101.0,
                102.0,
                "202312",
                103.0,
                20,
                0.1,
                ValueError,
                "Test 5: None in component list",
            ),
            (
                "A",
                "202312",
                "String",
                [1, 2, 3, 4],
                102.0,
                103.0,
                "202312",
                104.0,
                20,
                0.1,
                ValueError,
                "Test 6: Invalid Total",
            ),
            (
                "A",
                "202312",
                100.0,
                [1, 2, 3, 4],
                101.0,
                "String",
                "202312",
                102.0,
                20,
                0.1,
                ValueError,
                "Test 7: Invalid predictive test",
            ),
            (
                "A",
                "202312",
                100.0,
                [1, 2, 3, 4],
                101.0,
                102.0,
                "202312",
                "String",
                20,
                0.1,
                ValueError,
                "Test 8: Invalid auxiliary",
            ),
            (
                "A",
                "202312",
                100.0,
                [1, 2, 3, 4],
                102.0,
                103.0,
                "202312",
                104.0,
                {20},
                0.1,
                ValueError,
                "Test 9: Invalid absolute difference threshold",
            ),
            (
                "A",
                "202312",
                100.0,
                [1, 2, 3, 4],
                102.0,
                103.0,
                "202312",
                104.0,
                20,
                {2},
                ValueError,
                "Test 10: Invalid percentage difference threshold",
            ),
            (
                "A",
                "202312",
                100.0,
                [1, 2, 3, 4],
                102.0,
                101.0,
                "202312",
                89.0,
                None,   
                None,
                ValueError,
                "Test 11: None value for percentage and absolute difference threshold",
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
        test_id
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
                pytest.fail(EXCEPTION_FAIL_MESSAGE.format(test_id=test_id, exception_type=type(e).__name__,
                                                          exception_msg=str(e)))
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
            (100.0, None, (100.0, None), "Test 1: Predictive Only"),
            (None, 50.0, (50.0, None), "Test 2: Auxiliary Only"),
            (None, None, (None, 'S'), "Test 3: No Inputs"),
            (150.0, 50.0, (150.0, None), "Test 4: All Inputs"),
            (0, 0, (0, None), "Test 5: All 0")
        ],
    )
    def test_check_predictive_value(self, predictive, auxiliary, expected_result, test_id):
        try:
            result = check_predictive_value(predictive=predictive, auxiliary=auxiliary)
            print(result)
            assert result == expected_result, f"Test {test_id} failed: Unexpected result"
        except Exception as e:
            pytest.fail(EXCEPTION_FAIL_MESSAGE.format(test_id=test_id, exception_type=type(e).__name__,
                                                      exception_msg=str(e)))


class TestCheckZeroErrors:
    @pytest.mark.parametrize(
        "test_components, predictive, expected_result, test_id",
        [
            ([], 100.0, True, "Test 1: 12 RandomComponents, predictive positive"),
            ([Component_list(original_value=0, final_value=None), Component_list(original_value=0, final_value=None)],
             150.0, False, "Test 2: Components 0, predictive positive")
        ],
    )
    def test_check_zero_errors(self, test_components, predictive, expected_result, test_id):
        if "RandomComponents" in test_id:
            for _ in range(12):
                random_float = random.uniform(0, 12)
                component = Component_list(original_value=random_float, final_value=None)
                test_components.append(component)

        try:
            components_sum = sum_components(test_components)
            check_zero_errors(predictive=predictive, components_sum=components_sum)

        except Exception as e:
            pytest.fail(EXCEPTION_FAIL_MESSAGE.format(test_id=test_id, exception_type=type(e).__name__,
                                                      exception_msg=str(e)))


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
                True,
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
                False,
                "Test 2: Component Sum Does NOT Match Predictive",
            ),
        ],
    )
    def test_check_sum_components_predictive(
        self, test_components, predictive, expected_result, test_id
    ):
        try:

            components_sum = sum_components(test_components)
            check_sum_components_predictive(
                predictive=predictive, components_sum=components_sum
            )
            assert expected_result

        except Exception as e:
            pytest.fail(EXCEPTION_FAIL_MESSAGE.format(test_id=test_id, exception_type=type(e).__name__,
                                                      exception_msg=str(e)))


class TestDetermineErrorDetection:
    @pytest.mark.parametrize(
        "absolute_difference_threshold, percentage_difference_threshold, absolute_difference, components_sum,"
        "expected_result, test_id",
        [
            (20, None, 10, 100, True, "Test 1: Absolute Difference Only - Satisfied"),
            (5, None, 10, 100, False, "Test 2: Absolute Difference Only - NOT Satisfied"),
        ]
    )
    def test_determine_error_detection(
        self,
        absolute_difference_threshold,
        percentage_difference_threshold,
        absolute_difference,
        components_sum,
        expected_result,
        test_id,
    ):
        try:
            result = determine_error_detection(
                absolute_difference_threshold=absolute_difference_threshold,
                percentage_difference_threshold=percentage_difference_threshold,
                absolute_difference=absolute_difference,
                components_sum=components_sum,
            )

            assert result == expected_result, f"Test failed: {test_id}"
        except Exception as e:
            pytest.fail(EXCEPTION_FAIL_MESSAGE.format(test_id=test_id, exception_type=type(e).__name__,
                                                      exception_msg=str(e)))


class TestCheckAbsoluteDifferenceThreshold:
    @pytest.mark.parametrize(
        "absolute_difference_threshold, absolute_difference, expected_result, test_id",
        [
            (9, 10, True, "Case 1: Absolute difference is greater than threshold"),
            (10, 10, True, "Case 2: Absolute difference equals threshold"),
            (11, 10, False, "Case 3: Absolute difference is less than threshhold"),
        ]
    )
    def test_check_absolute_difference_threshold(
        self,
        absolute_difference_threshold,
        absolute_difference,
        expected_result,
        test_id
    ):
        try:
            result = check_absolute_difference_threshold(
                absolute_difference_threshold=absolute_difference_threshold,
                absolute_difference=absolute_difference
            )

            assert result == expected_result, f"Test failed: {test_id}"
        except Exception as e:
            pytest.fail(EXCEPTION_FAIL_MESSAGE.format(test_id=test_id, exception_type=type(e).__name__,
                                                      exception_msg=str(e)))


class TestCheckPercentageDifferenceThreshold:
    @pytest.mark.parametrize(
        "percentage_difference_threshold, components_sum, predictive, expected_result, test_id",
        [
            (0.1, 100.0, 110.0, True, "Test 1: Predictive total equals upper threshold"),
            (0.1, 100.0, 120.0, False, "Test 2: Predictive total is greater than upper threshold"),
            (0.2, 100.0, 110.0, True,
             "Test 3: Predictive total is less than upper threshold and greater than lower threshold"),
            (0.2, 100.0, 79.5, False, "Test 4: Predictive total is less than lower threshold"),
        ],
    )
    def test_check_percentage_difference_threshold(
        self, percentage_difference_threshold, components_sum, predictive, expected_result, test_id
    ):
        try:
            result = check_percentage_difference_threshold(
                percentage_difference_threshold, components_sum, predictive
            )
            assert result == expected_result, f"{test_id} - Unexpected result"

        except Exception as e:
            pytest.fail(EXCEPTION_FAIL_MESSAGE.format(test_id=test_id, exception_type=type(e).__name__,
                                                      exception_msg=str(e)))


class TestErrorCorrection:
    @pytest.mark.parametrize(
        "amend_total, components_sum, original_components, predictive, expected_result, test_id",
        [
            (True, 100.0, [Component_list(10.0, None)] * 10, 82.0, True, "Test 1: Amend total"),
            (False, 100.0, [Component_list(10.0, None)] * 10, 82.0, False, "Test 2: Amend components"),
        ],
    )
    def test_error_correction(
        self, amend_total, components_sum, original_components, predictive, expected_result, test_id
    ):
        try:
            result = error_correction(amend_total, components_sum, original_components, predictive)
            assert result == expected_result, f"{test_id} - Unexpected result"

        except Exception as e:
            pytest.fail(EXCEPTION_FAIL_MESSAGE.format(test_id=test_id, exception_type=type(e).__name__,
                                                      exception_msg=str(e)))


class TestCorrectTotal:
    @pytest.mark.parametrize(
            "components_sum, original_components, expected_result, test_id",
            [
                (100.0, [Component_list(10.0, None)] * 10, 100.0, "Test 1: Final total is sum of received components"),
            ],
    )
    def test_correct_total(self, components_sum, original_components, expected_result, test_id):
        try:
            correct_total(components_sum=components_sum, original_components=original_components)
            assert components_sum == expected_result, f"Test {test_id} failed: Unexpected result"
        except Exception as e:
            pytest.fail(EXCEPTION_FAIL_MESSAGE.format(test_id=test_id, exception_type=type(e).__name__,
                                                      exception_msg=str(e)))


class TestCorrectComponents:
    @pytest.mark.parametrize(
            "components_sum, original_components, predictive, expected_result, test_id",
            [
                (90.0, [Component_list(9.0, None)] * 10, 100.0, 100.0, "Test 1: Component sum matches total"),
            ])
    def test_correct_components(self, components_sum, original_components, predictive, expected_result, test_id):
        try:
            result = correct_components(components_sum=components_sum,
                                        original_components=original_components,
                                        predictive=predictive)

            assert result == expected_result, f"Test {test_id} failed: Unexpected result"
        except Exception as e:
            pytest.fail(EXCEPTION_FAIL_MESSAGE.format(test_id=test_id, exception_type=type(e).__name__,
                                                      exception_msg=str(e)))


class TestTotalsAndComponents:
    @pytest.mark.parametrize(
            "identifier, period, total, components, amend_total, predictive, predictive_period, auxiliary,"
            "absolute_difference_threshold, percentage_difference_threshold, expected_result, test_id",
            [
                ("A", "202312", 100.0, [Component_list(random.uniform(0, 12), None) for _ in range(12)], True, 100.0,
                 "202312", None, 20, 0.1, "T", "Test 1: TCC Marker T"),
            ])
    def test_totals_and_components(self, capfd, identifier, period, total, components, amend_total, predictive,
                                   predictive_period, auxiliary, absolute_difference_threshold,
                                   percentage_difference_threshold, expected_result, test_id):
        try:
            results = totals_and_components(identifier=identifier,
                                            period=period,
                                            total=total,
                                            components=components,
                                            amend_total=amend_total,
                                            predictive=predictive,
                                            predictive_period=predictive_period,
                                            auxiliary=auxiliary,
                                            absolute_difference_threshold=absolute_difference_threshold,
                                            percentage_difference_threshold=percentage_difference_threshold)

            # Capture the printed output and remove any leading or trailing whitespace
            captured = capfd.readouterr()
            printed_output = captured.out.strip()
            print(printed_output)

            assert results.tcc_marker == expected_result, f"Test {test_id} failed: Unexpected result"
        except Exception as e:
            pytest.fail(EXCEPTION_FAIL_MESSAGE.format(test_id=test_id, exception_type=type(e).__name__,
                                                      exception_msg=str(e)))
