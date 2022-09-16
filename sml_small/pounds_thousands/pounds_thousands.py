from dataclasses import dataclass
from typing import Optional, List


# Dataset holding all 'linked questions' with their response/adjusted values
@dataclass(frozen=True)
class Target_variable:
    identifier: str  # Unique identifer e.g. a question code - q050
    value: Optional[float]  # Response/adjusted value


# Structure of the output dataset
@dataclass(frozen=True)
class Thousands_output:
    principle_identifier: Optional[str]  # Unique identifer e.g. a question code - q500
    principle_final_value: float  # Output value that may or may not be adjusted
    target_variables: List[Target_variable]  # Output linked values that may or may not be adjusted
    ratio: Optional[float]  # Ratio of the principle variable against good/predicted/aux response
    tpc_marker: str  # C = Correction applied | N = No correction applied | E = Process failure
    error: str = ""  # Error information populated as required


# Process through the config and run the pounds thousands method
def run(
    principle_identifier: Optional[str],  # Unique identifer e.g. a question code - q500
    principle_variable: float,  # Original response value provided for the 'current' period
    predicted: Optional[float],  # Value used for 'previous' response (Returned/Imputed/Constructed)
    auxiliary: Optional[float],  # Calculated response for the 'previous' period
    upper_limit: float,  # Upper bound of 'error ratio' threshold
    lower_limit: float,  # Lower bound of 'error ratio' threshold
    target_variables: List[Target_variable],
) -> Thousands_output:
    """
    Calculates a pounds thousands error ratio and if the ration is between the bounds of the given limits will adjust
    the given principle variable and any linked variables by a factor of 1000.
    """

    try:
        predictive_value = determine_predictive_value(predicted, auxiliary)

        error_ratio = calculate_error_ratio(principle_variable, predictive_value)
        do_adjustment = is_within_threshold(error_ratio, lower_limit, upper_limit)
        principle_final_value = adjust_value(principle_variable) if do_adjustment else principle_variable

        target_variables_final = []
        for question in target_variables:
            final_value = adjust_value(question.value) if do_adjustment else question.value
            target_variables_final.append(Target_variable(identifier=question.identifier, value=final_value))

        output = Thousands_output(
            principle_identifier=principle_identifier,
            principle_final_value=principle_final_value,
            target_variables=target_variables_final,
            ratio=error_ratio,
            tpc_marker=determine_tpc_marker(do_adjustment),
        )

    except Exception as error:  # Catch any underlying errors and return a coherent output dataset
        output = Thousands_output(
            principle_identifier=principle_identifier,
            principle_final_value=principle_variable,
            target_variables=target_variables,
            tpc_marker="E",
            ratio=None,
            error=f"{error}",
        )

    return output


def determine_tpc_marker(do_adjustment: bool) -> str:
    if do_adjustment:
        return "C"
    return "N"


def determine_predictive_value(predicted: Optional[float], auxiliary: Optional[float]) -> float:
    if predicted:
        return predicted
    if auxiliary:
        return auxiliary
    raise ValueError("Both predicted and auxiliary values are missing/zero")


def calculate_error_ratio(principle_variable: float, predictive_value: float) -> float:
    if principle_variable is None:
        raise ValueError("Principle_variable is missing")
    if not predictive_value:
        raise ValueError("predictive_value is zero/missing")
    return principle_variable / predictive_value


# Calculate the error value and determine whether the adjustment should be made
def is_within_threshold(error_ratio: float, lower_limit: float, upper_limit: float) -> bool:

    if not lower_limit and not upper_limit:
        raise ValueError("The lower and upper limits are both 0")

    if (error_ratio > lower_limit) and (error_ratio < upper_limit):
        return True
    return False  # Outside the bounds of the threshold, do not adjust


# Perform the calculation to adjust the response value
def adjust_value(value: Optional[float]) -> Optional[float]:
    if value is None:
        return None  # Do not adjust missing/null responses
    return value / 1000
