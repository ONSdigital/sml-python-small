from dataclasses import dataclass
from enum import Enum
from typing import List, Optional, Tuple


class Index(Enum):
    LOW_THRESHOLD = 0
    HIGH_THRESHOLD = 1


class TccMarker(Enum):
    STOP = "S"
    MANUAL = "M"
    TOTAL_CORRECTED = "T"
    COMPONENTS_CORRECTED = "C"
    NO_CORRECTION = "N"
    METHOD_PROCEED = "P"


@dataclass(frozen=True)
class Component_list:
    original_value: Optional[float]
    final_value: Optional[float] = None


@dataclass(frozen=True)
class Totals_and_Components_Output:
    identifier: Optional[
        str
    ]  # unique identifier, e.g Business Reporting Unit SG-should this be optiional?
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
) -> bool:
    raise NotImplementedError(f"{validate_input.__name__}() not implemented yet")


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
    tcc_marker = None
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
    tcc_marker = None
    if predictive > 0 and components_sum == 0:
        tcc_marker = TccMarker.STOP.value
    else:
        tcc_marker = TccMarker.METHOD_PROCEED.value
    return tcc_marker


def check_sum_components_predictive(predictive: float, components_sum: float) -> bool:
    raise NotImplementedError(
        f"{check_sum_components_predictive.__name__}() not implemented yet"
    )


def determine_error_detection(
    absolute_difference_threshold: Optional[float],
    percentage_difference_threshold: Optional[float],
    absolute_difference: float,
    predictive: float,
    thresholds: tuple,
) -> str:
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
    error_detection_satisfiable = False
    if absolute_difference_threshold is not None:
        error_detection_satisfiable = check_absolute_difference_threshold(
            absolute_difference_threshold, absolute_difference
        )
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
    return tcc_marker


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
) -> bool:
    raise NotImplementedError(f"{error_correction.__name__}() not implemented yet")


def correct_total(
    components_sum: float, original_components: List[Component_list]
) -> bool:
    raise NotImplementedError(f"{correct_total.__name__}() not implemented yet")


def correct_components(
    components_sum: float, original_components: List[Component_list], predictive: float
) -> bool:
    raise NotImplementedError(f"{correct_components.__name__}() not implemented yet")


def sum_components(components: list[Component_list]) -> float:
    total_sum = 0.0

    for component in components:
        total_sum += component.original_value

    print(total_sum)

    return total_sum


def calculate_percent_threshold(
    sum_of_components: float, percentage_threshold: float
) -> Tuple[float, float]:
    low_percent_threshold = sum_of_components - (sum_of_components / percentage_threshold)
    high_percent_threshold = sum_of_components + (sum_of_components / percentage_threshold)

    return low_percent_threshold, high_percent_threshold


def totals_and_components(
    identifier: Optional[
        str
    ],  # unique identifier, e.g Business Reporting Unit SG-should this be optiional?
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
    predictive, tcc_marker = check_predictive_value(predictive, auxiliary)
    if tcc_marker == TccMarker.METHOD_PROCEED.value:
        component_total = sum_components(components=components)
        absolute_difference = component_total - predictive
        tcc_marker = check_zero_errors(predictive, component_total)
        if tcc_marker == TccMarker.METHOD_PROCEED.value:
            thresholds = calculate_percent_threshold(
                component_total, percentage_difference_threshold
            )
            tcc_marker = determine_error_detection(absolute_difference_threshold,
                                                   percentage_difference_threshold,
                                                   absolute_difference,
                                                   predictive,
                                                   thresholds)
            if tcc_marker == TccMarker.METHOD_PROCEED.value:
                pass
            else:
                # Manual correction, output
                pass
        else:
            # calc stopped, output
            pass
    else:
        # calc stopped output
        pass

    output: Totals_and_Components_Output = Totals_and_Components_Output(
        identifier=identifier,
        period=period,
        absolute_difference=absolute_difference,
        low_percent_threshold=thresholds[Index.LOW_THRESHOLD.value],
        high_percent_threshold=thresholds[Index.HIGH_THRESHOLD.value],
        final_total=predictive,
        final_components=components,
        tcc_marker="T",
    )

    output.print_output_table()

    return output
