from dataclasses import dataclass
from typing import Optional, List


# Input dataset holding all 'linked questions' with their response values
@dataclass(frozen=True)
class Response:
    question: str  # Question identifer e.g. a question code - q500
    response: Optional[float]  # Original response value provided


# Input dataset for the complete config and responses
@dataclass(frozen=True)
class Thousands_config:
    primary_question: str  # Question identifer
    current_value: Optional[float]  # Original response value provided for the 'current' period
    previous_value: Optional[float]  # Original cleared/valid response from the 'previous' period
    predicted_value: Optional[float]  # Imputed/Constructed response for the 'previous' period
    aux_value: Optional[float]  # Calculated response for the 'previous' period
    threshold_upper: float  # Upper bound of 'error value' threshold
    threshold_lower: float  # Lower bound of 'error value' threshold
    linked_questions: List[Response]  # All questions and responses associated with primary question


@dataclass(frozen=True)
class Thousands_output:
    question: str  # Question identifer e.g. a question code - q500
    original_value: Optional[float]  # Original response value provided
    adjusted_value: Optional[float]  # Updated/Adjusted response value
    is_adjusted: Optional[bool]  # Flag to indicate whether adjustment took place


# Process through the config and run the pounds thousands method
def run(configs: List[Thousands_config]) -> List[Thousands_output]:

    output = []
    for config in configs:

        do_adjustment = is_within_threshold(config)
        output.append(set_adjusted_figure(config.primary_question, config.current_value, do_adjustment))

        for question in config.linked_questions:
            output.append(set_adjusted_figure(question.question, question.response, do_adjustment))

    return output


# Calculate the error value and determine whether the adjustment should be made
def is_within_threshold(config: Thousands_config) -> Optional[bool]:

    if config.current_value is None:
        return  # We have a null/missing value so we are not adjusting this response or any of the linked

    previous_value = determine_previous_value(config)
    if not previous_value:
        return  # We do not have a non-zero figure for the previous period so we are not adjusting

    question_error = config.current_value / previous_value
    print(f"Primary question: {config.primary_question} -- Formula: {question_error} = {config.current_value} / {previous_value}")

    if (question_error > config.threshold_lower) and (question_error < config.threshold_upper):
        return True

    return False  # Outside the bounds of the threshold, do not adjust


# Perform the calculation to adjust the response value
def adjust_value(value: Optional[float]) -> Optional[float]:
    if value is None:
        return None  # Do not adjust missing/null responses
    return value / 1000


# Determine whether to adjust each response then populate the output dataset with the outcome
def set_adjusted_figure(question: str, original_value: Optional[float], do_adjustment: Optional[bool]) -> Thousands_output:
    adjusted_value = adjust_value(original_value) if do_adjustment else original_value
    return Thousands_output(question=question, original_value=original_value, adjusted_value=adjusted_value, is_adjusted=do_adjustment)


# Parse through each of the potential values and pick them in priority order
def determine_previous_value(config: Thousands_config) -> Optional[float]:
    if config.previous_value:
        return config.previous_value
    elif config.predicted_value:
        return config.predicted_value
    elif config.aux_value:
        return config.aux_value


##################################

# form_id | primary_question | linked_questions | lower_threshold | upper_threshold

##################################
