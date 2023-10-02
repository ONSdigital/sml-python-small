"""
Perform Totals and Components processing against provided data inputs
based on user supplied thresholds.

For Copyright information, please see LICENCE.
"""

import logging.config
import math
import sys
from decimal import Decimal, getcontext
from enum import Enum
from os import path
from typing import List, Optional, Tuple, Union

from sml_small.utils.common_utils import log_table, validate_number
from sml_small.utils.error_utils import (get_mandatory_param_error, get_one_of_params_mandatory_error,
                                         get_param_outside_range_error)

# Pick up configuration for logging
log_config_path = path.join(path.dirname(path.abspath(__file__)), "../../logging.conf")
logging.config.fileConfig(log_config_path)

# Create logger
logger = logging.getLogger("totalsAndComponents")


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
    PRECISION = 6


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
             - final_components (List[float]): The output components, which may have been
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

        #  Check for invalid parameter values
        input_parameters = validate_input(
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

        # Set the precision for Decimal calculations
        getcontext().prec = input_parameters[InputParameters.PRECISION.value]

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

        # Return the raw string instead of the enum value
        output_list["tcc_marker"] = output_list["tcc_marker"].value
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


def initialize_components_list(
    component_list: List[float],
) -> List[ComponentPair]:
    """
    Takes the list of components values and constructs Component_List objects from them

    :param component_list: List of component values, the sum of which, should match the received total value.
    :type component_list: list(float)
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
) -> Tuple[
    float,
    List[ComponentPair],
    Union[float, None],
    Union[float, None],
    Union[float, None],
    Union[float, None],
    int,
]:
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
    :return: total is returned as a converted float
    :rtype: float
    :return: components are returned as a list of converted floats
    :rtype: List[ComponentPair]
    :return: predictive is returned as a converted float
    :rtype: float | None
    :return: auxiliary is returned as a converted float
    :rtype: float | None
    :return: absolute_difference_threshold is returned as a converted float
    :rtype: float | None
    :return: percentage_difference_threshold is returned as a converted float
    :rtype: float | None
    :return: precision
    :rtype: int is returned as a converted integer
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

    # Default the precision value when not set
    if precision is None:
        precision = PRECISION_MAX
    else:
        if validate_number("precision", precision) is True:
            precision = int(precision)

            if precision < PRECISION_MIN or precision > PRECISION_MAX:
                raise ValueError(
                    get_param_outside_range_error(
                        "precision",
                        [
                            str(PRECISION_MIN),
                            str(PRECISION_MAX),
                        ],
                    )
                )

    return (
        total,
        components,
        predictive,
        auxiliary,
        absolute_difference_threshold,
        percentage_difference_threshold,
        precision,
    )


def set_predictive_value(
    predictive: Optional[float],
    auxiliary: Optional[float],
) -> Tuple[Union[float, None], TccMarker]:
    """
    Checks if predictive and auxiliary values are input, when predictive is None but auxiliary
    is available set predictive to auxiliary. If auxiliary is also None use the total value.

    :param predictive: The predictive value.
    :type predictive: float, optional
    :param auxiliary: The value to be used in the absence of a predictive value.
    :type auxiliary: float, optional
    ...
    :return: predictive, updated predictive value
    :rtype: None | float
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


def check_zero_errors(predictive: float, components_sum: float) -> TccMarker:
    """
    Stop method processing when the predictive value is positive but the sum of components is zero.
    In these scenarios a correction is not possible.

    :param predictive: The predictive value, typically the total.
    :type predictive: float
    :param components_sum: total sum of all the components values entered.
    :type components_sum: float
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


def check_sum_components_predictive(predictive: float, components_sum: float) -> float:
    """
    Calculates the absolute difference between the predictive value and the sum of the
    components and returns that value

    :param predictive: This is the predictive value used in the absolute difference calculation.
    :type predictive: float
    :param components_sum: total sum of all the components values entered.
    :type components_sum: float
    ...
    :return: Returns the absolute difference between the received predictive value and the received
             sum of the components as a float.
    :rtype: float
    """
    if not math.isnan(components_sum):
        absolute_difference = abs(
            Decimal(str(predictive)) - Decimal(str(components_sum))
        )
    else:
        absolute_difference = abs(Decimal(str(predictive)))

    return float(absolute_difference)


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
    :param predictive: The predictive value, typically the total.
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
    :return: correct_error a flag indicating if the threshold is satisfied and
                           automatic correction can be applied
    :rtype: bool
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

    :param predictive: The received predictive value, this could be based off
                       of the current total, predictive total or auxiliary
                       value dependant upon what values where passed to the
                       top level totals_and_components function.
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
    :return: correct_error a marker indicating if the threshold is satisfied
    :rtype: bool
    """
    correct_error = False
    if low_threshold <= predictive <= high_threshold:
        correct_error = True
    return correct_error


def error_correction(
    amend_total: bool,
    components_sum: float,
    original_components: List[ComponentPair],
    total: float,
) -> Tuple[float, List[float], TccMarker]:
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
    :type total: float
    :param components_sum: Sum of original values of components list
    :type components_sum: float
    :param original_components: List of Components objects so final values can be amended
    :type original_components: list(ComponentPair)
    :param precision: Precision is used by the decimal package to perform calculations to the specified accuracy.
    :type precision: int
    ...
    :return: final_total Final Total value to be output
    :rtype: float
    :return: original_components Updated final values list to be output
    :rtype: list(float)
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
    components_sum: float, original_components: List[ComponentPair]
) -> Tuple[float, List[ComponentPair], TccMarker]:
    """
    Function to correct the total value

    :param components_sum: Sum of original values of components list
    :type components_sum: float
    :param original_components: List of Components objects so final values can be amended
    :type original_components: list(Components_list)
    ...
    :return:  final_total, Final Total value to be output
    :rtype: float
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
    components_sum: float,
    components: List[ComponentPair],
    total: float,
) -> Tuple[float, List[ComponentPair], TccMarker]:
    """
    Function to correct the components values to add up to the received total value,
    set the final total as the received total and indicate that the component
    have been corrected. Calculates each component value based on the original value so
    values are weighted instead of normalised

    :param components_sum: Sum of original values of components list
    :type components_sum: float
    :param components: a list that includes the original component
                       values received, these are used when calculating the
                       amended component values to retain the original weighting.
    :type components: list(Components_list)
    :param precision: Precision is used by the decimal package to calculate the
                      adjusted components to the specified accuracy.
    :type precision: int
    :param total: current total
    :type total: float
    ...
    :return: final_total, Final Total value to be output
    :rtype: float
    :return: components Input Component list with final values updated
    :rtype: list(Components_list)
    :return: tcc_marker, Returned Tcc_Marker (Components_corrected)
    :rtyper: TccMarker
    """
    final_total = total
    for component in components:
        component.final_value = (
            Decimal(str(component.original_value)) / Decimal(str(components_sum))
        ) * Decimal(str(total))
        component.final_value = float(component.final_value)

    tcc_marker = TccMarker.COMPONENTS_CORRECTED
    return final_total, components, tcc_marker


def sum_components(components: List[ComponentPair]) -> float:
    """
    Returns the total sum of a received list of component values

    :param components: List of components to be summed together.
    :type components list(components_list)
    ...
    :return: total_sum Final total of summed components
    :rtype: float
    """
    total_sum = 0
    for component in components:
        if not math.isnan(component.original_value):
            total_sum += Decimal(str(component.original_value))

    return float(total_sum)


def calculate_percent_thresholds(
    sum_of_components: float,
    percentage_threshold: float,
    output_list: dict,
) -> Tuple[Union[float, None], Union[float, None], dict]:
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
    :return: low_percent_threshold, The lower threshold calculated from the sum of components
                                    and percentage threshold
    :rtype: float
    :return: high_percent_threshold The upper threshold calculated from the sum of components
                                     and percentage threshold
    :rtype: float
    :return: output_list, dictionary containing attributes output at the end of the totals and
    components function
    :rtype: dict
    """
    if percentage_threshold is None:
        low_percent_threshold = None
        high_percent_threshold = None
    else:
        low_percent_threshold = abs(
            Decimal(str(sum_of_components))
            - (Decimal(str(sum_of_components)) * Decimal(str(percentage_threshold)))
        )
        low_percent_threshold = float(low_percent_threshold)
        high_percent_threshold = abs(
            Decimal(str(sum_of_components))
            + (Decimal(str(sum_of_components)) * Decimal(str(percentage_threshold)))
        )
        high_percent_threshold = float(high_percent_threshold)
    output_list["low_percent_threshold"] = low_percent_threshold
    output_list["high_percent_threshold"] = high_percent_threshold
    return low_percent_threshold, high_percent_threshold, output_list
