from dataclasses import dataclass
from typing import List, Optional


# Dataset holding all 'linked questions' with their initial response and final/adjusted values
@dataclass(frozen=True)
class Target_variable:
    identifier: str  # Unique identifer e.g. a question code - q050
    original_value: Optional[float]
    final_value: Optional[float] = None


# Structure of the output dataset
@dataclass(frozen=True)
class Thousands_output:
    principal_identifier: Optional[str]  # Unique identifer e.g. a question code - q500
    principal_original_value: float  # Original provided value
    principal_final_value: Optional[float]  # Output value that may or may not be adjusted
    target_variables: List[Target_variable]  # Output linked values that may or may not be adjusted
    tpc_ratio: Optional[float]  # Ratio of the principal variable against good/predictive/aux response
    tpc_marker: str  # C = Correction applied | N = No correction applied | E = Process failure
    error_description: str = ""  # Error information populated as required


# Process through the config and run the pounds thousands method
def run(
    principal_identifier: Optional[str],  # Unique identifer e.g. a question code - q500
    principal_variable: float,  # Original response value provided for the 'current' period
    predictive: Optional[float],  # Value used for 'previous' response (Returned/Imputed/Constructed)
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
        predictive_value = determine_predictive_value(predictive, auxiliary)
        if predictive_value:  # Allow the case where given predictive = 0 and aux is missing to be a valid case
            error_ratio = calculate_error_ratio(principal_variable, predictive_value)
            do_adjustment = is_within_threshold(error_ratio, lower_limit, upper_limit)

        principal_adjusted_value = adjust_value(principal_variable) if do_adjustment else principal_variable
        target_variables_final = adjust_target_variables(do_adjustment, target_variables)

        return Thousands_output(
            principal_identifier=principal_identifier,
            principal_original_value=principal_variable,
            principal_final_value=principal_adjusted_value,
            target_variables=target_variables_final,
            tpc_ratio=error_ratio,
            tpc_marker=determine_tpc_marker(do_adjustment),
        )

    except Exception as error:  # Catch any underlying errors and return a coherent output dataset

        # Ensure we populate the output target variables with the same output values as originally given
        target_variables_final = []
        for question in target_variables:
            target_variables_final.append(
                Target_variable(identifier=question.identifier, original_value=question.original_value, final_value=question.original_value)
            )

        return Thousands_output(
            principal_identifier=principal_identifier,
            principal_original_value=principal_variable,
            principal_final_value=principal_variable,  # Always return the final output as the same as the input
            target_variables=target_variables_final,
            tpc_ratio=None,
            tpc_marker="E",
            error_description=f"{error}",
        )


def determine_tpc_marker(do_adjustment: bool) -> str:
    return "C" if do_adjustment else "N"


def determine_predictive_value(predictive: Optional[float], auxiliary: Optional[float]) -> float:
    if predictive:
        validate_number("predictive", predictive)
        return float(predictive)
    if auxiliary:
        validate_number("auxiliary", auxiliary)
        return float(auxiliary)
    if predictive == 0:  # Allow us to handle case when predictive = 0 and Aux is missing which is not an error
        return 0
    raise ValueError("Both predictive and auxiliary values are missing")


def calculate_error_ratio(principal_variable: float, predictive_value: float) -> float:
    if principal_variable is None:
        raise ValueError("principal_variable is missing")
    validate_number("principal_variable", principal_variable)
    if not predictive_value:
        raise ValueError("predictive_value is 0/missing")
    return float(principal_variable) / float(predictive_value)  # predictive is already validated


# Calculate the error value and determine whether the adjustment should be made
def is_within_threshold(error_ratio: float, lower_limit: float, upper_limit: float) -> bool:

    if not lower_limit or not upper_limit:
        raise ValueError("At least one of the lower or upper limits are 0 or missing")
    validate_number("lower_limit", lower_limit)
    validate_number("upper_limit", upper_limit)

    if float(lower_limit) > float(upper_limit):
        raise ValueError(f"Lower limit is larger than the upper limit ({lower_limit}:{upper_limit})")

    if float(error_ratio) > float(lower_limit) and float(error_ratio) < float(upper_limit):
        return True
    return False  # Outside the bounds of the threshold, do not adjust


# Perform the calculation to adjust the response value
def adjust_value(value: Optional[float]) -> Optional[float]:
    if value is not None:
        return float(value) / 1000  # Do not adjust missing/null responses


def validate_number(description: str, input) -> bool:
    if not isNumber(input):
        raise ValueError(f"Attribute '{description}' is missing or not a valid number")
    return True


# Validate that the provided attribute is a number
def isNumber(input) -> bool:
    try:
        float(input)
    except Exception:
        return False
    return True


def adjust_target_variables(do_adjustment: bool, target_variables: List[Target_variable]) -> List[Target_variable]:
    adjusted_target_variables = []
    for question in target_variables:
        if do_adjustment and validate_number(question.identifier, question.original_value):
            final_value = round(adjust_value(question.original_value), 2)
        else:
            final_value = question.original_value
        adjusted_target_variables.append(Target_variable(identifier=question.identifier, original_value=question.original_value, final_value=final_value))
    return adjusted_target_variables
