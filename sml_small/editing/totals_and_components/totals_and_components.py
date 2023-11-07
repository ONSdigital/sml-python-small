"""
Perform Totals and Components processing against provided data inputs
based on user supplied thresholds.

For Copyright information, please see LICENCE.
"""

import logging.config
import math
import sys
from decimal import Decimal
from enum import Enum
from os import path
from typing import List, Optional, Tuple, Union

from sml_small.utils.common_utils import convert_input_to_decimal, log_table, validate_number, validate_precision
from sml_small.utils.error_utils import get_mandatory_param_error, get_one_of_params_mandatory_error

# Pick up configuration for logging
log_config_path = path.join(path.dirname(path.abspath(__file__)), "../../logging.conf")
logging.config.fileConfig(log_config_path)

# Create logger
logger = logging.getLogger("SmlPythonSmallTotalsAndComponents")


# ---- Constant Definitions ----
PRECISION_MIN = 1
PRECISION_MAX = 28


# ---- Enum Definitions ----
class Index(Enum):
    """
    Enum for use when accessing values from thresholds tuple
    """

    LOW_THRESHOLD = 0
    HIGH_THRESHOLD = 1


class InputParameters(Enum):
    """
    Enum for use when accessing values from the input parameters tuple
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
        ...
        :return: Boolean, True if equality test passes
        """
        return self.value == value


# ---- Class Definitions ----
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
        ...
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

    identifier: Optional[str] = ""  # unique identifier
    absolute_difference: Optional[str]  # this is the absolute value showing the
    # difference between the components input and the predictive total
    low_percent_threshold: Optional[
        str
    ] = None  # the sum of the input components minus the absolute percentage difference
    high_percent_threshold: Optional[
        str
    ] = None  # the sum of the input components plus the absolute percentage difference
    final_total: Optional[
        str
    ] = None  # the output total which may have been corrected based on user input amend_
    # total variable
    final_components: Optional[
        List[str]
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


# ---- Custom Exceptions ----
class TACException(Exception):
    "Totals and Components error"
    pass


# ---- Method Definitions ----
def totals_and_components(
    identifier: str,
    total: float,
    components: List[float],
    amend_total: bool,
    predictive: Optional[float] = None,
    auxiliary: Optional[float] = None,
    absolute_difference_threshold: Optional[float] = None,
    percentage_difference_threshold: Optional[float] = None,
    precision: Optional[int] = PRECISION_MAX,
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
    generated. It is important to note that the value None is not to be mistaken for zero.
    It is actually representative of a null value.

    :param identifier: Unique identifier for the calculation.
    :type identifier: str
    :param total: Original value returned for the total.
    :type total: float
    :param components: List of component values, the sum of which, should match the received total value.
    :type components: List[float]
    :param amend_total: Specifies whether the total or components should be corrected when
                        an error is detected.
    :type amend_total:bool
    :param predictive: The predictive value. When specified, this value is used to determine whether
                       automatic error correction can be applied when comparing to the specified
                       absolute difference or percentage difference thresholds. Typically the predictive
                       value would be the total from an immediately prior period that has been
                       verified as valid.
    :type predictive: Optional[float]
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
    :param precision: Precision is used by the decimal package when calculating whether
                      error correction can take place and for the adjustment of either the
                      total or components and ensures the calculations are performed to the
                      specified accuracy. The default precision is specified under PRECISION_MAX
    :type precision: Optional[int]
    ...
    :raisesTACException: If invalid values are passed to the function.
    ...
    :return: TotalsAndComponentsOutput: An object containing the
                                       following attributes:
             - identifier (str): Unique identifier.
             - absolute_difference (str): The absolute value showing the difference between
             the input components and
               the predictive total.
             - low_percent_threshold (str, optional): The sum of the input components minus
             the absolute percentage
               difference (default: None).
             - high_percent_threshold (str, optional): The sum of the input components plus
             the absolute percentage
               difference (default: None).
             - final_total (str): The output total, which may have been corrected based on
             the amend_total variable.
             - final_components (List[str]): The output components, which may have been
             corrected to match the received predictive value. If corrected, the components are
               scaled proportionally
             - Tcc_Marker (str): Indicates what correction (if any) was necessary.
                Possible values:
                    T (totals corrected),
                    C (components corrected), N (no correction required),
                    M (manual correction required),
                    S (method stopped due to lack of data or zero values).
     :rtype: Tuple(TotalsAndComponentsOutput)
    """

    # we log a table of the input record values
    log_table(
        "Input Table Function",
        identifier=identifier,
        total=total,
        components=components,
        amend_total=amend_total,
        predictive=predictive,
        auxiliary=auxiliary,
        absolute_difference_threshold=absolute_difference_threshold,
        percentage_difference_threshold=percentage_difference_threshold,
    )

    try:
        output_list = {
            "identifier": identifier,
            "final_total": total,
            "final_components": components,
            "low_percent_threshold": None,
            "high_percent_threshold": None,
            "absolute_difference": None,
        }

        components_list = initialize_components_list(components)
        low_threshold = None
        high_threshold = None

        #  Check for invalid parameter values and set the precision value
        #  for decimal calculations
        precision = validate_input(
            identifier,
            total,
            components_list,
            amend_total,
            predictive,
            precision,
            auxiliary,
            absolute_difference_threshold,
            percentage_difference_threshold,
        )

        keys = [
            "total",
            "components",
            "predictive",
            "auxiliary",
            "absolute_difference_threshold",
            "percentage_difference_threshold",
        ]

        args = [
            total,
            components,
            predictive,
            auxiliary,
            absolute_difference_threshold,
            percentage_difference_threshold,
        ]

        decimal_values = convert_input_to_decimal(keys, args, precision)

        input_parameters = (
            decimal_values.get("total"),
            initialize_components_list(decimal_values.get("components")),
            decimal_values.get("predictive"),
            decimal_values.get("auxiliary"),
            decimal_values.get("absolute_difference_threshold"),
            decimal_values.get("percentage_difference_threshold"),
        )

        #  Set the predictive as either the current value, total or auxiliary
        # depending on what values exist from the data input.
        (predictive, output_list["tcc_marker"]) = set_predictive_value(
            input_parameters[InputParameters.PREDICTIVE.value],
            input_parameters[InputParameters.AUXILIARY.value],
        )

        component_total = sum_components(
            input_parameters[InputParameters.COMPONENTS.value]
        )

        if output_list["tcc_marker"] == TccMarker.METHOD_PROCEED:
            #  Check for error scenarios where the sum of the components is zero and
            #  a positive predictive value has been received
            output_list["tcc_marker"] = check_zero_errors(predictive, component_total)

            absolute_difference = check_sum_components_predictive(
                predictive, component_total
            )

            #  Determine if a correction is required
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

                # Absolute difference is output here as it would not change from this point
                # it is not output sooner as a S marker could be returned
                # before this point and that would have no absolute difference value.
                if absolute_difference_threshold is None:
                    output_list["absolute_difference"] = None
                else:
                    output_list["absolute_difference"] = absolute_difference

                # If the received total equals the sum of the received components
                # then no correction needs to take place.
                if input_parameters[InputParameters.TOTAL.value] == component_total:
                    output_list["tcc_marker"] = TccMarker.NO_CORRECTION
                else:
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
                            total=input_parameters[InputParameters.TOTAL.value],
                        )

        final_components = clean_component_list(output_list["final_components"])

        absolute_difference = (
            str(output_list["absolute_difference"])
            if output_list["absolute_difference"] is not None
            else output_list["absolute_difference"]
        )

        low_threshold = (
            str(low_threshold) if low_threshold is not None else low_threshold
        )

        high_threshold = (
            str(high_threshold) if high_threshold is not None else high_threshold
        )

        final_total = (
            str(output_list["final_total"])
            if output_list["final_total"] is not None
            else output_list["final_total"]
        )

        # Return the values as raw strings instead of decimal
        output_list = {
            "identifier": identifier,
            "absolute_difference": absolute_difference,
            "low_percent_threshold": low_threshold,
            "high_percent_threshold": high_threshold,
            "final_total": final_total,
            "final_components": final_components,
            "tcc_marker": output_list["tcc_marker"].value,
        }

        output = TotalsAndComponentsOutput(output_list)

        # Log the output table with the final values
        log_table(
            "Totals and Components Output",
            identifier=output_list["identifier"],
            absolute_difference=output_list["absolute_difference"],
            low_percent_threshold=output_list["low_percent_threshold"],
            high_percent_threshold=output_list["high_percent_threshold"],
            final_total=output_list["final_total"],
            final_components=output_list["final_components"],
            tcc_marker=output_list["tcc_marker"],
        )

        return output

    except Exception as error:
        if identifier is None:
            identifier = "N/A"

        logger.error(
            f"identifier: {identifier}, Exception full traceback: {error}",
            exc_info=True,
        )
        raise TACException(f"identifier: {identifier}", error)


def clean_component_list(components: List[Decimal]):
    """
    Takes a list of components and ensures that any empty values are treated as nan

    :param components: list of components
    :type components: List[]
    :return: cleaned_components
    :rtype: List[]
    """
    for i, component in enumerate(components):
        if isinstance(component, Decimal) and math.isnan(component):
            components[i] = float('nan')

    cleaned_components = [
        str(component) if component is not None and not math.isnan(component) else component
        for component in components
    ]

    return cleaned_components


def initialize_components_list(
    component_list: List[Decimal],
) -> List[ComponentPair]:
    """
    Takes the list of components values and constructs Component_List objects from them

    :param component_list: List of component values, the sum of which, should match the received total value.
    :type component_list: list(Decimal)
    ...
    :return: component_object_list List of components stored within ComponentsList objects
    :rtype: list(ComponentsList)
    """
    component_object_list = []
    for component in component_list:
        component_object_list.append(ComponentPair(component))
    return component_object_list


def validate_input(
    identifier: str,
    total: float,
    components: List[ComponentPair],
    amend_total: bool,
    predictive: Optional[float],
    precision: Optional[int],
    auxiliary: Optional[float],
    absolute_difference_threshold: Optional[float],
    percentage_difference_threshold: Optional[float],
) -> int:
    """
    This function is used to validate the data passed to the totals_and_components
    method ensuring that the values are present when expected and that they are of
    the correct type. If invalid data is received then an appropriate exception is
    raised.

    :param identifier: Unique identifier for the calculation.
    :type identifier: str
    :param total: Target total, numeric – nulls allowed
    :type total: float
    :param components: Corresponding list of Total variable's components, numeric – nulls allowed
    :type components: List[ComponentPair]
    :param amend_total: amend total is used for error correction
    :type amend_total: bool
    :param predictive: A value used as a predictor for a contributor's target variable.
    :type predictive: Optional[float]
    :param precision: Precision is used by the decimal package to perform calculations to the specified accuracy.
    :type precision: int
    :param auxiliary: The variable used as a predictor for a contributor’s target variable,
                      where the predictive value is not available.
    :type auxiliary: Optional[float]
    :param absolute_difference_threshold: Is the predefined threshold for the absolute difference
    :type absolute_difference_threshold: Optional[float]
    :param percentage_difference_threshold: Is the predefined percentage threshold
                                            represented as a decimal
    :type percentage_difference_threshold: Optional[float]
    ...
    :raises ValueError: ValueErrors are returned when required data is missing or in the
                        incorrect type/format.
    ...
    :return: precision
    :rtype: int
    """

    if identifier is None:
        raise ValueError(get_mandatory_param_error("identifier"))

    if total is None:
        raise ValueError(get_mandatory_param_error("total"))

    if validate_number("total", total) is True:
        total = float(total)

    # A list of empty components is not considered an error condition,
    # absence of any component list is an error
    if components is None:
        raise ValueError(get_mandatory_param_error("components"))

    for component in components:
        if validate_number(
            f"component={component.original_value}", component.original_value
        ):
            component.original_value = float(component.original_value)

    if amend_total is None:
        raise ValueError(get_mandatory_param_error("amend_total"))

    if predictive is not None and validate_number("predictive", predictive) is True:
        predictive = float(predictive)

    if auxiliary is not None and validate_number("auxiliary", auxiliary) is True:
        auxiliary = float(auxiliary)

    if (
        absolute_difference_threshold is None
        and percentage_difference_threshold is None
    ):
        raise ValueError(
            get_one_of_params_mandatory_error(
                ["absolute_difference_threshold", "percentage_difference_threshold"]
            )
        )

    if (
        absolute_difference_threshold is not None
        and validate_number(
            "absolute difference threshold", absolute_difference_threshold
        )
        is True
    ):
        absolute_difference_threshold = float(absolute_difference_threshold)

    if (
        percentage_difference_threshold is not None
        and validate_number(
            "percentage difference threshold", percentage_difference_threshold
        )
        is True
    ):
        percentage_difference_threshold = float(percentage_difference_threshold)
    precision = validate_precision(precision)
    return precision


def set_predictive_value(
    predictive: Optional[Decimal],
    auxiliary: Optional[Decimal],
) -> Tuple[Union[Decimal, None], TccMarker]:
    """
    Checks if predictive and auxiliary values are input, when predictive is None but auxiliary
    is available set predictive to auxiliary. If auxiliary is also None use the total value.

    :param predictive: The predictive value.
    :type predictive: Decimal, optional
    :param auxiliary: The value to be used in the absence of a predictive value.
    :type auxiliary: Decimal, optional
    ...
    :return: predictive, updated predictive value
    :rtype: None | Decimal
    :return: tcc_marker, updated tcc_marker value
    :rtype: TccMarker
    """
    if predictive is None:
        if auxiliary is not None:
            predictive = auxiliary
            tcc_marker = TccMarker.METHOD_PROCEED
        else:
            tcc_marker = TccMarker.STOP
            logger.warning(
                f"TCCMarker = STOP at line:{sys._getframe().f_back.f_lineno}"
            )
    else:
        tcc_marker = TccMarker.METHOD_PROCEED
    return predictive, tcc_marker


def check_zero_errors(predictive: Decimal, components_sum: Decimal) -> TccMarker:
    """
    Stop method processing when the predictive value is positive but the sum of components is zero.
    In these scenarios a correction is not possible.

    :param predictive: The predictive value, typically the total.
    :type predictive: Decimal
    :param components_sum: total sum of all the components values entered.
    :type components_sum: Decimal
    ...
    :return: tcc_marker, return a value of STOP if zero error is triggered
    :rtype: TccMarker
    """
    if predictive > 0 and (components_sum == 0 or math.isnan(components_sum)):
        tcc_marker = TccMarker.STOP
        logger.warning(f"TCCMarker = STOP at line:{sys._getframe().f_back.f_lineno}")
    else:
        tcc_marker = TccMarker.METHOD_PROCEED
    return tcc_marker


def check_sum_components_predictive(
    predictive: Decimal, components_sum: Decimal
) -> Decimal:
    """
    Calculates the absolute difference between the predictive value and the sum of the
    components and returns that value

    :param predictive: This is the predictive value used in the absolute difference calculation.
    :type predictive: Decimal
    :param components_sum: total sum of all the components values entered.
    :type components_sum: Decimal
    ...
    :return: Returns the absolute difference between the received predictive value and the received
             sum of the components as a Decimal.
    :rtype: Decimal
    """

    if not math.isnan(components_sum):
        absolute_difference = abs(predictive - components_sum)
    else:
        absolute_difference = abs(predictive)

    return absolute_difference


def determine_error_detection(
    absolute_difference_threshold: Optional[Decimal],
    percentage_difference_threshold: Optional[Decimal],
    absolute_difference: Decimal,
    predictive: Decimal,
    low_threshold: Optional[Decimal],
    high_threshold: Optional[Decimal],
) -> TccMarker:
    """
    Determines and calls the relevant error detection methods to be applied to the input

    :param absolute_difference_threshold: Value used to check if the difference
                                          between the predictive total and sum
                                          of components requires an automatic update.
    :type absolute_difference_threshold: None | Decimal
    :param percentage_difference_threshold: If the predictive total is within the
                                            specified percentage of the sum of the
                                            components, the method will
                                            automatically correct.
    :type percentage_difference_threshold: None | Decimal
    :param absolute_difference: The absolute value showing the difference between
                                the input components and the predictive total.
    :type absolute_difference: Decimal
    :param predictive: The predictive value, typically the total.
    :type predictive: Decimal
    :param low_threshold: Low percentage threshold previously
                       calculated from the percentage_difference_threshold and
                       input components
    :type low_threshold: Decimal | None
    :param high_threshold: High percentage threshold previously
                       calculated from the percentage_difference_threshold and
                       input components
    :type high_threshold: Decimal | None
    ...
    :return: TCC_Marker, Returned Tcc_Marker (either stop or continue)
    :rtype: TccMarker
    """
    if absolute_difference_threshold == 0 and percentage_difference_threshold == 0:
        tcc_marker = TccMarker.MANUAL
    else:
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
    absolute_difference_threshold: Decimal, absolute_difference: Decimal
) -> bool:
    """
    Function to determine whether error correction can be applied automatically
    based on the calculated difference between the sum of components and the predictive
    value and the specified difference threshold

    :param absolute_difference_threshold: Value used to check if the difference
                                          between the predictive total and sum of
                                          components requires an automatic update.
    :type absolute_difference_threshold: Decimal
    :param absolute_difference: The absolute value showing the difference between
                                the input components and the predictive total.
    :type absolute_difference: Decimal
    ...
    :return: correct_error a flag indicating if the threshold is satisfied and
                           automatic correction can be applied
    :rtype: bool
    """
    correct_error = False
    if absolute_difference <= absolute_difference_threshold:
        correct_error = True
    return correct_error


def check_percentage_difference_threshold(
    predictive: Decimal, low_threshold: Decimal, high_threshold: Decimal
) -> bool:
    """
    Function to determine whether error correction can be applied automatically
    based on the calculated low and high threshold based on the received sum of
    components compared to the predictive value

    :param predictive: The received predictive value, this could be based off
                       of the current total, predictive total or auxiliary
                       value dependant upon what values where passed to the
                       top level totals_and_components function.
    :type predictive: Decimal
    :param low_threshold: Low percentage threshold previously
                       calculated from the percentage_difference_threshold and
                       input components
    :type low_threshold: Decimal
     :param high_threshold: High percentage threshold previously
                       calculated from the percentage_difference_threshold and
                       input components
    :type high_threshold: Decimal
    ...
    :return: correct_error a marker indicating if the threshold is satisfied
    :rtype: bool
    """
    correct_error = False
    if low_threshold <= predictive <= high_threshold:
        correct_error = True
    return correct_error


def error_correction(
    amend_total: bool,
    components_sum: Decimal,
    original_components: List[ComponentPair],
    total: Decimal,
) -> Tuple[Decimal, List[Decimal], TccMarker]:
    """
    The error correction function will use the amend_total to either
    correct the total or components. Correcting the total will set the final
    total as the sum of components. Correcting the components will return the
    new adjusted components that have been adjusted by using the total.

    :param amend_total: Specifies whether the total or components should be corrected
                        when an error is detected.
    :type amend_total: bool
    :param total: Total value specified when the main totals_and_components method is
                  called, this is typically the total value associated with the
                  most current data received.
    :type total: Decimal
    :param components_sum: Sum of original values of components list
    :type components_sum: Decimal
    :param original_components: List of Components objects so final values can be amended
    :type original_components: list(ComponentPair)
    ...
    :return: final_total final total value to be output
    :rtype: Decimal
    :return: original_components Updated final values list to be output
    :rtype: list(Decimal)
    :return: tcc_marker Returned Tcc_Marker (either total corrected or components corrected)
    :rtype: TccMarker
    """

    if amend_total:
        final_total, original_components, tcc_marker = correct_total(
            components_sum, original_components
        )

    else:
        final_total, original_components, tcc_marker = correct_components(
            components_sum, original_components, total
        )

    final_components = []

    for component in original_components:
        final_components.append(component.final_value)

    return final_total, final_components, tcc_marker


def correct_total(
    components_sum: Decimal, original_components: List[ComponentPair]
) -> Tuple[Decimal, List[ComponentPair], TccMarker]:
    """
    Function to correct the total value

    :param components_sum: Sum of original values of components list
    :type components_sum: Decimal
    :param original_components: List of Components objects so final values can be amended
    :type original_components: list(Components_list)
    ...
    :return:  final_total, final total value to be output
    :rtype: Decimal
    :return: original_components, Input Component list with final values updated
    :rtype: list(Components_list)
    :return: tcc_marker, Returned Tcc_Marker (Total_corrected)
    :rtype: TccMarker
    """
    final_total = components_sum

    for component in original_components:
        component.final_value = component.original_value

    tcc_marker = TccMarker.TOTAL_CORRECTED

    return final_total, original_components, tcc_marker


def correct_components(
    components_sum: Decimal,
    components: List[ComponentPair],
    total: Decimal,
) -> Tuple[Decimal, List[ComponentPair], TccMarker]:
    """
    Function to correct the components values to add up to the received total value,
    set the final total as the received total and indicate that the components
    have been corrected. Calculates each component value based on the original value so
    values are weighted instead of normalised. Once corrections have taken place if
    the sum of the corrected components does not match the desired total the code
    adjusts the last component that has a positive value to ensure the sum of components
    does equal the target value. If the last component is Nan or 0 the method goes
    to the previous component in the list until it finds a valid number to correct.

    :param components_sum: Sum of original values of components list
    :type components_sum: Decimal
    :param components: a list that includes the original component
                       values received, these are used when calculating the
                       amended component values to retain the original weighting.
    :type components: list(Components_list)
    :param total: current total
    :type total: Decimal
    ...
    :return: final_total, final total value to be output
    :rtype: Decimal
    :return: components Input Component list with final values updated
    :rtype: list(Components_list)
    :return: tcc_marker, Returned Tcc_Marker (Components_corrected)
    :rtyper: TccMarker
    """
    final_total = total
    sum_of_adjusted = 0
    component_to_correct_position = 0

    # If the component sum does not equal the total then we want to correct the last
    # component so that the sum matches the total.
    # If the last final component is NaN or 0 we go to the final component before it.
    for count, component in enumerate(components):
        component.final_value = (component.original_value / components_sum) * total
        if math.isnan(
            component.final_value
        ) is False and component.final_value != Decimal("0"):
            sum_of_adjusted = sum_of_adjusted + component.final_value
            component_to_correct_position = count

    if sum_of_adjusted > final_total:
        logger.info(
            f"correct component fine tune down - {sum_of_adjusted} to {final_total}"
        )
        components[component_to_correct_position].final_value = components[
            component_to_correct_position
        ].final_value - (sum_of_adjusted - final_total)

    elif sum_of_adjusted < final_total:
        logger.info(
            f"correct component fine tune up - {sum_of_adjusted} to {final_total}"
        )
        components[component_to_correct_position].final_value = components[
            component_to_correct_position
        ].final_value + (final_total - sum_of_adjusted)

    tcc_marker = TccMarker.COMPONENTS_CORRECTED
    return final_total, components, tcc_marker


def sum_components(components: List[ComponentPair]) -> Decimal:
    """
    Returns the total sum of a received list of component values

    :param components: List of components to be summed together.
    :type components list(components_list)
    ...
    :return: total_sum Final total of summed components
    :rtype: Decimal
    """
    total_sum = 0
    for component in components:
        if not math.isnan(component.original_value):
            total_sum += component.original_value

    return total_sum


def calculate_percent_thresholds(
    sum_of_components: Decimal,
    percentage_threshold: Decimal,
    output_list: dict,
) -> Tuple[Union[Decimal, None], Union[Decimal, None], dict]:
    """
    Calculate and return the low and high percentage thresholds based on the
    sum of the received components and the specified percentage threshold factor
    (expressed as a decimal)

    :param sum_of_components: A sum of the original components list input to the method
    :type sum_of_components: Decimal
    :param percentage_threshold: If the predictive total is within the specified percentage
                                    of the sum of the components, the method will automatically
                                    correct.
    :type percentage_threshold: Decimal
    :param output_list: dictionary containing attributes output at the end of the totals and
    components function
    :type output_list: dict
    ...
    :return: low_percent_threshold, The lower threshold calculated from the sum of components
                                    and percentage threshold
    :rtype: Decimal
    :return: high_percent_threshold The upper threshold calculated from the sum of components
                                     and percentage threshold
    :rtype: Decimal
    :return: output_list, dictionary containing attributes output at the end of the totals and
    components function
    :rtype: dict
    """
    if percentage_threshold is None:
        low_percent_threshold = None
        high_percent_threshold = None
    else:
        low_percent_threshold = abs(
            sum_of_components - (sum_of_components * percentage_threshold)
        )

        high_percent_threshold = abs(
            sum_of_components + (sum_of_components * percentage_threshold)
        )

    output_list["low_percent_threshold"] = low_percent_threshold
    output_list["high_percent_threshold"] = high_percent_threshold

    return low_percent_threshold, high_percent_threshold, output_list
