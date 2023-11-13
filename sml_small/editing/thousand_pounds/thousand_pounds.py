import logging
import math
import sys
from dataclasses import dataclass
from decimal import Decimal
from enum import Enum
from os import path
from typing import List, Optional, Tuple

from sml_small.utils.common_utils import (
    convert_input_to_decimal,
    log_table,
    validate_number,
    validate_precision,
)
from sml_small.utils.error_utils import (
    get_boundary_error,
    get_mandatory_param_error,
    get_one_of_params_mandatory_error,
)

# Pick up configuration for logging
log_config_path = path.join(path.dirname(path.abspath(__file__)), "../../logging.conf")
logging.config.fileConfig(log_config_path)

# Create logger
logger = logging.getLogger("SmlPythonSmallThousandPounds")


# --- Enum Definitions ---
class InputParameters(Enum):
    """
    Enum for use when accessing values from the input parameters tuple
    """

    PRINCIPAL_VARIABLE = 0
    LOWER_LIMIT = 1
    UPPER_LIMIT = 2
    TARGET_VARIABLES = 3
    UNIQUE_IDENTIFIER = 4
    PREDICTIVE = 5
    AUXILIARY = 6
    PRECISION = 7


class TpcMarker(Enum):
    """
    Enum for use when setting/comparing tpc_marker values
    """

    STOP = "S"
    CORRECTION = "C"
    NO_CORRECTION = "N"
    METHOD_PROCEED = "P"


# --- Class Definitions  ---
# Dataset holding all 'linked questions' with their initial response and final/adjusted values
@dataclass(frozen=False)
class TargetVariable:
    identifier: str  # Unique identifer e.g. a question code - q050
    original_value: Optional[str]
    final_value: Optional[str] = None


# Structure of the output dataset
@dataclass(frozen=True)
class ThousandPoundsOutput: 
    unique_identifier: Optional[str]  # Unique identifer e.g. a question code - q500
    principal_final_value: Optional[str]  # Output value that may or may not be adjusted
    target_variables: List[
        TargetVariable
    ]  # Output linked values that may or may not be adjusted
    tpc_ratio: Optional[
        str
    ]  # Ratio of the principal variable against good/predictive/aux response
    tpc_marker: str  # C = Correction applied | N = No correction applied | E = Process failure


# --- Custom Exceptions ---
class TPException(Exception):
    "Thousand Pounds error"
    pass


# --- Method Definitions ---
def thousand_pounds(
    principal_variable: float,
    upper_limit: float,
    lower_limit: float,
    target_variables: dict = {},
    unique_identifier: Optional[str] = None,
    predictive: Optional[float] = None,
    auxiliary: Optional[float] = None,
    precision: Optional[int] = None,
) -> ThousandPoundsOutput:
    """
    Calculates a pounds thousands error ratio and if the ratio is between the bounds of the given limits will adjust
    the given principal variable and any linked variables by a factor of 1000.

    :param unique_identifier: Unique identifier e.g. a question code - q500
    :type unique_identifier: Optional[String]
    :param principal_variable: Original response value provided for the 'current' period
    :type principal_variable: float
    :param predictive: Value used for 'previous' response (Returned/Imputed/Constructed)
    :type predictive: Optional[float]
    :param auxiliary: Calculated response for the 'previous' period
    :type auxiliary: Optional[float]
    :param upper_limit: Upper bound of 'error ratio' threshold
    :param upper_limit: float
    :param lower_limit: Lower bound of 'error ratio' threshold
    :type lower_limit: float
    :param target_variables: List of monetary variables that may be automatically corrected
    :type target_variables: List[Float]
    :param precision: Precision is used by the decimal package to ensure a specified accuracy
    used throughout method processing
    :type precision: Optional[int]

    :return: ThousandPoundsOutput: An object containing the
                            following attributes:
            - unique_identifier: Unique identifier e.g. a question code - q500
            - principal_original_value: Original provided value
            - principal_final_value: Output value that may or may not be adjusted
            - target_variables: Output linked values that may or may not be adjusted
            - tpc_ratio: Ratio of the principal variable against good/predictive/aux response
            - tpc_marker: C = Correction applied | N = No correction applied | S = Process Stop

    """

    log_table(
        "Input Table Function",
        unique_identifier=unique_identifier,
        principal_variable=principal_variable,
        predictive=predictive,
        auxiliary=auxiliary,
        upper_limit=upper_limit,
        lower_limit=lower_limit,
        target_variables=target_variables,
    )
    error_ratio = None
    do_adjustment = False
    principal_adjusted_value = 0
    try:
        precision = validate_input(
            predictive,
            auxiliary,
            principal_variable,
            lower_limit,
            upper_limit,
            target_variables,
            precision,
        )

        keys = [
            "principal_variable",
            "upper_limit",
            "lower_limit",
            "target_variables",
            "predictive",
            "auxiliary",
        ]

        args = [
            principal_variable,
            upper_limit,
            lower_limit,
            target_variables,
            predictive,
            auxiliary,
        ]

        decimal_values = convert_input_to_decimal(keys, args, precision)
        input_parameters = (
            decimal_values.get("principal_variable"),
            decimal_values.get("lower_limit"),
            decimal_values.get("upper_limit"),
            create_target_variable_objects(decimal_values.get("target_variables")),
            unique_identifier,
            decimal_values.get("predictive"),
            decimal_values.get("auxiliary"),
            precision,
        )

        (
            tpc_marker,
            principal_adjusted_value,
            target_variables_final,
        ) = check_zero_errors(
            input_parameters[InputParameters.PREDICTIVE.value],
            input_parameters[InputParameters.AUXILIARY.value],
            input_parameters[InputParameters.PRINCIPAL_VARIABLE.value],
            input_parameters[InputParameters.TARGET_VARIABLES.value],
        )

        if tpc_marker == TpcMarker.METHOD_PROCEED:
            predictive_value = determine_predictive_value(
                input_parameters[InputParameters.PREDICTIVE.value],
                input_parameters[InputParameters.AUXILIARY.value],
            )
            if predictive_value:
                error_ratio = calculate_error_ratio(
                    input_parameters[InputParameters.PRINCIPAL_VARIABLE.value],
                    predictive_value,
                )
                do_adjustment = is_within_threshold(
                    error_ratio,
                    input_parameters[InputParameters.LOWER_LIMIT.value],
                    input_parameters[InputParameters.UPPER_LIMIT.value],
                )

            principal_adjusted_value = (
                adjust_value(input_parameters[InputParameters.PRINCIPAL_VARIABLE.value])
                if do_adjustment
                else input_parameters[InputParameters.PRINCIPAL_VARIABLE.value]
            )
            target_variables_final = adjust_target_variables(
                do_adjustment, input_parameters[InputParameters.TARGET_VARIABLES.value]
            )
            log_table(
                "Thousand Pounds Output",
                unique_identifier=input_parameters[
                    InputParameters.UNIQUE_IDENTIFIER.value
                ],
                principal_variable=input_parameters[
                    InputParameters.PRINCIPAL_VARIABLE.value
                ],
                predictive=input_parameters[InputParameters.PREDICTIVE.value],
                auxiliary=input_parameters[InputParameters.AUXILIARY.value],
                upper_limit=input_parameters[InputParameters.UPPER_LIMIT.value],
                lower_limit=input_parameters[InputParameters.LOWER_LIMIT.value],
                target_variables=input_parameters[
                    InputParameters.TARGET_VARIABLES.value
                ],
                tpc_marker=tpc_marker.value,
            )
        else:
            log_table(
                "Thousand Pounds Output",
                unique_identifier=input_parameters[
                    InputParameters.UNIQUE_IDENTIFIER.value
                ],
                principal_variable=input_parameters[
                    InputParameters.PRINCIPAL_VARIABLE.value
                ],
                predictive=input_parameters[InputParameters.PREDICTIVE.value],
                auxiliary=input_parameters[InputParameters.AUXILIARY.value],
                upper_limit=input_parameters[InputParameters.UPPER_LIMIT.value],
                lower_limit=input_parameters[InputParameters.LOWER_LIMIT.value],
                target_variables=input_parameters[
                    InputParameters.TARGET_VARIABLES.value
                ],
                tpc_marker=tpc_marker.value,
            )

        target_variables_final = clean_target_variables(target_variables_final)

        return ThousandPoundsOutput(
            unique_identifier=str(unique_identifier),
            principal_final_value=str(principal_adjusted_value)
            if principal_adjusted_value is not None
            else principal_adjusted_value,
            target_variables=target_variables_final,
            tpc_ratio=str(error_ratio) if error_ratio is not None else error_ratio,
            tpc_marker=determine_tpc_marker(do_adjustment, tpc_marker),
        )

    except (
        Exception
    ) as error:  # Catch any underlying errors and return a coherent output dataset
        # Ensure we populate the output target variables with the same output values as originally given
        log_table(
            "Thousand Pounds Error",
            unique_identifier=unique_identifier,
            principal_variable=principal_variable,
            predictive=predictive,
            auxiliary=auxiliary,
            upper_limit=upper_limit,
            lower_limit=lower_limit,
            target_variables=target_variables,
        )
        if unique_identifier is None:
            unique_identifier = "N/A"
        raise TPException(f"identifier: {unique_identifier}", error)


def clean_target_variables(
    target_variables_final: List[TargetVariable],
) -> List[TargetVariable]:
    """
    Takes a list of target variables and updates not a number values to be returned as nan

    :param target_variables_final: List containing values to become TargetVariable objects
    :type target_variables: List[TargetVariables]

    :return: target_variables_final, a list of TargetVariable objects
    :rtype: List[TargetVariable]
    """
    for target_variable in target_variables_final:
        # Check and update the values recorded as NaN
        if str(target_variable.original_value) == "NaN":
            target_variable.original_value = float("NaN")

        if str(target_variable.final_value) == "NaN":
            target_variable.final_value = float("NaN")

    return target_variables_final


def create_target_variable_objects(target_variables: dict) -> List[TargetVariable]:
    """
    Takes a dictionary of target variables, where key is the identifier and value is the original value and
    creates a list of target_variable objects to be used by the method

    :param target_variables: Dictionary containing values to become TargetVariable objects
    :type target_variables: dict

    :return: target_variables_list, a list of TargetVariable objects
    :rtype: List[TargetVariable]
    """
    target_variables_list = []
    for key, value in target_variables.items():
        target_variables_list.append(TargetVariable(key, value))

    return target_variables_list


def validate_input(
    predictive: Optional[float],
    auxiliary: Optional[float],
    principal_variable: float,
    lower_limit: float,
    upper_limit: float,
    target_variables: dict,
    precision: Optional[int],
) -> int:
    """
    This function is used to validate the data passed to the thousand_pounds
    method ensuring that the values are present when expected and that they are of
    the correct type. If invalid data is received then an appropriate exception is
    raised.

    :param predictive:  Value used for 'previous' response (Returned/Imputed/Constructed)
    :type predictive: Optional[float]
    :param auxiliary: Calculated response for the 'previous' period
    :type auxiliary: Optional[float]
    :param principal_variable: Original response value provided for the 'current' period
    :type principal_variable: float
    :param lower_limit: Lower bound of 'error ratio' threshold
    :type lower_limit: float
    :param upper_limit: Upper bound of 'error ratio' threshold
    :type upper_limit: float
    :param target_variables: Dictionary of monetary variables that may be automatically corrected
    :type target_variables: Dictionary
    :param precision: Precision is used by the decimal package to perform calculations to the specified accuracy.
    :type precision: int

    :return: predictive is returned as a converted float
    :rtype: float | None
    :return: auxiliary is returned as a converted float
    :rtype: float | None
    :return: principal_variable is returned as a converted float
    :rtype: float
    :return: lower_limit is returned as a converted float
    :rtype: float
    :return: upper_limit is returned as a converted float
    :rtype: float
    :return: computed precision
    :rtype: int
    """
    if predictive:
        validate_number("predictive", predictive)
    if auxiliary:
        validate_number("auxiliary", auxiliary)
    if predictive is None and auxiliary is None:
        raise ValueError(get_one_of_params_mandatory_error(["predictive", "auxiliary"]))
    if principal_variable is None:
        raise ValueError(get_mandatory_param_error("principal_variable"))
    else:
        validate_number("principal_variable", principal_variable)
    if not lower_limit:
        raise ValueError(get_mandatory_param_error("lower_limit"))
    else:
        validate_number("lower_limit", lower_limit)
    if not upper_limit:
        raise ValueError(get_mandatory_param_error("upper_limit"))
    else:
        validate_number("upper_limit", upper_limit)
    if float(lower_limit) >= float(upper_limit):
        raise ValueError(get_boundary_error([lower_limit, upper_limit]))
    for key, value in target_variables.items():
        if value is not None:
            validate_number(key, value)
    final_precision = validate_precision(precision)
    return final_precision


def check_zero_errors(
    predictive: Optional[Decimal],
    auxiliary: Optional[Decimal],
    principal_variable: Optional[Decimal],
    target_variables: List[TargetVariable],
) -> Tuple[TpcMarker, Decimal, List[TargetVariable]]:
    """
    Checks predictive and auxiliary to ensure that there is not only a 0 value available,
    as this will cause a divide by 0 error

    :param predictive: Value used for 'previous' response (Returned/Imputed/Constructed)
    :type predictive: Optional[Decimal]
    :param auxiliary: Calculated response for the 'previous' period
    :type auxiliary: Optional[Decimal]
    :param principal_variable: Original response value provided for the 'current' period
    :type principal_variable: Optional[Decimal]
    :param target_variables: list of TargetVariable objects that can be corrected
    :type target_variables: List[TargetVariable],

    :return: tpc_marker, either method_proceed or stop
    :rtype: TpcMarker
    :return: checked_principal_variable, Decimal value
    :rtype: Decimal
    :return: checked_target_variables, list of variables
    :rtype: List[TargetVariable]
    """
    tpc_marker = TpcMarker.METHOD_PROCEED

    checked_target_variables = target_variables

    checked_principal_variable = principal_variable

    if (predictive is None or predictive == 0) and (
        auxiliary is None or auxiliary == 0
    ):
        tpc_marker = TpcMarker.STOP
        logger.warning(f"TPCMarker = STOP at line:{sys._getframe().f_back.f_lineno}")

        checked_target_variables = []

        for question in target_variables:
            final_value = question.original_value
            checked_target_variables.append(
                TargetVariable(
                    identifier=question.identifier,
                    original_value=str(question.original_value)
                    if question.original_value is not None
                    else question.original_value,
                    final_value=str(final_value)
                    if final_value is not None
                    else final_value,
                )
            )

    return tpc_marker, checked_principal_variable, checked_target_variables


def determine_tpc_marker(do_adjustment: bool, tpc_marker: TpcMarker) -> str:
    """
    Determine correction marker that should be output, "C" if values can be corrected, "N" if not.

    :param do_adjustment: Marker for if principal variable falls within adjustable range
    :type do_adjustment: bool
    :param tpc_marker: current TPC marker
    :type: TpcMarker

    :return: "C", "N" or "S"
    :rtype: char
    """
    if tpc_marker is TpcMarker.STOP:
        return tpc_marker.value
    else:
        return (
            TpcMarker.CORRECTION.value
            if do_adjustment
            else TpcMarker.NO_CORRECTION.value
        )


def determine_predictive_value(
    predictive: Optional[Decimal], auxiliary: Optional[Decimal]
) -> Decimal:
    """
    Determine which value to use as the predictive value, predictive if input or auxiliary if no predictive is
    available

    :param predictive: Value used for 'previous' response (Returned/Imputed/Constructed)
    :type predictive: Optional[Decimal]
    :param auxiliary: Calculated response for the 'previous' period
    :type auxiliary: Optional[Decimal]

    :return: Either the input predictive or auxiliary value, which has been determined to used for the rest
     of the method
    :rtype: Decimal
    """
    if predictive:
        return predictive
    else:
        return auxiliary


def calculate_error_ratio(
    principal_variable: Decimal, predictive_value: Decimal
) -> Decimal:
    """
    Calculate the ratio for an acceptable error.

    :param principal_variable: Original response value provided for the 'current' period
    :type principal_variable: Decimal
    :param predictive_value: Either the input predictive or auxiliary value
    :type predictive_value: Decimal

    :return: principal_variable / predictive_value, the calculated acceptable error ratio
    :rtype: Decimal
    """
    return principal_variable / predictive_value  # predictive is already validated


# Calculate the error value and determine whether the adjustment should be made
def is_within_threshold(
    error_ratio: Decimal, lower_limit: Decimal, upper_limit: Decimal
) -> bool:
    """
    Determines if the error ratio is within the lower and upper limit input

    :param error_ratio: Previously determined error ratio in "calculate_error_ratio"
    :type error_ratio: Decimal
    :param lower_limit: Lower bound of 'error ratio' threshold
    :type lower_limit: Decimal
    :param upper_limit: Upper bound of 'error ratio' threshold
    :type upper_limit: Decimal

    :return: Boolean, True if error ratio is between lower and upper limits
    :rtype: Bool
    """
    if lower_limit < error_ratio < upper_limit:
        return True
    return False  # Outside the bounds of the threshold, do not adjust


# Perform the calculation to adjust the response value
def adjust_value(value: Optional[Decimal]) -> Optional[Decimal]:
    """
    Method to calculate the adjustment of the response value

    :param value: response value to adjust
    :type value: Decimal

    :return: adjusted value post calculation
    :rtype: Decimal
    """
    if value is not None:
        return value / 1000  # Do not adjust missing/null responses


def adjust_target_variables(
    do_adjustment: bool, target_variables: List[TargetVariable]
) -> List[TargetVariable]:
    """
    Method to amend the variables within the target_variables list and append the new values to the individual objects

    :param do_adjustment: Determines if the values should be corrected
    :type do_adjustment: bool
    :param target_variables: list of TargetVariable objects that can be corrected
    :type target_variables: List[TargetVariable]

    :return: A returned list of target variables with the final_value updated with either the corrected value, or the
    original value if no correction is to be made
    :rtype: List[TargetVariable]
    """
    adjusted_target_variables = []

    for question in target_variables:
        if do_adjustment:
            final_value = adjust_value(question.original_value)
        else:
            final_value = question.original_value
        adjusted_target_variables.append(
            TargetVariable(
                identifier=question.identifier,
                original_value=str(question.original_value)
                if question.original_value is not None
                and not math.isnan(question.original_value)
                else question.original_value,
                final_value=str(final_value)
                if final_value is not None and not math.isnan(final_value)
                else final_value,
            )
        )
    return adjusted_target_variables
