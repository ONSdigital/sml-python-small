from dataclasses import dataclass
from enum import Enum
from typing import List, Optional, Tuple


class Index(Enum):
    LOW_THRESHOLD = 0
    HIGH_THRESHOLD = 1


class Input_Parameters(Enum):
    TOTAL = 0
    COMPONENTS = 1
    PREDICTIVE = 2
    AUXILIARY = 3
    ABSOLUTE_DIFFERENCE_THRESHOLD = 4
    PERCENTAGE_DIFFERENCE_THRESHOLD = 5


class Error_Correction(Enum):
    TOTAL = 0
    COMPONENTS = 1
    TCC_MARKER = 2


class TccMarker(Enum):
    STOP = "S"
    MANUAL = "M"
    TOTAL_CORRECTED = "T"
    COMPONENTS_CORRECTED = "C"
    NO_CORRECTION = "N"
    METHOD_PROCEED = "P"


class Component_list:
    def __init__(
        self, original_value: Optional[float], final_value: Optional[float] = None
    ):
        self.original_value = original_value
        self.final_value = final_value

    def __eq__(self, other):
        if not isinstance(other, Component_list):
            # don't attempt to compare against unrelated types
            return NotImplemented

        return (
            self.original_value == other.original_value
            and self.final_value == other.final_value
        )


@dataclass(frozen=True)
class Totals_and_Components_Output:
    identifier: Optional[
        str
    ]  # unique identifier, e.g Business Reporting Unit SG-should this be optional?
    period: Optional[str]  # not used in initial PoC always assume current period
    absolute_difference: float  # this is the absolute value showing the difference between the components input and
    # the predictive total
    low_percent_threshold: Optional[
        float
    ]  # the sum of the input components minus the absolute percentage difference
    high_percent_threshold: Optional[
        float
    ]  # the sum of the input components plus the absolute percentage difference
    final_total: float  # the output total which may have been corrected based on user input amend_total variable
    final_components: List[
        Component_list
    ]  # the output components which may have been corrected to match the received
    # predictive value. If corrected the components are scaled proportionally
    # based on the input values
    tcc_marker: str  # Indicates what correction (if any) was necessary. T (totals corrected), C (components corrected),

    # N (no correction required), M (manual correction required), S (method stopped due to lack of data or zero values)

    def print_output_table(self):
        print("Totals and Components Output:")
        print("-----------------------------")
        print(f"Identifier: {self.identifier}")
        print(f"Period: {self.period}")
        print(f"Absolute Difference: {self.absolute_difference}")
        print(f"Low Percent Threshold: {self.low_percent_threshold}")
        print(f"High Percent Threshold: {self.high_percent_threshold}")
        print(f"Final Total: {self.final_total}")
        print("Final Components:")
        for component in self.final_components:
            print(f"  Original Value: {component.original_value}")
            print(f"  Final Value: {component.final_value}")
        print(f"TCC Marker: {self.tcc_marker}")


def print_input_table(**kwargs):
    # Print table of variable names and values
    print("Input Table Function")
    print("Variable Name   |   Value")
    print("----------------|---------")
    for var_name, var_value in kwargs.items():
        print(f"{var_name:<15}|   {var_value}")


def validate_input(
    identifier: Optional[str],
    period: Optional[str],
    total: float,
    components: List[Component_list],
    amend_total: bool,
    predictive: Optional[float],
    predictive_period: Optional[str],
    auxiliary: Optional[float],
    absolute_difference_threshold: Optional[float],
    percentage_difference_threshold: Optional[float],
) -> tuple[
    float | None,
    List[Component_list],
    float | None,
    float | None,
    float | None,
    float | None,
    float | None,
]:
    """
    validate_input is to ensure that the dataset input record has all the values
    we need in the correct format. To do this we check to see if the data exists and is a number.
    If the data does not exist and is not a number we throw ValueError's as appropriate.

    :param identifier: Any e.g., Business Reporting Unit
    :type identifier: Optional[str]
    :param period: String in "YYYYMM" format
    :type period: Optional[str]
    :param total: Target period total, numeric – nulls allowed
    :type total: float
    :param components: Corresponding list of Total variable's components, numeric – nulls allowed
    :type components: List[Component_list]
    :param amend_total: This decided whether Total Variable should be automatically corrected,
                        Boolean. FALSE = correct components, TRUE = correct total
    :type amend_total: bool
    :param predictive:A value used as a predictor for a contributor's target variable.
    :type predictive: Optional[float]
    :param predictive_period: The period containing predictive records; defined relative to the target period.
    :type predictive_period: Optional[str]
    :param auxiliary: The variable used as a predictor for a contributor’s target variable,
                      where the predictive value is not available
                      (e.g., where the contributor was not sampled in the predictive period).
    :type auxiliary: Optional[float]
    :param absolute_difference_threshold: Is the predefined threshold for the absolute difference
    :type absolute_difference_threshold: Optional[float]
    :param percentage_difference_threshold: Is the predefined percentage threshold represented as a decimal
    :type percentage_difference_threshold: Optional[float]
    :raises ValueError: ValueErrors are returned when data is missing or in the incorrect type/format.
    :return: The tuple is a returned list of values converted to floats (if possible).
    :rtype: tuple[float |
            List[Component_list] | None, float | None, float | None, float | None, float | None, float | None]
    """
    if total:
        validate_number("total", total)
        float(total)
    if not components:
        raise ValueError("The components are not populated")
    if components:
        for x in components:
            validate_number(f"component={x.original_value}", x.original_value)
            float(x.original_value)
    if predictive:
        validate_number("predictive", predictive)
        float(predictive)
    if auxiliary:
        validate_number("auxiliary", auxiliary)
        float(auxiliary)
    if (
        absolute_difference_threshold is None
        and percentage_difference_threshold is None
    ):
        raise ValueError(
            "One or both of absolute/percentage difference thresholds must be specified"
        )
    if absolute_difference_threshold:
        validate_number("absolute difference threshold", absolute_difference_threshold)
        float(absolute_difference_threshold)
    if percentage_difference_threshold:
        validate_number(
            "percentage difference threshold", percentage_difference_threshold
        )
        float(percentage_difference_threshold)
    return (
        total,
        components,
        predictive,
        auxiliary,
        absolute_difference_threshold,
        percentage_difference_threshold,
    )


def validate_number(tag: str, value) -> bool:
    """
    validate_number will take a parsed tag and value and check ot see if the value is a number.
    If this is not the case it returns a ValueError.

    :param tag: The tag is a way of identifying the value and type entered and is used if a ValueError is returned.
    :type tag: str
    :param value: value is what is parsed to the function it can be many different types.
    :type value: float | optional
    :raises ValueError: ValueError is a means to raise error alerts.
    :return: This return a True boolean value if the value obtained is a number.
    :rtype: boolean
    """
    if not is_number(value):
        if tag != 'predictive':
            raise ValueError(f"{tag} is missing or not a number")
    return True


def is_number(value) -> bool:
    """
    is_number is a function which attempts to convert a entered type into a float.
    If will return a boolean dependent on whether it can or can't be converted.

    :param value: value is the parsed parameter which is to be converted to a float(if possible).
    :type value: float | optional
    :rtype: boolean to indicate if value is a number or not.
    """
    try:
        float(value)
    except Exception:
        return False
    return True


def check_predictive_value(
    predictive: Optional[float], auxiliary: Optional[float]
) -> tuple[float | None, str | None]:
    """
    Checks if predictive and auxiliary values are input, when predictive is None and auxiliary
    is input set predictive to auxiliary, when both are None, set Tcc_Marker to S
    and stop calculation

    :param predictive: The predictive value, typically the total for the current period.
    :type predictive: float, optional
    :param auxiliary: The value to be used in the absence of a predictive value.
    :type auxiliary: float, optional
    ...
    :return predictive: updated predictive value
    :rtype predictive: None | float
    :return Tcc_Marker: Returned Tcc_Marker if all values are None
    :rtype Tcc_Marker: None | str
    """
    tcc_marker = TccMarker.METHOD_PROCEED.value
    if predictive is None:
        if auxiliary is None:
            tcc_marker = TccMarker.STOP.value
        else:
            tcc_marker = TccMarker.METHOD_PROCEED.value
            predictive = auxiliary
    return predictive, tcc_marker


def check_zero_errors(predictive: float, components_sum: float) -> None | str:
    """
    Checks if when the predictive total is > 0, that the components sum is also > 0,
    adds a tcc_marker of 'S' when not true

    :param predictive: The predictive value, typically the total for the current period.
    :type predictive: float
    :param components_sum: total sum of all the components values entered.
    :type components_sum: float
    ...
    :return Tcc_Marker: Returned Tcc_Marker if zero error is triggered
    :rtype Tcc_Marker: None | str
    """
    if predictive > 0 and components_sum == 0:
        tcc_marker = TccMarker.STOP.value
    else:
        tcc_marker = TccMarker.METHOD_PROCEED.value
    return tcc_marker


def check_sum_components_predictive(predictive: float, components_sum: float) -> float:
    """
    check_sum_components_predictive has a very simple role. It will calculate the the absolute difference value
    of the predictive minus the components sum and return the result.

    :param predictive: This is the predictive value used in the absolute difference calculation.
    :type predictive: float
    :return: We will be returning a number for the absolute difference.
    :rtype: float | str
    """
    absolute_difference = abs(predictive - components_sum)
    return absolute_difference


def determine_error_detection(
    absolute_difference_threshold: Optional[float],
    percentage_difference_threshold: Optional[float],
    absolute_difference: float,
    predictive: float,
    thresholds: tuple,
) -> tuple[str, float | None]:
    """
    Determines and calls the relevant error detection methods to be applied to the input

    :param absolute_difference_threshold: Value used to check if the difference
                                          between the predictive total and sum
                                          of components requires an automatic update.
    :type absolute_difference_threshold: None | float
    :param percentage_difference_threshold: If the predictive total is within the
                                            specified percentage of the sum of the
                                            components, the method will
                                            automatically correct.
    :type percentage_difference_threshold: None | float
    :param absolute_difference: The absolute value showing the difference between
                                the input components and the predictive total.
    :type absolute_difference: Float
    :param predictive: The predictive value, typically the total for the current
                       period.
    :type predictive: float
    :param thresholds: Contains the High and Low percentage thresholds previously
                       calculated from the percentage_difference_threshold and
                       input components
    :type thresholds: Tuple(None | float, None | float)
    ...
    :return Tcc_Marker: Returned Tcc_Marker (either stop or continue)
    :rtype Tcc_Marker: str
    """
    # change to correct_error
    error_detection_satisfiable = False
    if absolute_difference_threshold is not None:
        error_detection_satisfiable = check_absolute_difference_threshold(
            absolute_difference_threshold, absolute_difference
        )
    elif absolute_difference_threshold is None:
        absolute_difference = None
    if (
        percentage_difference_threshold is not None
        and error_detection_satisfiable is False
    ):
        error_detection_satisfiable = check_percentage_difference_threshold(
            predictive, thresholds
        )
    if error_detection_satisfiable is False:
        tcc_marker = TccMarker.MANUAL.value
    else:
        tcc_marker = TccMarker.METHOD_PROCEED.value
    return tcc_marker, absolute_difference


def check_absolute_difference_threshold(
    absolute_difference_threshold: float, absolute_difference: float
) -> bool:
    """
    Function to check the absolute_difference against the absolute_difference_threshold
    to establish if the relationship between them is satisfiable

    :param absolute_difference_threshold: Value used to check if the difference
                                          between the predictive total and sum of
                                          components requires an automatic update.
    :type absolute_difference_threshold: float
    :param absolute_difference: The absolute value showing the difference between
                                the input components and the predictive total.
    :type absolute_difference: float
    ...
    :return satisfied: a marker indicating if the threshold is satisfied
    :rtype satisfied: bool
    """
    satisfied = False
    if absolute_difference <= absolute_difference_threshold:
        satisfied = True
    return satisfied


def check_percentage_difference_threshold(predictive: float, thresholds: tuple) -> bool:
    """
    Function to check the predictive value against the percentage thresholds to establish
    if the relationship between them is satisfiable

    :param predictive: The predictive value, typically the total for the current period.
    :type predictive: float
    :param thresholds: Contains the High and Low percentage thresholds previously
                       calculated from the percentage_difference_threshold and
                       input components
    :type thresholds: Tuple(float, float)
    ...
    :return satisfied: a marker indicating if the threshold is satisfied
    :rtype satisfied: bool
    """
    satisfied = False
    if (
        thresholds[Index.LOW_THRESHOLD.value]
        <= predictive
        <= thresholds[Index.HIGH_THRESHOLD.value]
    ):
        satisfied = True
    return satisfied


def error_correction(
    amend_total: bool,
    components_sum: float,
    original_components: List[Component_list],
    predictive: float,
) -> tuple[float, list[Component_list], str]:
    """
    Function to run the relevant error correction method and output the final corrections the method
    makes

    :param amend_total: Specifies whether the total or components should be corrected
                        when an error is detected.
    :type amend_total: bool
    :param components_sum: Sum of original values of components list
    :type components_sum: float
    :param original_components: List of Components objects so final values can be amended
    :type original_components: list(Component_list)
    :param predictive: The predictive value, typically the total for the current period.
    :type predictive: float
    ...
    :return final_total: Final Total value to be output
    :rtype final total: float
    :return original_components: Input Component list with final values updated
    :rtype original_components: list(Component_list)
    :return tcc_marker: Returned Tcc_Marker (either total corrected or components corrected)
    :rtype tcc_marker: string
    """
    if amend_total:
        final_total, original_components, tcc_marker = correct_total(
            components_sum, original_components
        )
    else:
        final_total, original_components, tcc_marker = correct_components(
            components_sum, original_components, predictive
        )
    return final_total, original_components, tcc_marker


def correct_total(
    components_sum: float, original_components: List[Component_list]
) -> tuple[float, list[Component_list], str]:
    """
    Function to correct the total value

    :param components_sum: Sum of original values of components list
    :type components_sum: float
    :param original_components: List of Components objects so final values can be amended
    :type original_components: list(Components_list)
    ...
    :return final_total: Final Total value to be output
    :rtype final_total: float
    :return original_components: Input Component list with final values updated
    :rtype original_components: list(Components_list)
    :return tcc_marker: Returned Tcc_Marker (Total_corrected)
    :rtype tcc_marker: string
    """
    final_total = components_sum
    for component in original_components:
        component.final_value = component.original_value
    tcc_marker = TccMarker.TOTAL_CORRECTED.value

    return final_total, original_components, tcc_marker


def correct_components(
    components_sum: float, original_components: List[Component_list], predictive: float
) -> tuple[float, list[Component_list], str]:
    """
    Function to correct the components values
    Calculates each component value based on the original value so
    values are weighted instead of normalised

    :param components_sum: Sum of original values of components list
    :type components_sum: float
    :param original_components: List of Components objects so final values can be amended
    :type original_components: list(Components_list)
    :param predictive: The predictive value, typically the total for the current period.
    :type predictive: float
    ...
    :return final_total: Final Total value to be output
    :rtype final_total: float
    :return original_components: Input Component list with final values updated
    :rtype original_components: list(Components_list)
    :return tcc_marker: Returned Tcc_Marker (Components_corrected)
    :rtype tcc_marker: string
    """
    final_total = predictive
    for component in original_components:
        component.final_value = (component.original_value / components_sum) * predictive
    tcc_marker = TccMarker.COMPONENTS_CORRECTED.value
    return final_total, original_components, tcc_marker


def sum_components(components: list[Component_list]) -> float:
    """

    :param components: List of components to be summed together.
    :type components liat(components_list)
    ...
    :return total_sum: Final total of summed components
    :rtype total_sum: float
    """
    total_sum = 0.0

    for component in components:
        total_sum += component.original_value

    return total_sum


def calculate_percent_threshold(
    sum_of_components: float, percentage_threshold: float
) -> Tuple[float | None, float | None]:
    """

    :param sum_of_components: A sum of the original components list input to the method
    :type sum_of_components: float
    :param percentage_threshold: If the predictive total is within the specified percentage
                                    of the sum of the components, the method will automatically
                                    correct.
    :type percentage_threshold: float
    ...
    :return low_percent_threshold: The lower threshold calculated from the sum of components
                                    and percentage threshold
    :rtype low_percent_threshold: float
    :return high_percent_threshold: The upper threshold calculated from the sum of components
                                     and percentage threshold
    :rtype high_percent_threshold: float
    """
    if percentage_threshold is None:
        low_percent_threshold = None
        high_percent_threshold = None
    else:
        low_percent_threshold = (
            abs(sum_of_components - (sum_of_components / percentage_threshold)) / 10
        )
        high_percent_threshold = (
            abs(sum_of_components + (sum_of_components / percentage_threshold)) / 10
        )
    return low_percent_threshold, high_percent_threshold


def totals_and_components(
    identifier: Optional[
        str
    ],  # unique identifier, e.g Business Reporting Unit SG-should this be optional?
    period: Optional[str],
    total: float,
    components: List[Component_list],
    amend_total: bool,
    predictive: Optional[float],
    predictive_period: Optional[
        str
    ],  # not used in initial PoC always assume current period
    auxiliary: Optional[float],
    absolute_difference_threshold: Optional[float],
    percentage_difference_threshold: Optional[float],
) -> Totals_and_Components_Output:
    """
      Calculates totals and components based on the given parameters.

    :param identifier: Unique identifier for the calculation.
    :type identifier: Optional[str]
    :param period: Not used in initial Proof of Concept (PoC). Assumes current period.
    :type period: Optional[str]
    :param total: Original value returned for the total.
    :type total: float
    :param components: List of components that should equal the total or predictive value.
    :type components: List[Component_list]
    :param amend_total: Specifies whether the total or components should be corrected when an error is
                        detected.
    :type amend_total:bool
    :param predictive: The predictive value, typically the total for the current period.
    :type predictive: Optional[float]
    :param predictive_period: Not used in initial PoC. Assumes current period.
    :type predictive_period: Optional[str]
    :param auxiliary: The value to be used in the absence of a predictive value.
    :type auxiliary: Optional[float]
    :param absolute_difference_threshold: Value used to check if the difference between
                                          the predictive total and sum of components
                                          requires an automatic update.
    :type absolute_difference_threshold: Optional[float]
    :param percentage_difference_threshold: If the predictive total is within the specified percentage
                                            of the sum of the components, the method will automatically
                                            correct.
    :type percentage_difference_threshold: Optional[float]
    :raises: N/A Currently
    :return Totals_and_Components_Output: Totals_and_Components_Output: An object containing the following attributes:
             - identifier (str, optional): Unique identifier (default: None).
             - period (str, optional): Not used in initial PoC, always assume current period (default: None).
             - absolute_difference (float): The absolute value showing the difference between the input components and
               the predictive total.
             - low_percent_threshold (float, optional): The sum of the input components minus the absolute percentage
               difference (default: None).
             - high_percent_threshold (float, optional): The sum of the input components plus the absolute percentage
               difference (default: None).
             - final_total (float): The output total, which may have been corrected based on the amend_total variable.
             - final_components (List[Component_list]): The output components, which may have been corrected to match
               the received predictive value. If corrected, the components are
               scaled proportionally
             - Tcc_Marker (str): Indicates what correction (if any) was necessary.
                Possible values: T (totals corrected),
                C (components corrected), N (no correction required), M (manual correction required),
                S (method stopped due to lack of data or zero values).
     :rtype Totals_and_Components_Output: Object[Totals_and_Components_Output]
    """

    print_input_table(
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

    try:

        input_parameters = validate_input(
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
        )

        predictive, tcc_marker = check_predictive_value(
            input_parameters[Input_Parameters.PREDICTIVE.value],
            input_parameters[Input_Parameters.AUXILIARY.value],
        )

        if tcc_marker == TccMarker.METHOD_PROCEED.value:
            for x in components:
                x.final_value = x.original_value
            component_total = sum_components(
                components=input_parameters[Input_Parameters.COMPONENTS.value]
            )
            tcc_marker = check_zero_errors(predictive, component_total)
            absolute_difference = check_sum_components_predictive(
                predictive, component_total
            )
            if input_parameters[Input_Parameters.PREDICTIVE.value] == component_total:
                tcc_marker = TccMarker.NO_CORRECTION.value
            if tcc_marker == TccMarker.METHOD_PROCEED.value:
                thresholds = calculate_percent_threshold(
                    component_total,
                    input_parameters[
                        Input_Parameters.PERCENTAGE_DIFFERENCE_THRESHOLD.value
                    ],
                )
                tcc_marker, absolute_difference = determine_error_detection(
                    input_parameters[
                        Input_Parameters.ABSOLUTE_DIFFERENCE_THRESHOLD.value
                    ],
                    input_parameters[
                        Input_Parameters.PERCENTAGE_DIFFERENCE_THRESHOLD.value
                    ],
                    absolute_difference,
                    predictive,
                    thresholds,
                )
                if tcc_marker == TccMarker.METHOD_PROCEED.value:
                    error_correction_params = error_correction(
                        amend_total=amend_total,
                        components_sum=component_total,
                        original_components=input_parameters[
                            Input_Parameters.COMPONENTS.value
                        ],
                        predictive=predictive,
                    )

                    output: Totals_and_Components_Output = Totals_and_Components_Output(
                        identifier=identifier,
                        period=period,
                        absolute_difference=absolute_difference,
                        low_percent_threshold=thresholds[Index.LOW_THRESHOLD.value],
                        high_percent_threshold=thresholds[Index.HIGH_THRESHOLD.value],
                        final_total=error_correction_params[
                            Error_Correction.TOTAL.value
                        ],
                        final_components=error_correction_params[
                            Error_Correction.COMPONENTS.value
                        ],
                        tcc_marker=error_correction_params[
                            Error_Correction.TCC_MARKER.value
                        ],
                    )

                else:
                    output: Totals_and_Components_Output = Totals_and_Components_Output(
                        identifier=identifier,
                        period=period,
                        absolute_difference=absolute_difference,
                        low_percent_threshold=thresholds[Index.LOW_THRESHOLD.value],
                        high_percent_threshold=thresholds[Index.HIGH_THRESHOLD.value],
                        final_total=predictive,
                        final_components=input_parameters[
                            Input_Parameters.COMPONENTS.value
                        ],
                        tcc_marker=TccMarker.MANUAL.value,
                    )
            else:
                output: Totals_and_Components_Output = Totals_and_Components_Output(
                    identifier=identifier,
                    period=period,
                    absolute_difference=absolute_difference,
                    low_percent_threshold=None,
                    high_percent_threshold=None,
                    final_total=predictive,
                    final_components=input_parameters[
                        Input_Parameters.COMPONENTS.value
                    ],
                    tcc_marker=tcc_marker,
                )
        else:
            output: Totals_and_Components_Output = Totals_and_Components_Output(
                identifier=identifier,
                period=period,
                absolute_difference=None,
                low_percent_threshold=None,
                high_percent_threshold=None,
                final_total=predictive,
                final_components=input_parameters[Input_Parameters.COMPONENTS.value],
                tcc_marker=tcc_marker,
            )

        output.print_output_table()

    except Exception as error:
        print("Exception error detected:", error)

    return output
