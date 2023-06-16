"""
For Copyright information, please see LICENCE.
"""

from enum import Enum
from typing import List, Optional, Tuple
import datetime


class Index(Enum):
    """
    Enum for use when accessing values from thresholds tuple
    """

    LOW_THRESHOLD = 0
    HIGH_THRESHOLD = 1


class InputParameters(Enum):
    """
    Enum for use when accessing values from the inputs tuple
    """

    TOTAL = 0
    COMPONENTS = 1
    PREDICTIVE = 2
    AUXILIARY = 3
    ABSOLUTE_DIFFERENCE_THRESHOLD = 4
    PERCENTAGE_DIFFERENCE_THRESHOLD = 5


class TccMarker(Enum):
    """
    Enum for use when setting/comparing tcc_marker values
    """

    STOP = "S"
    MANUAL = "M"
    TOTAL_CORRECTED = "T"
    COMPONENTS_CORRECTED = "C"
    NO_CORRECTION = "N"
    METHOD_PROCEED = "P"

    def __eq__(self, value):
        """
        Function to determine equality between ComponentList objects

        :param value: string to compare against
        :type value: string
        :return: Boolean, True if equality test passes
        """
        return self.value == value


class ComponentPair:
    """
    A class to create value pairs for components
    """

    def __init__(self, original_value: float, final_value: Optional[float] = None):
        """
        Constructor function

        :param original_value: original value for other methods to use
        :type original_value: float
        :param final_value: final value to be set later in the method
        :type final_value: Optional[float]
        """
        self.original_value = original_value
        self.final_value = final_value

    def __eq__(self, other):
        """
        Function to determine equality between ComponentList objects

        :param other: ComponentList object to compare the current object too
        :type other: ComponentPair
        :return: Boolean, True if equality test passes
        """
        if not isinstance(other, ComponentPair):
            # don't attempt to compare against unrelated types
            return NotImplemented

        return (
            self.original_value == other.original_value
            and self.final_value == other.final_value
        )


class TotalsAndComponentsOutput:
    """
    A Class defining the output attributes of the totals and components method
    """

    identifier: Optional[
        str
    ] = ""  # unique identifier, e.g Business Reporting Unit SG-should this be optional?
    period: [str] = ""  # not used in initial PoC always assume current period
    absolute_difference: Optional[float]  # this is the absolute value showing the
    # difference between the components input and the predictive total
    low_percent_threshold: Optional[
        float
    ] = None  # the sum of the input components minus the absolute percentage difference
    high_percent_threshold: Optional[
        float
    ] = None  # the sum of the input components plus the absolute percentage difference
    final_total: Optional[
        float
    ] = None  # the output total which may have been corrected based on user input amend_
    # total variable
    original_components: Optional[float]  # the original input components
    final_components: Optional[
        float
    ] = None  # the output components which may have been corrected to match the received
    # predictive value. If corrected the components are scaled proportionally
    # based on the input values
    tcc_marker: Optional[str]  # Indicates what correction (if any) was necessary.

    # T (totals corrected), C (components corrected),
    # N (no correction required), M (manual correction required), S
    # (method stopped due to lack of data or zero values)

    def __init__(self, *args):
        """
        constructor function

        :param args: dictionary of attributes to set on the object
        """
        for dictionary in args:
            for key in dictionary:
                setattr(self, key, dictionary[key])

    def print_output_table(self):
        """
        print method
        """
        print("Totals and Components Output:")
        print("-----------------------------")
        print(f"Identifier: {self.identifier}")
        print(f"Period: {self.period}")
        print(f"Absolute Difference: {self.absolute_difference}")
        print(f"Low Percent Threshold: {self.low_percent_threshold}")
        print(f"High Percent Threshold: {self.high_percent_threshold}")
        print(f"Final Total: {self.final_total}")
        print(f"Original Value: {self.original_components}")
        print(f"Final Value: {self.final_components}")
        print(f"TCC Marker: {self.tcc_marker}")


def initialize_components_list(
    component_list: list[float],
) -> [list[ComponentPair]]:
    """
    Takes the list of components values and constructs Component_List objects from them
    :param component_list: List of components that should equal the total or predictive value.
    :type component_list: list(float)
    :return component_object_list: List of components stored within ComponentsList objects
    :rtype component_object_list: list(ComponentsList)
    """
    component_object_list = []
    for component in component_list:
        component_object_list.append(ComponentPair(component))
    return component_object_list


def print_input_table(**kwargs):
    """
    Prints the attributes input

    :param kwargs:
    :type kwargs: kwargs
    :return: N/A
    """
    # Print table of variable names and values
    print("Input Table Function")
    print("Variable Name   |   Value")
    print("----------------|---------")
    for var_name, var_value in kwargs.items():
        print(f"{var_name:<15}|   {var_value}")


def validate_input(
    identifier: str,
    total: float,
    components: List[ComponentPair],
    period: Optional[str],
    predictive: Optional[float],
    auxiliary: Optional[float],
    absolute_difference_threshold: Optional[float],
    percentage_difference_threshold: Optional[float],
) -> tuple[
    float,
    List[ComponentPair],
    float | None,
    float | None,
    float | None,
    float | None,
]:
    """
    validate_input is to ensure that the dataset input record has all the values
    we need in the correct format. To do this we check to see if the data exists and is a number.
    If the data does not exist and is not a number we throw ValueError's as appropriate.

    :param identifier:
    :type identifier:
    :param period:
    :type period
    :param total: Target period total, numeric – nulls allowed
    :type total: float
    :param components: Corresponding list of Total variable's components, numeric – nulls allowed
    :type components: List[ComponentPair]
    :param predictive:A value used as a predictor for a contributor's target variable.
    :type predictive: Optional[float]
    :param auxiliary: The variable used as a predictor for a contributor’s target variable,
                      where the predictive value is not available
                      (e.g., where the contributor was not sampled in the predictive period).
    :type auxiliary: Optional[float]
    :param absolute_difference_threshold: Is the predefined threshold for the absolute difference
    :type absolute_difference_threshold: Optional[float]
    :param percentage_difference_threshold: Is the predefined percentage threshold
                                            represented as a decimal
    :type percentage_difference_threshold: Optional[float]
    :raises ValueError: ValueErrors are returned when data is missing or in the
                        incorrect type/format.
    :return: The tuple is a returned list of values converted to floats (if possible).
    :rtype: tuple[float |
            List[Component_list] | None, float | None, float | None, float | None,
            float | None, float | None]
    """
    if not identifier:
        raise ValueError("The identifier is not populated")
    str(identifier)
    if period:
        try:
            datetime.datetime.strptime(period, "%Y%M")
        except ValueError as exc:
            raise type(exc)(str(exc) + f" Period: {period} must be a String of format 'YYYYMM'")
    if total:
        validate_number("total", total)
        float(total)
    if not components:
        raise ValueError("The components are not populated")
    if components:
        for component in components:
            validate_number(
                f"component={component.original_value}", component.original_value
            )
            float(component.original_value)
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

    :param tag: The tag is a way of identifying the value and type entered and is used if a
                ValueError is returned.
    :type tag: str
    :param value: value is what is parsed to the function it can be many different types.
    :type value: float | optional
    :raises ValueError: ValueError is a means to raise error alerts.
    :return: This return a True boolean value if the value obtained is a number.
    :rtype: boolean
    """
    if not is_number(value):
        if tag != "predictive":
            raise ValueError(f"{tag} is missing or not a number")
    return True


def is_number(value) -> bool:
    """
    is_number is a function which attempts to convert a entered type into a float.
    It will return a boolean dependent on whether it can or can't be converted.

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
) -> tuple[float | None, TccMarker]:
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
    :rtype Tcc_Marker: TccMarker
    """
    tcc_marker = TccMarker.METHOD_PROCEED
    if predictive is None:
        if auxiliary is None:
            tcc_marker = TccMarker.STOP
        else:
            tcc_marker = TccMarker.METHOD_PROCEED
            predictive = auxiliary
    return predictive, tcc_marker


def check_zero_errors(predictive: float, components_sum: float) -> TccMarker:
    """
    Stop method processing when the predictive value is positive but the sum of components is zero.
    In these scenarios a correction is not possible.

    :param predictive: The predictive value, typically the total for the current period.
    :type predictive: float
    :param components_sum: total sum of all the components values entered.
    :type components_sum: float
    ...
    :return Tcc_Marker: Returned Tcc_Marker if zero error is triggered
    :rtype Tcc_Marker: TccMarker
    """
    if predictive > 0 and components_sum == 0:
        tcc_marker = TccMarker.STOP
    else:
        tcc_marker = TccMarker.METHOD_PROCEED
    return tcc_marker


def check_sum_components_predictive(
    predictive: float,
    components_sum: float,
    absolute_difference_threshold: Optional[float],
) -> float:
    """
    Calculates the absolute difference between the predictive value and the sum of the
    components and returns that value

    :param predictive: This is the predictive value used in the absolute difference calculation.
    :type predictive: float
    :param components_sum: total sum of all the components values entered.
    :type components_sum: float
    :param absolute_difference_threshold:Value used to check if the difference
                                          between the predictive total and sum
                                          of components requires an automatic update.
                                          Absolute difference is None is threshold is None
    :type absolute_difference_threshold: float
    ...
    :return: We will be returning a number for the absolute difference.
    :rtype: float
    """
    if absolute_difference_threshold is None:
        absolute_difference = None
    else:
        absolute_difference = abs(predictive - components_sum)
    return absolute_difference


def determine_error_detection(
    absolute_difference_threshold: Optional[float],
    percentage_difference_threshold: Optional[float],
    absolute_difference: float,
    predictive: float,
    low_threshold: Optional[float],
    high_threshold: Optional[float],
) -> TccMarker:
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
    :param low_threshold: Low percentage threshold previously
                       calculated from the percentage_difference_threshold and
                       input components
    :type low_threshold: float | None
    :param high_threshold: High percentage threshold previously
                       calculated from the percentage_difference_threshold and
                       input components
    :type high_threshold: float | None
    ...
    :return Tcc_Marker: Returned Tcc_Marker (either stop or continue)
    :rtype Tcc_Marker: TccMarker
    """

    correct_error = False
    if absolute_difference_threshold is not None:
        correct_error = check_absolute_difference_threshold(
            absolute_difference_threshold, absolute_difference
        )
    if percentage_difference_threshold is not None and correct_error is False:
        correct_error = check_percentage_difference_threshold(
            predictive, low_threshold, high_threshold
        )
    if correct_error is False:
        tcc_marker = TccMarker.MANUAL
    else:
        tcc_marker = TccMarker.METHOD_PROCEED
    return tcc_marker


def check_absolute_difference_threshold(
    absolute_difference_threshold: float, absolute_difference: float
) -> bool:
    """
    Function to determine whether error correction can be applied automatically
    based on the calculated difference between the sum of components and the predictive
    value and the specified difference threshold

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
    correct_error = False
    if absolute_difference <= absolute_difference_threshold:
        correct_error = True
    return correct_error


def check_percentage_difference_threshold(
    predictive: float, low_threshold: float, high_threshold: float
) -> bool:
    """
    Function to determine whether error correction can be applied automatically
    based on the calculated low and high threshold based on the received sum of
    components compared to the predictive value

    :param predictive: The predictive value, typically the total for the current period.
    :type predictive: float
    :param low_threshold: Low percentage threshold previously
                       calculated from the percentage_difference_threshold and
                       input components
    :type low_threshold: float
     :param high_threshold: High percentage threshold previously
                       calculated from the percentage_difference_threshold and
                       input components
    :type high_threshold: float
    ...
    :return satisfied: a marker indicating if the threshold is satisfied
    :rtype satisfied: bool
    """
    correct_error = False
    if low_threshold <= predictive <= high_threshold:
        correct_error = True
    return correct_error


def error_correction(
    amend_total: bool,
    components_sum: float,
    original_components: List[ComponentPair],
    predictive: float,
) -> tuple[float, list[float], TccMarker]:
    """
    Function to run the relevant error correction method and output the final corrections
    the method makes. Return a final total that is calculated from the sum of the received
    components set the final components as the received components values and indicate the
    total has been corrected

    :param amend_total: Specifies whether the total or components should be corrected
                        when an error is detected.
    :type amend_total: bool
    :param components_sum: Sum of original values of components list
    :type components_sum: float
    :param original_components: List of Components objects so final values can be amended
    :type original_components: list(ComponentPair)
    :param predictive: The predictive value, typically the total for the current period.
    :type predictive: float
    ...
    :return final_total: Final Total value to be output
    :rtype final total: float
    :return original_components: Updated final values list to be output
    :rtype original_components: list(float)
    :return tcc_marker: Returned Tcc_Marker (either total corrected or components corrected)
    :rtype tcc_marker: TccMarker
    """
    if amend_total:
        final_total, original_components, tcc_marker = correct_total(
            components_sum, original_components
        )
    else:
        final_total, original_components, tcc_marker = correct_components(
            components_sum, original_components, predictive
        )
    final_components = []
    for component in original_components:
        final_components.append(component.final_value)
    return final_total, final_components, tcc_marker


def correct_total(
    components_sum: float, original_components: List[ComponentPair]
) -> tuple[float, list[ComponentPair], TccMarker]:
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
    :rtype tcc_marker: TccMarker
    """
    final_total = components_sum
    for component in original_components:
        component.final_value = component.original_value
    tcc_marker = TccMarker.TOTAL_CORRECTED

    return final_total, original_components, tcc_marker


def correct_components(
    components_sum: float, original_components: List[ComponentPair], predictive: float
) -> tuple[float, list[ComponentPair], TccMarker]:
    """
    Function to correct the components values to add up to the received predictive value,
    set the final total as the received predictive total and indicate that the component
    have been corrected. Calculates each component value based on the original value so
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
    :rtype tcc_marker: TccMarker
    """
    final_total = predictive
    for component in original_components:
        component.final_value = (component.original_value / components_sum) * predictive
    tcc_marker = TccMarker.COMPONENTS_CORRECTED
    return final_total, original_components, tcc_marker


def sum_components(components: list[ComponentPair]) -> float:
    """
    Returns the total sum of a received list of component values

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


def calculate_percent_thresholds(
    sum_of_components: float, percentage_threshold: float, output_list: dict
) -> Tuple[float | None, float | None, dict]:
    """
    Calculate and return the low and high percentage thresholds based on the
    sum of the received components and the specified percentage threshold factor
    (expressed as a decimal)

    :param sum_of_components: A sum of the original components list input to the method
    :type sum_of_components: float
    :param percentage_threshold: If the predictive total is within the specified percentage
                                    of the sum of the components, the method will automatically
                                    correct.
    :type percentage_threshold: float
    :param output_list: dictionary containing attributes output at the end of the totals and
    components function
    :type output_list: dict
    ...
    :return low_percent_threshold: The lower threshold calculated from the sum of components
                                    and percentage threshold
    :rtype low_percent_threshold: float
    :return high_percent_threshold: The upper threshold calculated from the sum of components
                                     and percentage threshold
    :rtype high_percent_threshold: float
    :return output_list:  dictionary containing attributes output at the end of the totals and
    components function
    :rtype output_list: dict
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
    output_list["low_percent_threshold"] = low_percent_threshold
    output_list["high_percent_threshold"] = high_percent_threshold
    return low_percent_threshold, high_percent_threshold, output_list


def totals_and_components(
    identifier: str,  # unique identifier, e.g Business Reporting Unit SG-should this be optional?
    period: Optional[str],
    total: float,
    components: List[float],
    amend_total: bool,
    predictive: Optional[float],
    predictive_period: Optional[
        str
    ],  # not used in initial PoC always assume current period
    auxiliary: Optional[float],
    absolute_difference_threshold: Optional[float],
    percentage_difference_threshold: Optional[float],
) -> TotalsAndComponentsOutput:
    """
    Determines whether a difference exists between a provided total value and the sum of
    individual components. In the case where a difference exists the function can decide
    whether an automatic correction should be made based on the provided absolute difference
    and/or percentage difference thresholds. Where the correction satisfies the given thresholds
    the amend_total variable determines whether the correction is applied to the total value
    (to match the sum of the given components) or the individual components (so they add up
    to the received total). When the components are corrected to match the total then the original
    value of the components is taken into account to ensure that the corrected values are weighted
    accordingly to maintain the original distribution. If an automatic correction cannot be applied
    because the difference is out of bounds of the given thresholds then the function indicates
    that a manual correction could be attempted. When there is no difference between the provided
    total and the sum of the individual components then the function indicates no correction has
    been applied. For exceptional cases where the sum of the original components is zero and a
    positive total has been received the function indicates the method stopped processing. When
    invalid types are received for the function then an exception will be raised and no output is
    generated.


    :param identifier: Unique identifier for the calculation.
    :type identifier: str
    :param period: Not used in initial Proof of Concept (PoC). Assumes current period.
    :type period: Optional[str]
    :param total: Original value returned for the total.
    :type total: float
    :param components: List of components that should equal the total or predictive value.
    :type components: List[float]
    :param amend_total: Specifies whether the total or components should be corrected when
                        an error is detected.
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
    :param percentage_difference_threshold: If the predictive total is within the specified
                                            percentage of the sum of the components, the
                                            method will automatically correct.
    :type percentage_difference_threshold: Optional[float]
    :raises: N/A Currently
    :return: TotalsAndComponentsOutput: An object containing the
                                       following attributes:
             - identifier (str, optional): Unique identifier (default: None).
             - period (str, optional): Not used in initial PoC, always assume current period
             (default: None).
             - absolute_difference (float): The absolute value showing the difference between
             the input components and
               the predictive total.
             - low_percent_threshold (float, optional): The sum of the input components minus
             the absolute percentage
               difference (default: None).
             - high_percent_threshold (float, optional): The sum of the input components plus
             the absolute percentage
               difference (default: None).
             - final_total (float): The output total, which may have been corrected based on
             the amend_total variable.
             - final_components (List[Component_list]): The output components, which may have been
             corrected to match the received predictive value. If corrected, the components are
               scaled proportionally
             - Tcc_Marker (str): Indicates what correction (if any) was necessary.
                Possible values:
                    T (totals corrected),
                    C (components corrected), N (no correction required),
                    M (manual correction required),
                    S (method stopped due to lack of data or zero values).
     :rtype: Object[TotalsAndComponentsOutput]
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
        output_list = {
            "identifier": identifier,
            "period": period,
            "original_components": components,
        }
        components_list = initialize_components_list(components)
        #  Check for invalid parameter values
        input_parameters = validate_input(
            total,
            components_list,
            predictive,
            auxiliary,
            absolute_difference_threshold,
            percentage_difference_threshold,
        )
        #  Ensure either the predictive or auxiliary parameter specified
        predictive, output_list["tcc_marker"] = check_predictive_value(
            input_parameters[InputParameters.PREDICTIVE.value],
            input_parameters[InputParameters.AUXILIARY.value],
        )

        if output_list["tcc_marker"] == TccMarker.METHOD_PROCEED:
            component_total = sum_components(
                input_parameters[InputParameters.COMPONENTS.value]
            )
            #  Check for error scenarios where the sum of the components is zero and
            #  a positive predictive value has been received
            output_list["tcc_marker"] = check_zero_errors(predictive, component_total)
            absolute_difference = check_sum_components_predictive(
                predictive, component_total, absolute_difference_threshold
            )
            output_list["absolute_difference"] = absolute_difference
            #  Determine if a correction is required
            if input_parameters[InputParameters.PREDICTIVE.value] == component_total:
                output_list["tcc_marker"] = TccMarker.NO_CORRECTION
                output_list["final_total"] = total
                output_list["final_components"] = components
            if output_list["tcc_marker"] == TccMarker.METHOD_PROCEED:
                (
                    low_threshold,
                    high_threshold,
                    output_list,
                ) = calculate_percent_thresholds(
                    component_total,
                    input_parameters[
                        InputParameters.PERCENTAGE_DIFFERENCE_THRESHOLD.value
                    ],
                    output_list,
                )
                #  Determine if the difference error can be automatically corrected
                output_list["tcc_marker"] = determine_error_detection(
                    input_parameters[
                        InputParameters.ABSOLUTE_DIFFERENCE_THRESHOLD.value
                    ],
                    input_parameters[
                        InputParameters.PERCENTAGE_DIFFERENCE_THRESHOLD.value
                    ],
                    absolute_difference,
                    predictive,
                    low_threshold,
                    high_threshold,
                )
                if output_list["tcc_marker"] == TccMarker.MANUAL:
                    output_list["final_total"] = total
                    output_list["final_components"] = components
                if output_list["tcc_marker"] == TccMarker.METHOD_PROCEED:
                    (
                        output_list["final_total"],
                        output_list["final_components"],
                        output_list["tcc_marker"],
                    ) = error_correction(
                        amend_total=amend_total,
                        components_sum=component_total,
                        original_components=input_parameters[
                            InputParameters.COMPONENTS.value
                        ],
                        predictive=predictive,
                    )
        output_list["tcc_marker"] = output_list["tcc_marker"].value
        output = TotalsAndComponentsOutput(output_list)
        output.print_output_table()

    except Exception as error:
        print("Exception error detected:", error)

    return output
