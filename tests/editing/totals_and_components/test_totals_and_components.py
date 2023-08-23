import random
from decimal import Decimal, getcontext

import pytest

from sml_small.editing.totals_and_components.totals_and_components import (PRECISION_MAX, PRECISION_MIN, ComponentPair,
                                                                           TACException, TccMarker,
                                                                           check_absolute_difference_threshold,
                                                                           check_percentage_difference_threshold,
                                                                           check_sum_components_predictive,
                                                                           check_zero_errors, correct_components,
                                                                           correct_total, determine_error_detection,
                                                                           error_correction, set_predictive_value,
                                                                           sum_components, totals_and_components,
                                                                           validate_input)
from sml_small.utils.error_utils import (get_mandatory_param_error, get_one_of_params_mandatory_error,
                                         get_param_outside_range_error, get_params_is_not_a_number_error)

# ---- Constant Definitions ----
EXCEPTION_FAIL_MESSAGE = "{test_id} : Expected no exception, but got {exception_type}: {exception_msg}"


# ---- Class Defnitions ----

#  Class used to force str() cast during validation to fail as all standard library python types have
#  valid string conversions
class NoString:
    def __str__(self):
        pass


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
                None,
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
                    "identifier: H",
                    ValueError(
                        get_params_is_not_a_number_error("component=InvalidString")
                    ),
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
                    "identifier: I",
                    ValueError(get_params_is_not_a_number_error("predictive")),
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
                    "identifier: J",
                    ValueError(get_params_is_not_a_number_error("auxiliary")),
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
                    "identifier: K",
                    ValueError(
                        get_one_of_params_mandatory_error(
                            [
                                "absolute_difference_threshold",
                                "percentage_difference_threshold",
                            ]
                        )
                    ),
                ),
                # An invalid absolute difference threshold or PDT is passed to the method which is not allowed
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
                # Test checking absolute difference threshold passes to totals correction and corrects the total
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
                # Test checking absolute difference threshold fails to totals correction and returns M tcc marker
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
                "Test 17 - absolute difference threshold and PDT specified and absolute difference threshold satisfied",
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
                "Test 18 - absolute difference threshold and PDT specified and absolute difference threshold not satisfied and PDT satisfied",  # noqa: E501
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
                    10.0,
                    10.0,
                    5,
                    [1, 2, 3, 4],
                    "M",
                ),
                "Test 19 - Absolute and Percentage Difference Thresholds set to zero",
                # Test checking for a error exception thrown when we provide
                # zero values for absolute difference threshold and PDT this is caught in validate input
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
                    "identifier: T",
                    ValueError(
                        get_one_of_params_mandatory_error(
                            [
                                "absolute_difference_threshold",
                                "percentage_difference_threshold",
                            ]
                        )
                    ),
                ),
                "Test 20 - Absolute and Percentage Difference Thresholds not specified",
                # Test checking for a error exception thrown when we provide
                # zero values for absolute difference threshold or PDT this is caught in validate input
            ),
            (
                "UAT-ZERO-CHECK-1",
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
                    "UAT-ZERO-CHECK-1",
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
                "UAT-ZERO-CHECK-2",
                9,
                [(0), (0), (0), (0)],
                False,
                9,
                1,
                None,
                11,
                None,
                (
                    "UAT-ZERO-CHECK-2",
                    None,
                    None,
                    None,
                    9,
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
                "UAT-ZERO-CHECK-3",
                0,
                [
                    (7),
                    (0),
                    (2),
                    (2),
                ],
                True,
                0,
                28,
                None,
                11,
                None,
                (
                    "UAT-ZERO-CHECK-3",
                    11,
                    None,
                    None,
                    11,
                    [7, 0, 2, 2],
                    "T",
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
                "UAT-ZERO-CHECK-3-B",
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
                    "UAT-ZERO-CHECK-3-B",
                    10811,
                    None,
                    None,
                    0,
                    [9201, 866, 632, 112],
                    "M",
                ),
                "Test 23-b - Zero Case 3",
                # If target total = 0 and components sum > 0
                # and amend total = TRUE: The total should be
                # corrected if the difference observed is
                # within the tolerances determined by the
                # detection method. Else, the difference
                # should be flagged for manual checking.
            ),
            (
                "UAT-ZERO-CHECK-4",
                0,
                [(7), (0), (2), (2)],
                False,
                0,
                28,
                None,
                11,
                None,
                (
                    "UAT-ZERO-CHECK-4",
                    11,
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
                "UAT-ZERO-CHECK-4-B",
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
                    "UAT-ZERO-CHECK-4-B",
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
                        0.440366972477064220183486238532,
                        0.477064220183486238532110091743,
                        0.513761467889908256880733944954,
                        0.568807339449541284403669724770,
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
                    "C",
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
                    "C",
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
                    "identifier: AH",
                    ValueError(get_params_is_not_a_number_error("total")),
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
                    "identifier: N/A",
                    ValueError(get_mandatory_param_error("identifier")),
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
                    "identifier: AJ",
                    ValueError(get_mandatory_param_error("amend_total")),
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
                        2.201834862385321100917431192660,
                        2.385321100917431192660550458715,
                        2.568807339449541284403669724770,
                        2.844036697247706422018348623853,
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
                    "identifier: AM",
                    ValueError(
                        get_param_outside_range_error(
                            "precision",
                            [
                                str(PRECISION_MIN),
                                str(PRECISION_MAX),
                            ],
                        )
                    ),
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
                    "identifier: AN",
                    ValueError(
                        get_param_outside_range_error(
                            "precision",
                            [
                                str(PRECISION_MIN),
                                str(PRECISION_MAX),
                            ],
                        )
                    ),
                ),
                "Test 40 - Testing precision value = 0",
                # Testing the accuracy of the components returned
                # when the entered precision value is equal to 0
            ),
            (
                "AO",
                0.6,
                [
                    (0.1),
                    (0.2),
                    (0.4),
                ],
                True,
                0.6,
                2,
                None,
                11,
                None,
                (
                    "AO",
                    0.1,
                    None,
                    None,
                    0.7,
                    [0.1, 0.2, 0.4],
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
                    "identifier: AS", ValueError(get_mandatory_param_error("total"))
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
                    90,
                    [81, 0, 3.6, 5.4],
                    "C",
                ),
                "Test 49 - test when components are string values",
                # When components are strings, we would expect
                # the method to still work
            ),
            (
                "AX",
                9,
                [
                    (0),
                    (0),
                    (0),
                    (0),
                ],
                True,
                9,
                1,
                None,
                11,
                None,
                (
                    "AX",
                    None,
                    None,
                    None,
                    9,
                    [0, 0, 0, 0],
                    "S",
                ),
                "Test 50 - absolute difference <= absolute difference threshold and component sum is 0 and amend total is true",  # noqa: E501
                # If the absolute difference is less than or equal to
                # the absolute difference threshold and > 0, the component sum
                # is 0 and the amend total is true then the method stops
            ),
            (
                "AY",
                8,
                [],
                True,
                8,
                2,
                None,
                11,
                None,
                (
                    "AY",
                    None,
                    None,
                    None,
                    8,
                    [],
                    "S",
                ),
                "Test 51 - absolute difference <= absolute difference threshold and component sum is missing and amend total is true",  # noqa: E501
                # If the absolute difference is less than or equal to
                # the absolute difference threshold and > 0, the component sum
                # is missing and the amend total is true then the method stops
            ),
            (
                "AZ",
                10,
                [
                    (0),
                    (0),
                    (0),
                    (0),
                ],
                False,
                10,
                4,
                None,
                11,
                None,
                (
                    "AZ",
                    None,
                    None,
                    None,
                    10,
                    [0, 0, 0, 0],
                    "S",
                ),
                "Test 52 - absolute difference <= absolute difference threshold and component sum is 0 and amend total is false",  # noqa: E501
                # If the absolute difference is less than or equal to
                # the absolute difference threshold and > 0, the component sum
                # is 0 and the amend total is false then the method stops
            ),
            (
                "BA",
                6,
                [],
                False,
                6,
                2,
                None,
                11,
                None,
                (
                    "BA",
                    None,
                    None,
                    None,
                    6,
                    [],
                    "S",
                ),
                "Test 53 - absolute difference <= absolute difference threshold and component sum is missing and amend total is false",  # noqa: E501
                # If the absolute difference is less than or equal to
                # the absolute difference threshold and > 0, the component sum
                # is missing and the amend total is false then the method stops
            ),
            (
                "BB",
                6,
                [
                    (0),
                    (0),
                    (0),
                    (0),
                ],
                True,
                6,
                1,
                None,
                None,
                0.1,
                (
                    "BB",
                    None,
                    None,
                    None,
                    6,
                    [0, 0, 0, 0],
                    "S",
                ),
                "Test 54 - percentage difference > 0 and component sum is 0 and amend total is true",
                # If the percentage difference is greater than 0, the component sum
                # is 0 and the amend total is true then the method stops
            ),
            (
                "BC",
                9,
                [],
                True,
                9,
                1,
                None,
                None,
                0.1,
                (
                    "BC",
                    None,
                    None,
                    None,
                    9,
                    [],
                    "S",
                ),
                "Test 55 - percentage difference > 0 and component sum is missing and amend total is true",
                # If the percentage difference is greater than 0, the component sum
                # is missing and the amend total is true then the method stops
            ),
            (
                "BD",
                6,
                [
                    (0),
                    (0),
                    (0),
                    (0),
                ],
                False,
                6,
                1,
                None,
                None,
                0.1,
                (
                    "BD",
                    None,
                    None,
                    None,
                    6,
                    [0, 0, 0, 0],
                    "S",
                ),
                "Test 56 - percentage difference > 0 and component sum is 0 and amend total is false",
                # If the percentage difference is greater than 0, the component sum
                # is 0 and the amend total is false then the method stops
            ),
            (
                "BE",
                9,
                [],
                False,
                None,
                1,
                9,
                None,
                0.1,
                (
                    "BE",
                    None,
                    None,
                    None,
                    9,
                    [],
                    "S",
                ),
                "Test 57 - percentage difference > 0 and component sum is missing and amend total is false",
                # If the percentage difference is greater than 0, the component sum
                # is missing and the amend total is false then the method stops
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
                assert results.tcc_marker == expected_result[6]

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

class TestsTotalsAndComponentsUAT:
    @pytest.mark.parametrize(
        "identifier, total, components, amend_total, predictive, precision,"
        "auxiliary, absolute_difference_threshold, percentage_difference_threshold,"
        "expected_result, test_id",
        [
            (
                "UAT-ABD-DIFF-1001",
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
                    "UAT-ABD-DIFF-1001",
                    0,
                    None,
                    None,
                    1625,
                    [632, 732, 99, 162],
                    "N",
                ),
                "Test 1 - If absolute difference = 0 then no correction is applied",
                # Sheet TCC_test_data_case_a1 reference 1001
                # If absolute difference = 0, then no correction is applied.
                # TCC = N
            ),
            (
                "UAT-ABD-DIFF-1002",
                10811,
                [
                    (9201),
                    (866),
                    (632),
                    (112),
                ],
                True,
                10811,
                28,
                None,
                11,
                None,
                (
                    "UAT-ABD-DIFF-1002",
                    0,
                    None,
                    None,
                    10811,
                    [9201, 866, 632, 112],
                    "N",
                ),
                "Test 2 - If absolute difference = 0 then no correction is applied",
                # Sheet TCC_test_data_case_a1 reference 1002
                # If absolute difference = 0, then no correction is applied.
                # TCC = N
            ),
            (
                "UAT-ABD-DIFF-1003",
                108,
                [
                    (98),
                    (0),
                    (4),
                    (6),
                ],
                True,
                108,
                28,
                None,
                11,
                None,
                (
                    "UAT-ABD-DIFF-1003",
                    0,
                    None,
                    None,
                    108,
                    [98, 0, 4, 6],
                    "N",
                ),
                "Test 3 - If absolute difference = 0 then no correction is applied",
                # Sheet TCC_test_data_case_a1 reference 1003
                # If absolute difference = 0, then no correction is applied.
                # TCC = N
            ),
            (
                "UAT-ABD-DIFF-2001",
                1603,
                [
                    (632),
                    (732),
                    (99),
                    (162),
                ],
                True,
                1603,
                28,
                None,
                11,
                None,
                (
                    "UAT-ABD-DIFF-2001",
                    22,
                    None,
                    None,
                    1603,
                    [632, 732, 99, 162],
                    "M",
                ),
                "Test 4 - If absolute difference > 11 then manual editing is required",
                # Sheet TCC_test_data_case_a2 reference 2001
                # If absolute difference > absolute difference threshold,
                # then no correction is applied, and marker
                # shows manual editing required. TCC = M
            ),
            (
                "UAT-ABD-DIFF-2002",
                10745,
                [
                    (9201),
                    (866),
                    (632),
                    (112),
                ],
                True,
                10745,
                28,
                None,
                11,
                None,
                (
                    "UAT-ABD-DIFF-2002",
                    66,
                    None,
                    None,
                    10745,
                    [9201, 866, 632, 112],
                    "M",
                ),
                "Test 5 - If absolute difference > 11 then manual editing is required",
                # Sheet TCC_test_data_case_a2 reference 2002
                # If absolute difference > absolute difference threshold,
                # then no correction is applied, and marker
                # shows manual editing required. TCC = M
            ),
            (
                "UAT-ABD-DIFF-2003",
                153,
                [
                    (98),
                    (0),
                    (4),
                    (6),
                ],
                True,
                153,
                28,
                None,
                11,
                None,
                (
                    "UAT-ABD-DIFF-2003",
                    45,
                    None,
                    None,
                    153,
                    [98, 0, 4, 6],
                    "M",
                ),
                "Test 6 - If absolute difference > 11 then manual editing is required",
                # Sheet TCC_test_data_case_a2 reference 2003
                # If absolute difference > absolute difference threshold,
                # then no correction is applied, and marker
                # shows manual editing required. TCC = M
            ),
            (
                "UAT-ABD-DIFF-3001",
                1614,
                [
                    (632),
                    (732),
                    (99),
                    (162),
                ],
                True,
                1614,
                28,
                None,
                11,
                None,
                (
                    "UAT-ABD-DIFF-3001",
                    11,
                    None,
                    None,
                    1625,
                    [632, 732, 99, 162],
                    "T",
                ),
                "Test 7 - If absolute difference = 11 and amend total is true then we correct the total",
                # Sheet TCC_test_data_case_a3 reference 3003
                # If absolute difference = absolute difference threshold and amend
                # total = TRUE, then correction is applied
                # and total corrected. TCC = T
            ),
            (
                "UAT-ABD-DIFF-3002",
                10822,
                [
                    (9201),
                    (866),
                    (632),
                    (112),
                ],
                True,
                10822,
                28,
                None,
                11,
                None,
                (
                    "UAT-ABD-DIFF-3002",
                    11,
                    None,
                    None,
                    10811,
                    [9201, 866, 632, 112],
                    "T",
                ),
                "Test 8 - If absolute difference = 11 and amend total is true then we correct the total",
                # Sheet TCC_test_data_case_a3 reference 3002
                # If absolute difference = absolute difference threshold and amend
                # total = TRUE, then correction is applied
                # and total corrected. TCC = T
            ),
            (
                "UAT-ABD-DIFF-3003",
                119,
                [
                    (98),
                    (0),
                    (4),
                    (6),
                ],
                True,
                119,
                28,
                None,
                11,
                None,
                (
                    "UAT-ABD-DIFF-3003",
                    11,
                    None,
                    None,
                    108,
                    [98, 0, 4, 6],
                    "T",
                ),
                "Test 9 - If absolute difference = 11 and amend total is true then we correct the total",
                # Sheet TCC_test_data_case_a3 reference 3003
                # If absolute difference = absolute difference threshold and amend
                # total = TRUE, then correction is applied
                # and total corrected. TCC = T
            ),
            (
                "UAT-ABD-DIFF-4001",
                1614,
                [
                    (632),
                    (732),
                    (99),
                    (162),
                ],
                False,
                1614,
                28,
                None,
                11,
                None,
                (
                    "UAT-ABD-DIFF-4001",
                    11,
                    None,
                    None,
                    1614,
                    [627.7218461538462, 727.044923076923, 98.32984615384615, 160.90338461538462],
                    "C",
                ),
                "Test 10 - If absolute difference = 11 and amend total is false then we correct the components",
                # Sheet TCC_test_data_case_a4 reference 4001
                # If absolute difference = absolute difference threshold and amend total = FALSE,
                # then correction is applied, and components
                # rescaled. TCC = C
            ),
            (
                "UAT-ABD-DIFF-4002",
                10822,
                [
                    (9201),
                    (866),
                    (632),
                    (112),
                ],
                False,
                10822,
                28,
                None,
                11,
                None,
                (
                    "UAT-ABD-DIFF-4002",
                    11,
                    None,
                    None,
                    10822,
                    [9210.36185366756, 866.8811395800574, 632.643048746647, 112.1139580057349],
                    "C",
                ),
                "Test 11 - If absolute difference = 11 and amend total is false then we correct the components",
                # Sheet TCC_test_data_case_a4 reference 4002
                # If absolute difference = absolute difference threshold and amend total = FALSE,
                # then correction is applied, and components
                # rescaled. TCC = C
            ),
            (
                "UAT-ABD-DIFF-4003",
                119,
                [
                    (98),
                    (0),
                    (4),
                    (6),
                ],
                False,
                119,
                28,
                None,
                11,
                None,
                (
                    "UAT-ABD-DIFF-4003",
                    11,
                    None,
                    None,
                    119,
                    [107.98148148148148, 0, 4.407407407407407, 6.611111111111111],
                    "C",
                ),
                "Test 12 - If absolute difference = 11 and amend total is false then we correct the components",
                # Sheet TCC_test_data_case_a4 reference 4003
                # If absolute difference = absolute difference threshold and amend total = FALSE,
                # then correction is applied, and components
                # rescaled. TCC = C
            ),
            (
                "UAT-ABD-DIFF-5001",
                1621,
                [
                    (632),
                    (732),
                    (99),
                    (162),
                ],
                True,
                1621,
                28,
                None,
                11,
                None,
                (
                    "UAT-ABD-DIFF-5001",
                    4,
                    None,
                    None,
                    1625,
                    [632, 732, 99, 162],
                    "T",
                ),
                "Test 13 - If absolute difference < 11 and amend total is true then we correct the components",
                # Sheet TCC_test_data_case_a5 reference 5001
                # If absolute difference < absolute difference threshold and amend total = TRUE,
                # then correction applied and total corrected.
                # TCC = T
            ),
            (
                "UAT-ABD-DIFF-5002",
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
                    "UAT-ABD-DIFF-5002",
                    6,
                    None,
                    None,
                    10811,
                    [9201, 866, 632, 112],
                    "T",
                ),
                "Test 14 - If absolute difference < 11 and amend total is true then we correct the components",
                # Sheet TCC_test_data_case_a5 reference 5002
                # If absolute difference < absolute difference threshold and amend total = TRUE,
                # then correction applied and total corrected.
                # TCC = T
            ),
            (
                "UAT-ABD-DIFF-5003",
                103,
                [
                    (98),
                    (0),
                    (4),
                    (6),
                ],
                True,
                103,
                28,
                None,
                11,
                None,
                (
                    "UAT-ABD-DIFF-5003",
                    5,
                    None,
                    None,
                    108,
                    [98, 0, 4, 6],
                    "T",
                ),
                "Test 15 - If absolute difference < 11 and amend total is true then we correct the components",
                # Sheet TCC_test_data_case_a5 reference 5003
                # If absolute difference < absolute difference threshold and amend total = TRUE,
                # then correction applied and total corrected.
                # TCC = T
            ),
            (
                "UAT-ABD-DIFF-6001",
                1621,
                [
                    (632),
                    (732),
                    (99),
                    (162),
                ],
                False,
                1621,
                28,
                None,
                11,
                None,
                (
                    "UAT-ABD-DIFF-6001",
                    4,
                    None,
                    None,
                    1621,
                    [
                        630.4443076923077, 730.1981538461539, 98.75630769230769, 161.60123076923077
                    ],
                    "C",
                ),
                "Test 63 - If absolute difference < 11 and amend total is false then we correct the components",
                # Sheet TCC_test_data_case_a6 reference 6001
                # If absolute difference < absolute difference threshold and amend total = FALSE,
                # then correction applied, and
                # components rescaled. TCC = C
            ),
            # (
            #     "UAT-ABD-DIFF-6002",
            #     10817,
            #     [
            #         (9201),
            #         (866),
            #         (632),
            #         (112),
            #     ],
            #     False,
            #     10817,
            #     28,
            #     None,
            #     11,
            #     None,
            #     (
            #         "UAT-ABD-DIFF-6002",
            #         6,
            #         None,
            #         None,
            #         10817,
            #         [
            #             9206.10646563685, 866.4806215891222, 632.3507538618074, 112.06215891221903
            #         ],
            #         "C",
            #     ),
            #     "Test 17 - If absolute difference < 11 and amend total is false then we correct the components",
            #     # Sheet TCC_test_data_case_a6 reference 6002
            #     # If absolute difference < absolute difference threshold and amend total = FALSE,
            #     # then correction applied, and
            #     # components rescaled. TCC = C
            # ),
            (
                "UAT-ABD-DIFF-6003",
                103,
                [
                    (98),
                    (0),
                    (4),
                    (6),
                ],
                False,
                103,
                28,
                None,
                11,
                None,
                (
                    "UAT-ABD-DIFF-6003",
                    5,
                    None,
                    None,
                    103,
                    [
                        93.46296296296296,
                        0,
                        3.814814814814815,
                        5.722222222222222
                    ],
                    "C",
                ),
                "Test 18 - If absolute difference < 11 and amend total is false then we correct the components",
                # Sheet TCC_test_data_case_a6 reference 6003
                # If absolute difference < absolute difference threshold and amend total = FALSE,
                # then correction applied, and
                # components rescaled. TCC = C
            ),
            (
                "UAT-ABD-DIFF-7001",
                9,
                [
                    (0),
                    (0),
                    (0),
                    (0),
                ],
                True,
                9,
                28,
                None,
                11,
                None,
                (
                    "UAT-ABD-DIFF-7001",
                    None,
                    None,
                    None,
                    9,
                    [0, 0, 0, 0],
                    "S",
                ),
                "Test 19 - If absolute difference < 11 and amend total is true then we correct the components",
                # Sheet TCC_test_data_case_a7 reference 7001
                # If absolute difference <= absolute difference threshold and > 0 but components sum = 0 or missing,
                # and amend total = TRUE, then do not amend total.
                # TCC marker = S
            ),
            # (
            #     "UAT-ABD-DIFF-7002",
            #     4,
            #     [
            #         (),
            #         (),
            #         (),
            #         (),
            #     ],
            #     True,
            #     4,
            #     28,
            #     None,
            #     11,
            #     None,
            #     (
            #         "UAT-ABD-DIFF-7002",
            #         None,
            #         None,
            #         None,
            #         4,
            #         [0, 0, 0, 0],
            #         "S",
            #     ),
            #     "Test 20 - If absolute difference < 11 and amend total is true then we correct the components",
            #     # Sheet TCC_test_data_case_a7 reference 7002
            #     # If absolute difference <= absolute difference threshold and > 0 but components sum = 0 or missing,
            #     # and amend total = TRUE, then do not amend total.
            #     # TCC marker = S
            # ),
            (
                "UAT-ABD-DIFF-7003",
                11,
                [
                    (0),
                    (0),
                    (0),
                    (0),
                ],
                True,
                11,
                28,
                None,
                11,
                None,
                (
                    "UAT-ABD-DIFF-7003",
                    None,
                    None,
                    None,
                    11,
                    [0, 0, 0, 0],
                    "S",
                ),
                "Test 21 - If absolute difference < 11 and amend total is true then we correct the components",
                # Sheet TCC_test_data_case_a7 reference 7003
                # If absolute difference <= absolute difference threshold and > 0 but components sum = 0 or missing,
                # and amend total = TRUE, then do not amend total.
                # TCC marker = S
            ),
            (
                "UAT-ABD-DIFF-8001",
                9,
                [
                    (0),
                    (0),
                    (0),
                    (0),
                ],
                False,
                9,
                28,
                None,
                11,
                None,
                (
                    "UAT-ABD-DIFF-8001",
                    None,
                    None,
                    None,
                    9,
                    [0, 0, 0, 0],
                    "S",
                ),
                "Test 22 - If absolute difference < 11 and amend total is false then we correct the components",
                # Sheet TCC_test_data_case_a8 reference 8001
                # If absolute difference <= absolute difference threshold and > 0 but components sum = 0 or missing,
                # and amend total = False, then do not amend total.
                # TCC marker = S
            ),
            # (
            #     "UAT-ABD-DIFF-8002",
            #     4,
            #     [
            #         (),
            #         (),
            #         (),
            #         (),
            #     ],
            #     False,
            #     4,
            #     28,
            #     None,
            #     11,
            #     None,
            #     (
            #         "UAT-ABD-DIFF-8002",
            #         None,
            #         None,
            #         None,
            #         4,
            #         [0, 0, 0, 0],
            #         "S",
            #     ),
            #     "Test 23 - If absolute difference < 11 and amend total is false then we correct the components",
            #     # Sheet TCC_test_data_case_a8 reference 8002
            #     # If absolute difference <= absolute difference threshold and > 0 but components sum = 0 or missing,
            #     # and amend total = False, then do not amend total.
            #     # TCC marker = S
            # ),
            (
                "UAT-ABD-DIFF-8003",
                11,
                [
                    (0),
                    (0),
                    (0),
                    (0),
                ],
                False,
                11,
                28,
                None,
                11,
                None,
                (
                    "UAT-ABD-DIFF-8003",
                    None,
                    None,
                    None,
                    11,
                    [0, 0, 0, 0],
                    "S",
                ),
                "Test 24 - If absolute difference < 11 and amend total is false then we correct the components",
                # Sheet TCC_test_data_case_a8 reference 8003
                # If absolute difference <= absolute difference threshold and > 0 but components sum = 0 or missing,
                # and amend total = False, then do not amend total.
                # TCC marker = S
            ),
            (
                "UAT-ABD-DIFF-9001",
                0,
                [
                    (7),
                    (0),
                    (2),
                    (2),
                ],
                True,
                0,
                28,
                None,
                11,
                None,
                (
                    "UAT-ABD-DIFF-9001",
                    11,
                    None,
                    None,
                    11,
                    [7, 0, 2, 2],
                    "T",
                ),
                "Test 25 - If the total is 0, sum of components is > 0, amend total is true then we correct the total",
                # Sheet TCC_test_data_case_a9 reference 9001
                # If Total = 0 and comp sum > 0 and amend total = TRUE.
                # Correct total if within tolerance, else flag for manual check.
                # TCC = T or M, depending on IF
            ),
            (
                "UAT-ABD-DIFF-9002",
                0,
                [
                    (2),
                    (4),
                    (3),
                    (1),
                ],
                True,
                0,
                28,
                None,
                11,
                None,
                (
                    "UAT-ABD-DIFF-9002",
                    10,
                    None,
                    None,
                    10,
                    [2, 4, 3, 1],
                    "T",
                ),
                "Test 26 - If the total is 0, sum of components is > 0, amend total is true then we correct the total",
                # Sheet TCC_test_data_case_a9 reference 9002
                # If Total = 0 and comp sum > 0 and amend total = TRUE.
                # Correct total if within tolerance, else flag for manual check.
                # TCC = T or M, depending on IF
            ),
            (
                "UAT-ABD-DIFF-9003",
                0,
                [
                    (6),
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
                    "UAT-ABD-DIFF-9003",
                    6,
                    None,
                    None,
                    6,
                    [6, 0, 0, 0],
                    "T",
                ),
                "Test 27 - If the total is 0, sum of components is > 0, amend total is true then we correct the total",
                # Sheet TCC_test_data_case_a9 reference 9003
                # If Total = 0 and comp sum > 0 and amend total = TRUE.
                # Correct total if within tolerance, else flag for manual check.
                # TCC = T or M, depending on IF
            ),
            (
                "UAT-ABD-DIFF-10001",
                0,
                [
                    (7),
                    (0),
                    (2),
                    (2),
                ],
                False,
                0,
                28,
                None,
                11,
                None,
                (
                    "UAT-ABD-DIFF-10001",
                    11,
                    None,
                    None,
                    0,
                    [0, 0, 0, 0],
                    "C",
                ),
                "Test 28 - If the total is 0, sum of components is > 0, amend total is false then we correct the component",  # noqa: E501
                # Sheet TCC_test_data_case_a10 reference 10001
                # If Total = 0 and components > 0 and amend total = FALSE.
                # Override comps with zeros, if within tolerance.
                # TCC = C or M, depending on IF
            ),
            (
                "UAT-ABD-DIFF-10002",
                0,
                [
                    (2),
                    (4),
                    (3),
                    (1),
                ],
                False,
                0,
                28,
                None,
                11,
                None,
                (
                    "UAT-ABD-DIFF-10002",
                    10,
                    None,
                    None,
                    0,
                    [0, 0, 0, 0],
                    "C",
                ),
                "Test 29 - If the total is 0, sum of components is > 0, amend total is false then we correct the component",  # noqa: E501
                # Sheet TCC_test_data_case_a10 reference 10002
                # If Total = 0 and components > 0 and amend total = FALSE.
                # Override comps with zeros, if within tolerance.
                # TCC = C or M, depending on IF
            ),
            (
                "UAT-ABD-DIFF-10003",
                0,
                [
                    (6),
                    (0),
                    (0),
                    (0),
                ],
                False,
                0,
                28,
                None,
                11,
                None,
                (
                    "UAT-ABD-DIFF-10003",
                    6,
                    None,
                    None,
                    0,
                    [0, 0, 0, 0],
                    "C",
                ),
                "Test 30 - If the total is 0, sum of components is > 0, amend total is false then we correct the component",  # noqa: E501
                # Sheet TCC_test_data_case_a10 reference 10003
                # If Total = 0 and components > 0 and amend total = FALSE.
                # Override comps with zeros, if within tolerance.
                # TCC = C or M, depending on IF
            ),
            (
                "UAT-ABD-DIFF-11001",
                1621,
                [
                    (632),
                    (732),
                    (99),
                    (162),
                ],
                True,
                None,
                28,
                1619,
                11,
                None,
                (
                    "UAT-ABD-DIFF-11001",
                    6,
                    None,
                    None,
                    1625,
                    [632, 732, 99, 162],
                    "T",
                ),
                "Test 31 - If absolute difference <= 11 and the auxiliary is used as the predictive then we correct the total",  # noqa: E501
                # Sheet TCC_test_data_case_a11 reference 11001
                # If the absolute difference <= absolute difference threshold and > 0
                # but absolute difference is calculated with auxiliary
                # (should only be used if populated and predictive value is missing).
                # TCC = T/C depending on Amend Total
            ),
            (
                "UAT-ABD-DIFF-11002",
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
                10821,
                11,
                None,
                (
                    "UAT-ABD-DIFF-11002",
                    10,
                    None,
                    None,
                    10811,
                    [9201, 866, 632, 112],
                    "T",
                ),
                "Test 32 - If absolute difference <= 11 and the auxiliary is used as the predictive then we correct the total",  # noqa: E501
                # Sheet TCC_test_data_case_a11 reference 11002
                # If the absolute difference <= absolute difference threshold and > 0
                # but absolute difference is calculated with auxiliary
                # (should only be used if populated and predictive value is missing).
                # TCC = T/C depending on Amend Total
            ),
            (
                "UAT-ABD-DIFF-11003",
                103,
                [
                    (98),
                    (0),
                    (4),
                    (6),
                ],
                True,
                None,
                28,
                107,
                11,
                None,
                (
                    "UAT-ABD-DIFF-11003",
                    1,
                    None,
                    None,
                    108,
                    [98, 0, 4, 6],
                    "T",
                ),
                "Test 33 - If absolute difference <= 11 and the auxiliary is used as the predictive then we correct the total",  # noqa: E501
                # Sheet TCC_test_data_case_a11 reference 11003
                # If the absolute difference <= absolute difference threshold and > 0
                # but absolute difference is calculated with auxiliary
                # (should only be used if populated and predictive value is missing).
                # TCC = T/C depending on Amend Total
            ),
            (
                "UAT-ABD-DIFF-12001",
                1621,
                [
                    (632),
                    (732),
                    (99),
                    (162),
                ],
                True,
                1621,
                28,
                None,
                0,
                None,
                (
                    "UAT-ABD-DIFF-12001",
                    4,
                    None,
                    None,
                    1621,
                    [632, 732, 99, 162],
                    "M",
                ),
                "Test 34 - If absolute difference > absolute difference threshold but the predictive total is different to current total then we get a total correction",  # noqa: E501
                # Sheet TCC_test_data_case_a12 reference 12001
                # If absolute difference > absolute difference threshold,
                # where threshold = 0.
                # TCC Marker = M
            ),
            (
                "UAT-ABD-DIFF-12002",
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
                0,
                None,
                (
                    "UAT-ABD-DIFF-12002",
                    6,
                    None,
                    None,
                    10817,
                    [9201, 866, 632, 112],
                    "M",
                ),
                "Test 35 - If absolute difference > absolute difference threshold but the predictive total is different to current total then we get a total correction",  # noqa: E501
                # Sheet TCC_test_data_case_a12 reference 12002
                # If absolute difference > absolute difference threshold,
                # where threshold = 0.
                # TCC Marker = M
            ),
            (
                "UAT-ABD-DIFF-12003",
                103,
                [
                    (98),
                    (0),
                    (4),
                    (6),
                ],
                True,
                103,
                28,
                None,
                0,
                None,
                (
                    "UAT-ABD-DIFF-12003",
                    5,
                    None,
                    None,
                    103,
                    [98, 0, 4, 6],
                    "M",
                ),
                "Test 36 - If absolute difference > absolute difference threshold but the predictive total is different to current total then we get a total correction",  # noqa: E501
                # Sheet TCC_test_data_case_a12 reference 12003
                # If absolute difference > absolute difference threshold,
                # where threshold = 0.
                # TCC Marker = M
            ),
            (
                "UAT-ABD-DIFF-13001",
                1621,
                [
                    (632),
                    (732),
                    (99),
                    (162),
                ],
                True,
                1619,
                28,
                None,
                11,
                None,
                (
                    "UAT-ABD-DIFF-13001",
                    6,
                    None,
                    None,
                    1625,
                    [632, 732, 99, 162],
                    "T",
                ),
                "Test 37 - If absolute difference <= 11 and > 0 but the predictive total is different to the current period total then we do a total correction",  # noqa: E501
                # Sheet TCC_test_data_case_a13 reference 13001
                # If absolute difference <= absolute difference threshold and > 0 but the predictive total
                # is different to the current period total
                # (I.e., user fed in another column of data as predictive).
                # TCC = T/C depending on Amend Total
            ),
            (
                "UAT-ABD-DIFF-13002",
                10817,
                [
                    (9201),
                    (866),
                    (632),
                    (112),
                ],
                True,
                10821,
                28,
                None,
                11,
                None,
                (
                    "UAT-ABD-DIFF-13002",
                    10,
                    None,
                    None,
                    10811,
                    [9201, 866, 632, 112],
                    "T",
                ),
                "Test 38 - If absolute difference <= 11 and > 0 but the predictive total is different to the current period total then we do a total correction",  # noqa: E501
                # Sheet TCC_test_data_case_a13 reference 13002
                # If absolute difference <= absolute difference threshold and > 0 but the predictive total
                # is different to the current period total
                # (I.e., user fed in another column of data as predictive).
                # TCC = T/C depending on Amend Total
            ),
            (
                "UAT-ABD-DIFF-13003",
                103,
                [
                    (98),
                    (0),
                    (4),
                    (6),
                ],
                True,
                107,
                28,
                None,
                11,
                None,
                (
                    "UAT-ABD-DIFF-13003",
                    1,
                    None,
                    None,
                    108,
                    [98, 0, 4, 6],
                    "T",
                ),
                "Test 39 - If absolute difference <= 11 and > 0 but the predictive total is different to the current period total then we do a total correction",  # noqa: E501
                # Sheet TCC_test_data_case_a13 reference 13003
                # If absolute difference <= absolute difference threshold and > 0 but the predictive total
                # is different to the current period total
                # (I.e., user fed in another column of data as predictive).
                # TCC = T/C depending on Amend Total
            ),
            # (
            #     "UAT-ABD-DIFF-14001",
            #     1522,
            #     [
            #         (632),
            #         (732),
            #         (),
            #         (162),
            #     ],
            #     False,
            #     1522,
            #     28,
            #     None,
            #     11,
            #     None,
            #     (
            #         "UAT-ABD-DIFF-14001",
            #         4,
            #         None,
            #         None,
            #         1522,
            #         [9206.1599, 866.48565, None, 632.35443],
            #         "C",
            #     ),
            #     "Test 40 - If absolute difference < absolute difference threshold amend total is false then we correct the components",  # noqa: E501
            #     # Sheet TCC_test_data_case_a14 reference 14001
            #     # If absolute difference < absolute difference threshold,
            #     # amend total = FALSE, some
            #     # components are missing. TCC = C
            # ),
            # (
            #     "UAT-ABD-DIFF-14002",
            #     10705,
            #     [
            #         (9201),
            #         (866),
            #         (632),
            #         (),
            #     ],
            #     False,
            #     10705,
            #     8,
            #     None,
            #     11,
            #     None,
            #     (
            #         "UAT-ABD-DIFF-14002",
            #         6,
            #         None,
            #         None,
            #         10705,
            #         [9206.1599, 866.48565, 632.35443, None],
            #         "C",
            #     ),
            #     "Test 41 - If absolute difference < absolute difference threshold amend total is false then we correct the components",  # noqa: E501
            #     # Sheet TCC_test_data_case_a14 reference 14002
            #     # If absolute difference < absolute difference threshold,
            #     # amend total = FALSE, some
            #     # components are missing. TCC = C
            # ),
            # (
            #     "UAT-ABD-DIFF-14003",
            #     103,
            #     [
            #         (98),
            #         (),
            #         (4),
            #         (6),
            #     ],
            #     False,
            #     103,
            #     8,
            #     None,
            #     11,
            #     None,
            #     (
            #         "UAT-ABD-DIFF-14003",
            #         6,
            #         None,
            #         None,
            #         103,
            #         [9206.1599, None, 866.48565, 632.35443],
            #         "C",
            #     ),
            #     "Test 42 - If absolute difference < absolute difference threshold amend total is false then we correct the components",  # noqa: E501
            #     # Sheet TCC_test_data_case_a14 reference 14003
            #     # If absolute difference < absolute difference threshold,
            #     # amend total = FALSE, some
            #     # components are missing. TCC = C
            # ),
            (
                "UAT-PERC-DIFF-1001",
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
                None,
                0.1,
                (
                    "UAT-PERC-DIFF-1001",
                    None,
                    1462.5,
                    1787.5,
                    1625,
                    [632, 732, 99, 162],
                    "N",
                ),
                "Test 43 - Absolute difference = 0, then no correction is applied.",
                # Sheet TCC_test_data_case_b1 reference 1001
                # If initial absolute difference between
                # the total and components sum = 0,
                # then no correction is applied.
                # TCC = N
            ),
            (
                "UAT-PERC-DIFF-1002",
                10811,
                [
                    (9201),
                    (866),
                    (632),
                    (112),
                ],
                True,
                10811,
                28,
                None,
                None,
                0.1,
                (
                    "UAT-PERC-DIFF-1002",
                    None,
                    9729.9,
                    11892.1,
                    10811,
                    [9201, 866, 632, 112],
                    "N",
                ),
                "Test 44 - Absolute difference = 0, then no correction is applied.",
                # Sheet TCC_test_data_case_b1 reference 1002
                # If initial absolute difference between
                # the total and components sum = 0,
                # then no correction is applied.
                # TCC = N
            ),
            (
                "UAT-PERC-DIFF-1003",
                108,
                [
                    (98),
                    (0),
                    (4),
                    (6),
                ],
                True,
                108,
                28,
                None,
                None,
                0.1,
                (
                    "UAT-PERC-DIFF-1003",
                    None,
                    97.2,
                    118.8,
                    108,
                    [98, 0, 4, 6],
                    "N",
                ),
                "Test 45 - Absolute difference = 0, then no correction is applied.",
                # Sheet TCC_test_data_case_b1 reference 1003
                # If initial absolute difference between
                # the total and components sum = 0,
                # then no correction is applied.
                # TCC = N
            ),
            (
                "UAT-PERC-DIFF-2001",
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
                None,
                0.1,
                (
                    "UAT-PERC-DIFF-2001",
                    None,
                    1462.5,
                    1787.5,
                    1964,
                    [632, 732, 99, 162],
                    "M",
                ),
                "Test 46 - If percentage difference > 10 then manual editing is required",
                # Sheet TCC_test_data_case_b2 reference 2001
                # If percentage difference > 10, then no correction is applied,
                # and marker shows manual editing required.
                # TCC = M
            ),
            (
                "UAT-PERC-DIFF-2002",
                12492,
                [
                    (9201),
                    (866),
                    (632),
                    (112),
                ],
                True,
                12492,
                28,
                None,
                None,
                0.1,
                (
                    "UAT-PERC-DIFF-2002",
                    None,
                    9729.9,
                    11892.1,
                    12492,
                    [9201, 866, 632, 112],
                    "M",
                ),
                "Test 47 - If percentage difference > 10 then manual editing is required",
                # Sheet TCC_test_data_case_b2 reference 2002
                # If percentage difference > 10, then no correction is applied,
                # and marker shows manual editing required.
                # TCC = M
            ),
            (
                "UAT-PERC-DIFF-2003",
                153,
                [
                    (98),
                    (0),
                    (4),
                    (6),
                ],
                True,
                153,
                28,
                None,
                None,
                0.1,
                (
                    "UAT-PERC-DIFF-2003",
                    None,
                    97.2,
                    118.8,
                    153,
                    [98, 0, 4, 6],
                    "M",
                ),
                "Test 48 - If percentage difference > 10 then manual editing is required",
                # Sheet TCC_test_data_case_b2 reference 2003
                # If percentage difference > 10, then no correction is applied,
                # and marker shows manual editing required.
                # TCC = M
            ),
            (
                "UAT-PERC-DIFF-3001",
                1458,
                [
                    (632),
                    (732),
                    (99),
                    (157),
                ],
                True,
                1458,
                28,
                None,
                None,
                0.1,
                (
                    "UAT-PERC-DIFF-3001",
                    None,
                    1458,
                    1782,
                    1620,
                    [632, 732, 99, 157],
                    "T",
                ),
                "Test 49 - If percentage difference = 10 and amend total = TRUE, then the total is corrected",
                # Sheet TCC_test_data_case_b3 reference 3001
                # If percentage difference = 10 and amend total = TRUE, then correction applied
                # and total corrected. TCC = T
            ),
            (
                "UAT-PERC-DIFF-3002",
                11902,
                [
                    (9201),
                    (866),
                    (641),
                    (112),
                ],
                True,
                11902,
                28,
                None,
                None,
                0.1,
                (
                    "UAT-PERC-DIFF-3002",
                    None,
                    9738,
                    11902,
                    10820,
                    [9201, 866, 641, 112],
                    "T",
                ),
                "Test 50 - If percentage difference = 10 and amend total = TRUE, then the total is corrected",
                # Sheet TCC_test_data_case_b3 reference 3002
                # If percentage difference = 10 and amend total = TRUE, then correction applied
                # and total corrected. TCC = T
            ),
            (
                "UAT-PERC-DIFF-3003",
                90,
                [
                    (90),
                    (0),
                    (4),
                    (6),
                ],
                True,
                90,
                28,
                None,
                None,
                0.1,
                (
                    "UAT-PERC-DIFF-3003",
                    None,
                    90,
                    110,
                    100,
                    [90, 0, 4, 6],
                    "T",
                ),
                "Test 51 - If percentage difference = 10 and amend total = TRUE, then the total is corrected",
                # Sheet TCC_test_data_case_b3 reference 3003
                # If percentage difference = 10 and amend total = TRUE, then correction applied
                # and total corrected. TCC = T
            ),
            (
                "UAT-PERC-DIFF-4001",
                1458,
                [
                    (632),
                    (732),
                    (99),
                    (157),
                ],
                False,
                1458,
                28,
                None,
                None,
                0.1,
                (
                    "UAT-PERC-DIFF-4001",
                    None,
                    1458,
                    1782,
                    1458,
                    [568.8, 658.8, 89.1, 141.3],
                    "C",
                ),
                "Test 52 - If percentage difference = 10 and amend total = FALSE, then component correction is applied",
                # Sheet TCC_test_data_case_b4 reference 4001
                # If percentage difference = 10 and amend total = FALSE, then correction applied,
                # and components rescaled. TCC = C
            ),
            (
                "UAT-PERC-DIFF-4002",
                11902,
                [
                    (9201),
                    (866),
                    (641),
                    (112),
                ],
                False,
                11902,
                28,
                None,
                None,
                0.1,
                (
                    "UAT-PERC-DIFF-4002",
                    None,
                    9738,
                    11902,
                    11902,
                    [10121.1, 952.6, 705.1, 123.2],
                    "C",
                ),
                "Test 53 - If percentage difference = 10 and amend total = FALSE, then component correction is applied",
                # Sheet TCC_test_data_case_b4 reference 4002
                # If percentage difference = 10 and amend total = FALSE, then correction applied,
                # and components rescaled. TCC = C
            ),
            (
                "UAT-PERC-DIFF-4003",
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
                    "UAT-PERC-DIFF-4003",
                    None,
                    90,
                    110,
                    90,
                    [81, 0, 3.6, 5.4],
                    "C",
                ),
                "Test 54 - If percentage difference = 10 and amend total = FALSE, then component correction is applied",
                # Sheet TCC_test_data_case_b4 reference 4003
                # If percentage difference = 10 and amend total = FALSE, then correction applied,
                # and components rescaled. TCC = C
            ),
            (
                "UAT-PERC-DIFF-5001",
                1621,
                [
                    (632),
                    (732),
                    (99),
                    (162),
                ],
                True,
                1621,
                28,
                None,
                None,
                0.1,
                (
                    "UAT-PERC-DIFF-5001",
                    None,
                    1462.5,
                    1787.5,
                    1625,
                    [632, 732, 99, 162],
                    "T",
                ),
                "Test 55 - If percentage difference < 10 and amend total = TRUE, then total is corrected",
                # Sheet TCC_test_data_case_b5 reference 5001
                # If percentage difference < 10 and amend total = TRUE, then correction applied
                # and total corrected. TCC = T
            ),
            (
                "UAT-PERC-DIFF-5002",
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
                None,
                0.1,
                (
                    "UAT-PERC-DIFF-5002",
                    None,
                    9729.9,
                    11892.1,
                    10811,
                    [9201, 866, 632, 112],
                    "T",
                ),
                "Test 56 - If percentage difference < 10 and amend total = TRUE, then total is corrected",
                # Sheet TCC_test_data_case_b5 reference 5002
                # If percentage difference < 10 and amend total = TRUE, then correction applied
                # and total corrected. TCC = T
            ),
            (
                "UAT-PERC-DIFF-5003",
                103,
                [
                    (98),
                    (0),
                    (4),
                    (6),
                ],
                True,
                103,
                28,
                None,
                None,
                0.1,
                (
                    "UAT-PERC-DIFF-5003",
                    None,
                    97.2,
                    118.8,
                    108,
                    [98, 0, 4, 6],
                    "T",
                ),
                "Test 57 - If percentage difference < 10 and amend total = TRUE, then total is corrected",
                # Sheet TCC_test_data_case_b5 reference 5003
                # If percentage difference < 10 and amend total = TRUE, then correction applied
                # and total corrected. TCC = T
            ),
            (
                "UAT-PERC-DIFF-6001",
                1621,
                [
                    (632),
                    (732),
                    (99),
                    (162),
                ],
                False,
                1621,
                28,
                None,
                None,
                0.1,
                (
                    "UAT-PERC-DIFF-6001",
                    None,
                    1462.5,
                    1787.5,
                    1621,
                    [
                        630.4443076923077,
                        730.1981538461539,
                        98.75630769230769,
                        161.60123076923077,
                    ],
                    "C",
                ),
                "Test 58 - If percentage difference < 10 and amend total = FALSE, then component correction is applied",  # noqa: E501
                # Sheet TCC_test_data_case_b6 reference 6001
                # If percentage difference < 10 and amend total = FALSE, then correction applied,
                # and components rescaled. TCC = C
            ),
            # (
            #     "UAT-PERC-DIFF-6002",
            #     10817,
            #     [
            #         (9201),
            #         (866),
            #         (632),
            #         (112),
            #     ],
            #     False,
            #     10817,
            #     28,
            #     None,
            #     None,
            #     0.1,
            #     (
            #         "UAT-PERC-DIFF-6002",
            #         None,
            #         9729.9,
            #         11892.1,
            #         10817,
            #         [
            #             9206.10646563685,
            #             866.4806215891222,
            #             632.3507538618074,
            #             112.06215891221903,
            #         ],
            #         "C",
            #     ),
            #     "Test 59 - If percentage difference < 10 and amend total = FALSE, then component correction is applied",  # noqa: E501
            #     # Sheet TCC_test_data_case_b6 reference 6002
            #     # If percentage difference < 10 and amend total = FALSE, then correction applied,
            #     # and components rescaled. TCC = C
            # ),
            (
                "UAT-PERC-DIFF-6003",
                103,
                [
                    (98),
                    (0),
                    (4),
                    (6),
                ],
                False,
                103,
                28,
                None,
                None,
                0.1,
                (
                    "UAT-PERC-DIFF-6003",
                    None,
                    97.2,
                    118.8,
                    103,
                    [
                        93.46296296296296,
                        0,
                        3.814814814814815,
                        5.722222222222222,
                    ],
                    "C",
                ),
                "Test 60 - If percentage difference < 10 and amend total = FALSE, then component correction is applied",  # noqa: E501
                # Sheet TCC_test_data_case_b6 reference 6003
                # If percentage difference < 10 and amend total = FALSE, then correction applied,
                # and components rescaled. TCC = C
            ),
            (
                "UAT-PERC-DIFF-7001",
                1621,
                [
                    (0),
                    (0),
                    (0),
                    (0),
                ],
                True,
                1621,
                1,
                None,
                None,
                0.1,
                (
                    "UAT-PERC-DIFF-7001",
                    None,
                    None,
                    None,
                    1621,
                    [0, 0, 0, 0],
                    "S",
                ),
                "Test 61 - percentage difference > 0 and component sum is 0 and amend total is true",
                # Sheet TCC_test_data_case_b7 reference 7001
                # If the percentage difference is greater than 0, the component sum
                # is 0 and the amend total is true then the method stops
            ),
            (
                "UAT-PERC-DIFF-7002",
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
                None,
                0.1,
                (
                    "UAT-PERC-DIFF-7002",
                    None,
                    None,
                    None,
                    10817,
                    [0, 0, 0, 0],
                    "S",
                ),
                "Test 62 - percentage difference > 0 and component sum is 0 and amend total is true",
                # Sheet TCC_test_data_case_b7 reference 7002
                # If the percentage difference is greater than 0, the component sum
                # is 0 and the amend total is true then the method stops
            ),
            (
                "UAT-PERC-DIFF-7003",
                103,
                [
                    (0),
                    (0),
                    (0),
                    (0),
                ],
                True,
                103,
                1,
                None,
                None,
                0.1,
                (
                    "UAT-PERC-DIFF-7003",
                    None,
                    None,
                    None,
                    103,
                    [0, 0, 0, 0],
                    "S",
                ),
                "Test 63 - percentage difference > 0 and component sum is 0 and amend total is true",
                # Sheet TCC_test_data_case_b7 reference 7003
                # If the percentage difference is greater than 0, the component sum
                # is 0 and the amend total is true then the method stops
            ),
            (
                "UAT-PERC-DIFF-8001",
                1621,
                [
                    (0),
                    (0),
                    (0),
                    (0),
                ],
                False,
                1621,
                1,
                None,
                None,
                0.1,
                (
                    "UAT-PERC-DIFF-8001",
                    None,
                    None,
                    None,
                    1621,
                    [0, 0, 0, 0],
                    "S",
                ),
                "Test 64 - If percentage difference > 0 but components sum = 0 or missing, amend total = FALSE, then the method stops",  # noqa: E501
                # Sheet TCC_test_data_case_b8 reference 8001
                # If percentage difference > 0 but components sum = 0 or missing, amend total = FALSE,
                # TCC Marker = S
            ),
            (
                "UAT-PERC-DIFF-8002",
                10817,
                [
                    (0),
                    (0),
                    (0),
                    (0),
                ],
                False,
                10817,
                1,
                None,
                None,
                0.1,
                (
                    "UAT-PERC-DIFF-8002",
                    None,
                    None,
                    None,
                    10817,
                    [0, 0, 0, 0],
                    "S",
                ),
                "Test 65 - If percentage difference > 0 but components sum = 0 or missing, amend total = FALSE, then the method stops",  # noqa: E501
                # Sheet TCC_test_data_case_b8 reference 8002
                # If percentage difference > 0 but components sum = 0 or missing, amend total = FALSE,
                # TCC Marker = S
            ),
            (
                "UAT-PERC-DIFF-8003",
                103,
                [
                    (0),
                    (0),
                    (0),
                    (0),
                ],
                False,
                103,
                1,
                None,
                None,
                0.1,
                (
                    "UAT-PERC-DIFF-8003",
                    None,
                    None,
                    None,
                    103,
                    [0, 0, 0, 0],
                    "S",
                ),
                "Test 68 - If percentage difference > 0 but components sum = 0 or missing, amend total = FALSE, then the method stops",  # noqa: E501
                # Sheet TCC_test_data_case_b8 reference 8003
                # If percentage difference > 0 but components sum = 0 or missing, amend total = FALSE,
                # TCC Marker = S
            ),
            (
                "UAT-PERC-DIFF-9001",
                1612,
                [
                    (632),
                    (732),
                    (99),
                    (162),
                ],
                True,
                None,
                28,
                1745,
                None,
                0.1,
                (
                    "UAT-PERC-DIFF-9001",
                    None,
                    1462.5,
                    1787.5,
                    1625,
                    [632, 732, 99, 162],
                    "T",
                ),
                "Test 67 - If percentage difference <= 10 and > 0 but percentage difference is calculated with auxiliary",  # noqa: E501
                # Sheet TCC_test_data_case_b9 reference 9001
                # If percentage difference <= 10 and > 0 but percentage difference is calculated with auxiliary
                # (I.e., should only be used if populated and predictive value
                # is missing). TCC = T/C depending on Amend Total
            ),
            (
                "UAT-PERC-DIFF-9002",
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
                10695,
                None,
                0.1,
                (
                    "UAT-PERC-DIFF-9002",
                    None,
                    9729.9,
                    11892.1,
                    10811,
                    [9201, 866, 632, 112],
                    "T",
                ),
                "Test 68 - If percentage difference <= 10 and > 0 but percentage difference is calculated with auxiliary",  # noqa: E501
                # Sheet TCC_test_data_case_b9 reference 9002
                # If percentage difference <= 10 and > 0 but percentage difference is calculated with auxiliary
                # (I.e., should only be used if populated and predictive value
                # is missing). TCC = T/C depending on Amend Total
            ),
            (
                "UAT-PERC-DIFF-9003",
                103,
                [
                    (98),
                    (0),
                    (4),
                    (6),
                ],
                True,
                None,
                28,
                101,
                None,
                0.1,
                (
                    "UAT-PERC-DIFF-9003",
                    None,
                    97.2,
                    118.8,
                    108,
                    [98, 0, 4, 6],
                    "T",
                ),
                "Test 69 - If percentage difference <= 10 and > 0 but percentage difference is calculated with auxiliary",  # noqa: E501
                # Sheet TCC_test_data_case_b9 reference 9003
                # If percentage difference <= 10 and > 0 but percentage difference is calculated with auxiliary
                # (I.e., should only be used if populated and predictive value
                # is missing). TCC = T/C depending on Amend Total
            ),
            (
                "UAT-PERC-DIFF-10001",
                1612,
                [
                    (632),
                    (732),
                    (99),
                    (162),
                ],
                True,
                1621,
                28,
                None,
                None,
                0,
                (
                    "UAT-PERC-DIFF-10001",
                    None,
                    1625,
                    1625,
                    1612,
                    [
                        (632),
                        (732),
                        (99),
                        (162),
                    ],
                    "M",
                ),
                "Test 70 - If percentage difference > percentage difference threshold, where threshold = 0 we require manual editing",  # noqa: E501
                # Sheet TCC_test_data_case_b10 reference 10001
                # If percentage difference > percentage difference threshold, where threshold = 0. TCC Marker = M
            ),
            (
                "UAT-PERC-DIFF-10002",
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
                None,
                0,
                (
                    "UAT-PERC-DIFF-10002",
                    None,
                    10811,
                    10811,
                    10817,
                    [9201, 866, 632, 112],
                    "M",
                ),
                "Test 71 - If percentage difference > percentage difference threshold, where threshold = 0 we require manual editing",  # noqa: E501
                # Sheet TCC_test_data_case_b10 reference 10002
                # If percentage difference > percentage difference threshold, where threshold = 0. TCC Marker = M
            ),
            (
                "UAT-PERC-DIFF-10003",
                103,
                [
                    (98),
                    (0),
                    (4),
                    (6),
                ],
                True,
                103,
                28,
                None,
                None,
                0,
                (
                    "UAT-PERC-DIFF-10003",
                    None,
                    108,
                    108,
                    103,
                    [98, 0, 4, 6],
                    "M",
                ),
                "Test 72 - If percentage difference > percentage difference threshold, where threshold = 0 we require manual editing",  # noqa: E501
                # Sheet TCC_test_data_case_b10 reference 10003
                # If percentage difference > percentage difference threshold, where threshold = 0. TCC Marker = M
            ),
            (
                "UAT-PERC-DIFF-11001",
                1621,
                [
                    (632),
                    (732),
                    (99),
                    (162),
                ],
                True,
                1745,
                28,
                None,
                None,
                0.1,
                (
                    "UAT-PERC-DIFF-11001",
                    None,
                    1462.5,
                    1787.5,
                    1625,
                    [632, 732, 99, 162],
                    "T",
                ),
                "Test 73 - If percentage difference <= 10 and > 0 then we correct the total",
                # Sheet TCC_test_data_case_b11 reference 11001
                # If percentage difference <= 10 and > 0 but the predictive total is different
                # to the current period total
                # (I.e., user fed in another column of data as predictive).
                # TCC = T/C depending on amend total
            ),
            (
                "UAT-PERC-DIFF-11002",
                10817,
                [
                    (9201),
                    (866),
                    (632),
                    (112),
                ],
                True,
                10695,
                28,
                None,
                None,
                0.1,
                (
                    "UAT-PERC-DIFF-11002",
                    None,
                    9729.9,
                    11892.1,
                    10811,
                    [9201, 866, 632, 112],
                    "T",
                ),
                "Test 74 - If percentage difference <= 10 and > 0 then we correct the total",
                # Sheet TCC_test_data_case_b11 reference 11002
                # If percentage difference <= 10 and > 0 but the predictive total is different
                # to the current period total
                # (I.e., user fed in another column of data as predictive).
                # TCC = T/C depending on amend total
            ),
            (
                "UAT-PERC-DIFF-11003",
                103,
                [
                    (98),
                    (0),
                    (4),
                    (6),
                ],
                True,
                101,
                28,
                None,
                None,
                0.1,
                (
                    "UAT-PERC-DIFF-11003",
                    None,
                    97.2,
                    118.8,
                    108,
                    [98, 0, 4, 6],
                    "T",
                ),
                "Test 75 - If percentage difference <= 10 and > 0 then we correct the total",
                # Sheet TCC_test_data_case_b11 reference 11003
                # If percentage difference <= 10 and > 0 but the predictive total is different
                # to the current period total
                # (I.e., user fed in another column of data as predictive).
                # TCC = T/C depending on amend total
            ),
            (
                "UAT-ABS-PERC-DIFF-1001",
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
                    "UAT-ABS-PERC-DIFF-1001",
                    339,
                    1462.5,
                    1787.5,
                    1964,
                    [632, 732, 99, 162],
                    "M",
                ),
                "Test 76 - If absolute difference > 25 and percentage difference > 10, then manual editing is required",
                # Sheet TCC_test_data_case_c1 reference 1001
                # If absolute difference > absolute difference threshold
                # and percentage difference > 10, then no correction is applied,
                # the marker shows manual editing required. TCC = M
            ),
            (
                "UAT-ABS-PERC-DIFF-1002",
                12492,
                [
                    (9201),
                    (866),
                    (632),
                    (112),
                ],
                True,
                12492,
                28,
                None,
                25,
                0.1,
                (
                    "UAT-ABS-PERC-DIFF-1002",
                    1681,
                    9729.9,
                    11892.1,
                    12492,
                    [9201, 866, 632, 112],
                    "M",
                ),
                "Test 77 - If absolute difference > 25 and percentage difference > 10, then manual editing is required",
                # Sheet TCC_test_data_case_c1 reference 1002
                # If absolute difference > absolute difference threshold
                # and percentage difference > 10, then no correction is applied,
                # the marker shows manual editing required. TCC = M
            ),
            (
                "UAT-ABS-PERC-DIFF-1003",
                153,
                [
                    (98),
                    (0),
                    (4),
                    (6),
                ],
                True,
                153,
                28,
                None,
                25,
                0.1,
                (
                    "UAT-ABS-PERC-DIFF-1003",
                    45,
                    97.2,
                    118.8,
                    153,
                    [98, 0, 4, 6],
                    "M",
                ),
                "Test 78 - If absolute difference > 25 and percentage difference > 10, then manual editing is required",
                # Sheet TCC_test_data_case_c1 reference 1003
                # If absolute difference > absolute difference threshold
                # and percentage difference > 10, then no correction is applied,
                # the marker shows manual editing required. TCC = M
            ),
            (
                "UAT-ABS-PERC-DIFF-2001",
                1793,
                [
                    (632),
                    (732),
                    (101),
                    (165),
                ],
                True,
                1793,
                28,
                None,
                25,
                0.1,
                (
                    "UAT-ABS-PERC-DIFF-2001",
                    163,
                    1467,
                    1793,
                    1630,
                    [632, 732, 101, 165],
                    "T",
                ),
                "Test 79 - If absolute difference > 25, percentage difference = 10 and amend total = TRUE, then the total correction is applied",  # noqa: E501
                # Sheet TCC_test_data_case_c2 reference 2001
                # If absolute difference > absolute difference threshold,
                # percentage difference = 10 and amend total = TRUE,
                # then correction applied, and total corrected. TCC = T
            ),
            (
                "UAT-ABS-PERC-DIFF-2002",
                9729,
                [
                    (9200),
                    (866),
                    (632),
                    (112),
                ],
                True,
                9729,
                28,
                None,
                25,
                0.1,
                (
                    "UAT-ABS-PERC-DIFF-2002",
                    1081,
                    9729,
                    11891,
                    10810,
                    [9200, 866, 632, 112],
                    "T",
                ),
                "Test 80 - If absolute difference > 25, percentage difference = 10 and amend total = TRUE, then the total correction is applied",  # noqa: E501
                # Sheet TCC_test_data_case_c2 reference 2002
                # If absolute difference > absolute difference threshold,
                # percentage difference = 10 and amend total = TRUE,
                # then correction applied, and total corrected. TCC = T
            ),
            (
                "UAT-ABS-PERC-DIFF-2003",
                308,
                [
                    (240),
                    (0),
                    (30),
                    (10),
                ],
                True,
                308,
                28,
                None,
                25,
                0.1,
                (
                    "UAT-ABS-PERC-DIFF-2003",
                    28,
                    252,
                    308,
                    280,
                    [240, 0, 30, 10],
                    "T",
                ),
                "Test 81 - If absolute difference > 25, percentage difference = 10 and amend total = TRUE, then the total correction is applied",  # noqa: E501
                # Sheet TCC_test_data_case_c2 reference 2003
                # If absolute difference > absolute difference threshold,
                # percentage difference = 10 and amend total = TRUE,
                # then correction applied, and total corrected. TCC = T
            ),
            (
                "UAT-ABS-PERC-DIFF-3001",
                1793,
                [
                    (632),
                    (732),
                    (101),
                    (165),
                ],
                False,
                1793,
                28,
                None,
                25,
                0.1,
                (
                    "UAT-ABS-PERC-DIFF-3001",
                    163,
                    1467,
                    1793,
                    1793,
                    [695.2, 805.2, 111.1, 181.5],
                    "C",
                ),
                "Test 82 - If absolute difference > 25, percentage difference = 10 and amend total = FALSE, then component correction is applied",  # noqa: E501
                # Sheet TCC_test_data_case_c3 reference 3001
                # If absolute difference > absolute difference threshold,
                # percentage difference = 10 and amend total = FALSE,
                # then correction applied, and components corrected. TCC = C
            ),
            (
                "UAT-ABS-PERC-DIFF-3002",
                9729,
                [
                    (9200),
                    (866),
                    (632),
                    (112),
                ],
                False,
                9729,
                28,
                None,
                25,
                0.1,
                (
                    "UAT-ABS-PERC-DIFF-3002",
                    1081,
                    9729,
                    11891,
                    9729,
                    [8280, 779.4, 568.8, 100.8],
                    "C",
                ),
                "Test 83 - If absolute difference > 25, percentage difference = 10 and amend total = FALSE, then component correction is applied",  # noqa: E501
                # Sheet TCC_test_data_case_c3 reference 3002
                # If absolute difference > absolute difference threshold,
                # percentage difference = 10 and amend total = FALSE,
                # then correction applied, and components corrected. TCC = C
            ),
            (
                "UAT-ABS-PERC-DIFF-3003",
                308,
                [
                    (240),
                    (0),
                    (30),
                    (10),
                ],
                False,
                308,
                28,
                None,
                25,
                0.1,
                (
                    "UAT-ABS-PERC-DIFF-3003",
                    28,
                    252,
                    308,
                    308,
                    [264, 0, 33, 11],
                    "C",
                ),
                "Test 84 - If absolute difference > 25, percentage difference = 10 and amend total = FALSE, then component correction is applied",  # noqa: E501
                # Sheet TCC_test_data_case_c3 reference 3003
                # If absolute difference > absolute difference threshold,
                # percentage difference = 10 and amend total = FALSE,
                # then correction applied, and components corrected. TCC = C
            ),
            (
                "UAT-ABS-PERC-DIFF-4001",
                1689,
                [
                    (632),
                    (732),
                    (101),
                    (165),
                ],
                True,
                1689,
                28,
                None,
                25,
                0.1,
                (
                    "UAT-ABS-PERC-DIFF-4001",
                    59,
                    1467,
                    1793,
                    1630,
                    [632, 732, 101, 165],
                    "T",
                ),
                "Test 85 - If absolute difference > 25, percentage difference < 10 and amend total = TRUE, then the total correction is applied",  # noqa: E501
                # Sheet TCC_test_data_case_c4 reference 4001
                # If absolute difference > absolute difference threshold,
                # percentage difference < 10 and amend total = TRUE,
                # then correction applied, and total corrected. TCC = T
            ),
            (
                "UAT-ABS-PERC-DIFF-4002",
                10384,
                [
                    (9200),
                    (866),
                    (632),
                    (112),
                ],
                True,
                10384,
                28,
                None,
                25,
                0.1,
                (
                    "UAT-ABS-PERC-DIFF-4002",
                    426,
                    9729,
                    11891,
                    10810,
                    [9200, 866, 632, 112],
                    "T",
                ),
                "Test 86 - If absolute difference > 25, percentage difference < 10 and amend total = TRUE, then the total correction is applied",  # noqa: E501
                # Sheet TCC_test_data_case_c4 reference 4002
                # If absolute difference > absolute difference threshold,
                # percentage difference < 10 and amend total = TRUE,
                # then correction applied, and total corrected. TCC = T
            ),
            (
                "UAT-ABS-PERC-DIFF-4003",
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
                    "UAT-ABS-PERC-DIFF-4003",
                    26,
                    252,
                    308,
                    280,
                    [240, 0, 30, 10],
                    "T",
                ),
                "Test 87 - If absolute difference > 25, percentage difference < 10 and amend total = TRUE, then the total correction is applied",  # noqa: E501
                # Sheet TCC_test_data_case_c4 reference 4003
                # If absolute difference > absolute difference threshold,
                # percentage difference < 10 and amend total = TRUE,
                # then correction applied, and total corrected. TCC = T
            ),
            (
                "UAT-ABS-PERC-DIFF-5002",
                10384,
                [
                    (9200),
                    (866),
                    (632),
                    (112),
                ],
                False,
                10384,
                10,
                None,
                25,
                0.1,
                (
                    "UAT-ABS-PERC-DIFF-5002",
                    426,
                    9729,
                    11891,
                    10384,
                    [
                        8837.446809,
                        831.8727105,
                        607.0941721,
                        107.586309,
                    ],
                    "C",
                ),
                "Test 88 - If absolute difference > 25, percentage difference < 10 and amend total = FALSE, then the component correction is applied",  # noqa: E501
                # Sheet TCC_test_data_case_c5 reference 5002
                # If absolute difference > absolute difference threshold,
                # percentage difference < 10 and amend total = FALSE,
                # then correction applied, and components corrected.
                # TCC = C
            ),
            (
                "UAT-ABS-PERC-DIFF-5003",
                306,
                [
                    (240),
                    (0),
                    (30),
                    (10),
                ],
                False,
                306,
                10,
                None,
                25,
                0.1,
                (
                    "UAT-ABS-PERC-DIFF-5003",
                    26,
                    252,
                    308,
                    306,
                    [
                        262.2857143,
                        0,
                        32.78571427,
                        10.92857143,
                    ],
                    "C",
                ),
                "Test 89 - If absolute difference > 25, percentage difference < 10 and amend total = FALSE, then the component correction is applied",  # noqa: E501
                # Sheet TCC_test_data_case_c5 reference 5003
                # If absolute difference > absolute difference threshold,
                # percentage difference < 10 and amend total = FALSE,
                # then correction applied, and components corrected.
                # TCC = C
            ),
            (
                "UAT-ABS-PERC-DIFF-6001",
                17,
                [
                    (5),
                    (4),
                    (0),
                    (2),
                ],
                True,
                17,
                28,
                None,
                25,
                0.1,
                (
                    "UAT-ABS-PERC-DIFF-6001",
                    6,
                    9.9,
                    12.1,
                    11,
                    [5, 4, 0, 2],
                    "T",
                ),
                "Test 90 - If absolute difference <= 25, percentage difference > 10 and amend total = TRUE, then the total correction is applied",  # noqa: E501
                # Sheet TCC_test_data_case_c6 reference 6001
                # If absolute difference <= 25, percentage difference > 10 and amend total = TRUE,
                # then correction applied, and total corrected
                # (do not flag as P not considered). TCC = T
            ),
            (
                "UAT-ABS-PERC-DIFF-6002",
                77,
                [
                    (53),
                    (24),
                    (4),
                    (7),
                ],
                True,
                77,
                28,
                None,
                25,
                0.1,
                (
                    "UAT-ABS-PERC-DIFF-6002",
                    11,
                    79.2,
                    96.8,
                    88,
                    [53, 24, 4, 7],
                    "T",
                ),
                "Test 91 - If absolute difference <= 25, percentage difference > 10 and amend total = TRUE, then the total correction is applied",  # noqa: E501
                # Sheet TCC_test_data_case_c6 reference 6002
                # If absolute difference <= 25, percentage difference > 10 and amend total = TRUE,
                # then correction applied, and total corrected
                # (do not flag as P not considered). TCC = T
            ),
            (
                "UAT-ABS-PERC-DIFF-6003",
                114,
                [
                    (49),
                    (0),
                    (30),
                    (10),
                ],
                True,
                114,
                28,
                None,
                25,
                0.1,
                (
                    "UAT-ABS-PERC-DIFF-6003",
                    25,
                    80.1,
                    97.9,
                    89,
                    [49, 0, 30, 10],
                    "T",
                ),
                "Test 92 - If absolute difference <= 25, percentage difference > 10 and amend total = TRUE, then the total correction is applied",  # noqa: E501
                # Sheet TCC_test_data_case_c6 reference 6003
                # If absolute difference <= 25, percentage difference > 10 and amend total = TRUE,
                # then correction applied, and total corrected
                # (do not flag as P not considered). TCC = T
            ),
            (
                "UAT-ABS-PERC-DIFF-7001",
                1689,
                [
                    (632),
                    (732),
                    (101),
                    (165),
                ],
                True,
                1689,
                28,
                None,
                0,
                0,
                (
                    "UAT-ABS-PERC-DIFF-7001",
                    59,
                    1630,
                    1630,
                    1689,
                    [632, 732, 101, 165],
                    "M",
                ),
                "Test 93 - If absolute difference > absolute difference threshold and percentage difference > percentage difference threshold, where both thresholds = 0. We would require manual editing",  # noqa: E501
                # Sheet TCC_test_data_case_c7 reference 7001
                # If absolute difference > absolute difference threshold
                # and percentage difference > percentage
                # difference threshold, where both thresholds = 0.
                # TCC Marker = M
            ),
            (
                "UAT-ABS-PERC-DIFF-7003",
                10384,
                [
                    (9200),
                    (866),
                    (632),
                    (112),
                ],
                True,
                10384,
                28,
                None,
                0,
                0,
                (
                    "UAT-ABS-PERC-DIFF-7003",
                    426,
                    10810,
                    10810,
                    10384,
                    [9200, 866, 632, 112],
                    "M",
                ),
                "Test 94 - If absolute difference > absolute difference threshold and percentage difference > percentage difference threshold, where both thresholds = 0. We would require manual editing",  # noqa: E501
                # Sheet TCC_test_data_case_c7 reference 7003
                # If absolute difference > absolute difference threshold
                # and percentage difference > percentage
                # difference threshold, where both thresholds = 0.
                # TCC Marker = M
            ),
            (
                "UAT-ABS-PERC-DIFF-7003",
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
                0,
                0,
                (
                    "UAT-ABS-PERC-DIFF-7003",
                    26,
                    280,
                    280,
                    306,
                    [240, 0, 30, 10],
                    "M",
                ),
                "Test 95 - If absolute difference > absolute difference threshold and percentage difference > percentage difference threshold, where both thresholds = 0. We would require manual editing",  # noqa: E501
                # Sheet TCC_test_data_case_c7 reference 7003
                # If absolute difference > absolute difference threshold
                # and percentage difference > percentage
                # difference threshold, where both thresholds = 0.
                # TCC Marker = M
            ),
            (
                "UAT-ABS-PERC-DIFF-8001",
                1689,
                [
                    (632),
                    (732),
                    (101),
                    (165),
                ],
                True,
                None,
                28,
                1748,
                25,
                0.1,
                (
                    "UAT-ABS-PERC-DIFF-8001",
                    118,
                    1467,
                    1793,
                    1630,
                    [632, 732, 101, 165],
                    "T",
                ),
                "Test 96 - If absolute difference > 25, percentage difference < 10 and amend total = TRUE and absolute difference and percentage difference are calculated with auxiliary then we correct the total",  # noqa: E501
                # Sheet TCC_test_data_case_c8 reference 8001
                # If absolute difference > absolute difference threshold,
                # percentage difference < 10 and amend total = TRUE
                # and absolute difference and percentage difference
                # are calculated with auxiliary
                # (I.e., should only be used if populated and
                # predictive value is missing). TCC = T
            ),
            (
                "UAT-ABS-PERC-DIFF-8002",
                10384,
                [
                    (9200),
                    (866),
                    (632),
                    (112),
                ],
                True,
                None,
                28,
                10576,
                25,
                0.1,
                (
                    "UAT-ABS-PERC-DIFF-8002",
                    234,
                    9729,
                    11891,
                    10810,
                    [9200, 866, 632, 112],
                    "T",
                ),
                "Test 97 - If absolute difference > 25, percentage difference < 10 and amend total = TRUE and absolute difference and percentage difference are calculated with auxiliary then we correct the total",  # noqa: E501
                # Sheet TCC_test_data_case_c8 reference 8002
                # If absolute difference > absolute difference threshold,
                # percentage difference < 10 and amend total = TRUE
                # and absolute difference and percentage difference
                # are calculated with auxiliary
                # (I.e., should only be used if populated and
                # predictive value is missing). TCC = T
            ),
            (
                "UAT-ABS-PERC-DIFF-8003",
                306,
                [
                    (240),
                    (0),
                    (30),
                    (10),
                ],
                True,
                None,
                28,
                307,
                25,
                0.1,
                (
                    "UAT-ABS-PERC-DIFF-8003",
                    27,
                    252,
                    308,
                    280,
                    [240, 0, 30, 10],
                    "T",
                ),
                "Test 98 - If absolute difference > 25, percentage difference < 10 and amend total = TRUE and absolute difference and percentage difference are calculated with auxiliary then we correct the total",  # noqa: E501
                # Sheet TCC_test_data_case_c8 reference 8003
                # If absolute difference > absolute difference threshold,
                # percentage difference < 10 and amend total = TRUE
                # and absolute difference and percentage difference
                # are calculated with auxiliary
                # (I.e., should only be used if populated and
                # predictive value is missing). TCC = T
            ),
            (
                "UAT-ABS-PERC-DIFF-9001",
                1689,
                [
                    (632),
                    (732),
                    (101),
                    (165),
                ],
                True,
                1748,
                28,
                None,
                25,
                0.1,
                (
                    "UAT-ABS-PERC-DIFF-9001",
                    118,
                    1467,
                    1793,
                    1630,
                    [632, 732, 101, 165],
                    "T",
                ),
                "Test 99 - If absolute difference > 25, percentage difference < 10 and amend total = TRUE but the predictive total is different to the current period total then we correct the total"  # noqa: E501
                # Sheet TCC_test_data_case_c9 reference 9001
                # If absolute difference > absolute difference threshold,
                # percentage difference < 10 and amend total = TRUE
                # but the predictive total is different to
                # the current period total (I.e., user fed
                # in another column of data as predictive).
                # TCC = T
            ),
            (
                "UAT-ABS-PERC-DIFF-9002",
                10384,
                [
                    (9200),
                    (866),
                    (632),
                    (112),
                ],
                True,
                10576,
                28,
                None,
                25,
                0.1,
                (
                    "UAT-ABS-PERC-DIFF-9002",
                    234,
                    9729,
                    11891,
                    10810,
                    [9200, 866, 632, 112],
                    "T",
                ),
                "Test 100 - If absolute difference > 25, percentage difference < 10 and amend total = TRUE but the predictive total is different to the current period total then we correct the total"  # noqa: E501
                # Sheet TCC_test_data_case_c9 reference 9002
                # If absolute difference > absolute difference threshold,
                # percentage difference < 10 and amend total = TRUE
                # but the predictive total is different to
                # the current period total (I.e., user fed
                # in another column of data as predictive).
                # TCC = T
            ),
            (
                "UAT-ABS-PERC-DIFF-9003",
                306,
                [
                    (240),
                    (0),
                    (30),
                    (10),
                ],
                True,
                307,
                28,
                None,
                25,
                0.1,
                (
                    "UAT-ABS-PERC-DIFF-9003",
                    27,
                    252,
                    308,
                    280,
                    [240, 0, 30, 10],
                    "T",
                ),
                "Test 101 - If absolute difference > 25, percentage difference < 10 and amend total = TRUE but the predictive total is different to the current period total then we correct the total"  # noqa: E501
                # Sheet TCC_test_data_case_c9 reference 9003
                # If absolute difference > absolute difference threshold,
                # percentage difference < 10 and amend total = TRUE
                # but the predictive total is different to
                # the current period total (I.e., user fed
                # in another column of data as predictive).
                # TCC = T
            ),
            (
                "UAT-PERC-DIFF-10001",
                110,
                [
                    (20),
                    (30),
                    (40),
                    (10),
                ],
                True,
                100,
                28,
                None,
                10,
                0,
                (
                    "UAT-PERC-DIFF-10001",
                    0,
                    100,
                    100,
                    100,
                    [20, 30, 40, 10],
                    "T",
                ),
                "Test 102 - If the absolute difference threshold = 10, and if percentage difference = 0, then no correction is made",  # noqa: E501
                # If the absolute difference threshold = 0, and if percentage difference = 0,
                # then the difference is less than or equal to the
                # threshold and the method will not correct. TCC = T
            ),
            (
                "UAT-TOLERANCE-1000",
                100,
                [
                    (20),
                    (30),
                    (40),
                    (10),
                ],
                True,
                100,
                28,
                None,
                0,
                None,
                (
                    "UAT-TOLERANCE-1000",
                    0,
                    None,
                    None,
                    100,
                    [20, 30, 40, 10],
                    "N",
                ),
                "Test 103 - If the absolute difference threshold = 0, and if absolute difference = 0, then no correction is made",  # noqa: E501
                # If the absolute difference threshold = 0, and if absolute difference = 0,
                # then the difference is less than or equal to the
                # threshold and the method will not correct. TCC = N
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
                assert results.tcc_marker == expected_result[6]

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
                100,
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
                    100,
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
                100,
                [],
                True,
                101,
                103,
                20,
                0.1,
                28,
                (
                    100,
                    [],
                    101,
                    103,
                    20,
                    0.1,
                    28,
                ),
                "Test 5: Empty component list",
                # Test to see what happens when no component list is provided
                # we expect the method to return the values
            ),
            (
                "F",
                100.0,
                [
                    ComponentPair(original_value="InvalidString", final_value=None),
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
                ValueError(get_params_is_not_a_number_error("component=InvalidString")),
                "Test 6: Invalid string in component list",
                # Test to see what happens when an invalid string value is within the
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
                ValueError(get_params_is_not_a_number_error("total")),
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
                ValueError(get_params_is_not_a_number_error("predictive")),
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
                ValueError(get_params_is_not_a_number_error("auxiliary")),
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
                ValueError(
                    get_params_is_not_a_number_error("absolute difference threshold")
                ),
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
                ValueError(
                    get_params_is_not_a_number_error("percentage difference threshold")
                ),
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
                ValueError(
                    get_one_of_params_mandatory_error(
                        [
                            "absolute_difference_threshold",
                            "percentage_difference_threshold",
                        ]
                    )
                ),
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
                ValueError(get_mandatory_param_error("amend_total")),
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
                ValueError(get_mandatory_param_error("total")),
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
            with pytest.raises(Exception) as exc_info:
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
            assert (str(exc_info.value)) == str(expected_result)


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
        getcontext().prec = precision

        if "RandomComponents" in test_id:
            for _ in range(12):
                random_float = random.uniform(0, 12)
                component = ComponentPair(original_value=random_float, final_value=None)
                test_components.append(component)

        try:
            components_sum = sum_components(test_components)
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
        getcontext().prec = precision

        try:
            components_sum = sum_components(test_components)
            absolute_difference = check_sum_components_predictive(predictive, components_sum)

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
                # Test to check if absolute difference threshold is satisfied and goes to the error correction
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
                # Test to check if absolute difference threshold is not satisfied meaning we would
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
                # Test to check if absolute difference threshold is satisfied and moves onto the
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
                # Test to check if absolute difference threshold and PDT thresholds are not satisfied
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
        # set the entered precision for Decimal calculations
        getcontext().prec = precision

        try:
            result = error_correction(
                amend_total, components_sum, original_components, predictive
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
        # set the precision for Decimal calculations
        getcontext().prec = precision

        try:
            result = correct_components(
                components_sum=components_sum,
                components=components,
                total=total
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
