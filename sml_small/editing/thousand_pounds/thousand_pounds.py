from dataclasses import dataclass
from enum import Enum
from typing import List, Optional, Tuple, Union

from sml_small.utils.common_utils import validate_number
from sml_small.utils.error_utils import get_boundary_error, get_mandatory_param_error, get_one_of_params_mandatory_error

# --- Enum Definitions ---
class InputParameters(Enum):
    """
    Enum for use when accessing values from the input parameters tuple
    """

    PREDICTIVE = 0
    AUXILIARY = 1
    PRINCIPAL_VARIABLE = 2
    LOWER_LIMIT = 3
    UPPER_LIMIT = 4
    TARGET_VARIABLES = 5


# --- Class Definitions  ---
# Dataset holding all 'linked questions' with their initial response and final/adjusted values
@dataclass(frozen=False)
class Target_variable:
    identifier: str  # Unique identifer e.g. a question code - q050
    original_value: Optional[float]
    final_value: Optional[float] = None


# Structure of the output dataset
@dataclass(frozen=True)
class Thousands_output:
    principal_identifier: Optional[str]  # Unique identifer e.g. a question code - q500
    principal_original_value: float  # Original provided value
    principal_final_value: Optional[
        float
    ]  # Output value that may or may not be adjusted
    target_variables: List[
        Target_variable
    ]  # Output linked values that may or may not be adjusted
    tpc_ratio: Optional[
        float
    ]  # Ratio of the principal variable against good/predictive/aux response
    tpc_marker: str  # C = Correction applied | N = No correction applied | E = Process failure


# --- Custom Exceptions ---
class TPException(Exception):
    "Thousand Pounds error"
    pass


# --- Method Definitions ---
def run(
    principal_identifier: Optional[str],  # Unique identifer e.g. a question code - q500
    principal_variable: float,  # Original response value provided for the 'current' period
    predictive: Optional[
        float
    ],  # Value used for 'previous' response (Returned/Imputed/Constructed)
    auxiliary: Optional[float],  # Calculated response for the 'previous' period
    upper_limit: float,  # Upper bound of 'error ratio' threshold
    lower_limit: float,  # Lower bound of 'error ratio' threshold
    target_variables: List[Target_variable],
) -> Thousands_output:
    """
    Calculates a pounds thousands error ratio and if the ration is between the bounds of the given limits will adjust
    the given principal variable and any linked variables by a factor of 1000.
    """

    error_ratio = None
    do_adjustment = False
    try:
        input_parameters = validate_input(
            predictive,
            auxiliary,
            principal_variable,
            lower_limit,
            upper_limit,
            target_variables,
        )

        predictive_value = determine_predictive_value(
            input_parameters[InputParameters.PREDICTIVE.value],
            input_parameters[InputParameters.AUXILIARY.value],
        )
        if (
            predictive_value
        ):
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

        return Thousands_output(
            principal_identifier=principal_identifier,
            principal_original_value=input_parameters[
                InputParameters.PRINCIPAL_VARIABLE.value
            ],
            principal_final_value=principal_adjusted_value,
            target_variables=target_variables_final,
            tpc_ratio=error_ratio,
            tpc_marker=determine_tpc_marker(do_adjustment),
        )

    except (
        Exception
    ) as error:  # Catch any underlying errors and return a coherent output dataset
        # Ensure we populate the output target variables with the same output values as originally given
        target_variables_final = []
        if principal_identifier is None:
            principal_identifier = "N/A"
        raise TPException(f"identifier: {principal_identifier}", error)


def validate_input(
    predictive: Optional[float],
    auxiliary: Optional[float],
    principal_variable:  float,
    lower_limit: float,
    upper_limit: float,
    target_variables: List[Target_variable],
) -> Tuple[
    Union[float, None],
    Union[float, None],
    float,
    float,
    float,
    List[Target_variable],
]:

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
    :param target_variables: List of monetary variables that may be automatically corrected
    :type target_variables: List[Targer_variable]

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
    :return: target_variables, target_variable.original_value is returned as a converted float
    :rtype: List[Target_variable]
    """
    if predictive and validate_number("predictive", predictive):
        predictive = float(predictive)
    if auxiliary and validate_number("auxiliary", auxiliary):
        auxiliary = float(auxiliary)
    if predictive is None and auxiliary is None:
        raise ValueError(get_one_of_params_mandatory_error(["predictive", "auxiliary"]))
    if principal_variable is None:
        raise ValueError(get_mandatory_param_error("principal_variable"))
    elif validate_number("principal_variable", principal_variable) is True:
        principal_variable = float(principal_variable)
    if not lower_limit:
        raise ValueError(get_mandatory_param_error("lower_limit"))
    elif validate_number("lower_limit", lower_limit) is True:
        lower_limit = float(lower_limit)
    if not upper_limit:
        raise ValueError(get_mandatory_param_error("upper_limit"))
    elif validate_number("upper_limit", upper_limit) is True:
        upper_limit = float(upper_limit)
    if float(lower_limit) >= float(upper_limit):
        raise ValueError(get_boundary_error([lower_limit, upper_limit]))
    for question in target_variables:
        if validate_number(question.identifier, question.original_value) is True:
            question.original_value = float(question.original_value)
    return (
        predictive,
        auxiliary,
        principal_variable,
        lower_limit,
        upper_limit,
        target_variables,
    )


def determine_tpc_marker(do_adjustment: bool) -> str:
    return "C" if do_adjustment else "N"


def determine_predictive_value(
    predictive: Optional[float], auxiliary: Optional[float]
) -> float:
    if predictive or predictive == 0:
        return predictive
    if auxiliary:
        return auxiliary


def calculate_error_ratio(principal_variable: float, predictive_value: float) -> float:
    return principal_variable / predictive_value  # predictive is already validated


# Calculate the error value and determine whether the adjustment should be made
def is_within_threshold(
    error_ratio: float, lower_limit: float, upper_limit: float
) -> bool:
    if lower_limit < error_ratio < upper_limit:
        return True
    return False  # Outside the bounds of the threshold, do not adjust


# Perform the calculation to adjust the response value
def adjust_value(value: Optional[float]) -> Optional[float]:
    if value is not None:
        return value / 1000  # Do not adjust missing/null responses


def adjust_target_variables(
    do_adjustment: bool, target_variables: List[Target_variable]
) -> List[Target_variable]:
    adjusted_target_variables = []
    for question in target_variables:
        if do_adjustment:
            final_value = round(adjust_value(question.original_value), 2)
        else:
            final_value = question.original_value
        adjusted_target_variables.append(
            Target_variable(
                identifier=question.identifier,
                original_value=question.original_value,
                final_value=final_value,
            )
        )
    return adjusted_target_variables
