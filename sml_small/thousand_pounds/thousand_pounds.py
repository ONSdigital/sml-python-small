from dataclasses import dataclass
from typing import List, Optional


# Dataset holding all 'linked questions' with their response/adjusted values
@dataclass(frozen=True)
class Target_variable:
    identifier: str  # Unique identifer e.g. a question code - q050
    original_value: Optional[float]
    adjusted_value: Optional[float] = None


# Structure of the output dataset
@dataclass(frozen=True)
class Thousands_output:
    principal_identifier: Optional[str]  # Unique identifer e.g. a question code - q500
    principal_original_value: float  # Original provided value
    principal_adjusted_value: Optional[float]  # Output value that may or may not be adjusted
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

    try:
        predictive_value = determine_predictive_value(predictive, auxiliary)

        error_ratio = calculate_error_ratio(principal_variable, predictive_value)
        do_adjustment = is_within_threshold(error_ratio, lower_limit, upper_limit)
        principal_adjusted_value = adjust_value(principal_variable) if do_adjustment else principal_variable

        target_variables_final = []
        for question in target_variables:
            final_value = adjust_value(question.original_value) if do_adjustment else question.original_value
            target_variables_final.append(Target_variable(identifier=question.identifier, original_value=question.original_value, adjusted_value=final_value))

        output = Thousands_output(
            principal_identifier=principal_identifier,
            principal_original_value=principal_variable,
            principal_adjusted_value=principal_adjusted_value,
            target_variables=target_variables_final,
            tpc_ratio=error_ratio,
            tpc_marker=determine_tpc_marker(do_adjustment),
        )

    except Exception as error:  # Catch any underlying errors and return a coherent output dataset
        output = Thousands_output(
            principal_identifier=principal_identifier,
            principal_original_value=principal_variable,
            principal_adjusted_value=None,
            target_variables=target_variables,
            tpc_ratio=None,
            tpc_marker="E",
            error_description=f"{error}",
        )

    return output


def determine_tpc_marker(do_adjustment: bool) -> str:
    if do_adjustment:
        return "C"
    return "N"


def determine_predictive_value(predictive: Optional[float], auxiliary: Optional[float]) -> float:
    if predictive:
        return predictive
    if auxiliary:
        return auxiliary
    raise ValueError("Both predictive and auxiliary values are missing/zero")


def calculate_error_ratio(principal_variable: float, predictive_value: float) -> float:
    if principal_variable is None:
        raise ValueError("principal_variable is missing")
    if not predictive_value:
        raise ValueError("predictive_value is zero/missing")
    return principal_variable / predictive_value


# Calculate the error value and determine whether the adjustment should be made
def is_within_threshold(error_ratio: float, lower_limit: float, upper_limit: float) -> bool:

    if not lower_limit or not upper_limit:
        raise ValueError("At least one of the lower or upper limits are 0 or missing")

    if (error_ratio > lower_limit) and (error_ratio < upper_limit):
        return True
    return False  # Outside the bounds of the threshold, do not adjust


# Perform the calculation to adjust the response value
def adjust_value(value: Optional[float]) -> Optional[float]:
    if value is None:
        return None  # Do not adjust missing/null responses
    return value / 1000
