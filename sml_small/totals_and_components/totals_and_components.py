from dataclasses import dataclass
from enum import Enum
from typing import List, Optional, Tuple


class Index(Enum):
    LOW_THRESHOLD = 0
    HIGH_THRESHOLD = 1


@dataclass(frozen=True)
class Component_list:
    original_value: Optional[float]
    final_value: Optional[float] = None


@dataclass(frozen=True)
class Totals_and_Components_Output:
    identifier: Optional[str]  # unique identifier, e.g Business Reporting Unit SG-should this be optiional?
    period: Optional[str]  # not used in initial PoC always assume current period
    absolute_difference: float  # this is the absolute value showing the difference between the components input and
    # the predictive total
    low_percent_threshold: Optional[float]  # the sum of the input components minus the absolute percentage difference
    high_percent_threshold: Optional[float]  # the sum of the input components plus the absolute percentage difference
    final_total: float  # the output total which may have been corrected based on user input amend_total variable
    final_components: List[Component_list]  # the output components which may have been corrected to match the received
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


def sum_components(components: Component_list) -> float:
    total_sum = 0.0

    for component in components:
        total_sum += component.original_value

    print(total_sum)

    return total_sum


def calculate_percent_threshold(sum_components: float, percentage_threshold: float) -> Tuple[float, float]:

    low_percent_threshold = sum_components - (sum_components / percentage_threshold)
    high_percent_threshold = sum_components + (sum_components / percentage_threshold)

    return low_percent_threshold, high_percent_threshold


def totals_and_components(
        identifier: Optional[str],  # unique identifier, e.g Business Reporting Unit SG-should this be optiional?
        period: Optional[str],
        total: float,
        components: List[Component_list],
        amend_total: bool,
        predictive: Optional[float],
        predictive_period: Optional[str],  # not used in initial PoC always assume current period
        auxiliary: Optional[float],
        absolute_difference_threshold: Optional[float],
        percentage_difference_threshold: Optional[float]
        ) -> Totals_and_Components_Output:

    """
    Calculates totals and components based on the given parameters.

    Parameters:
        identifier (Optional[str]): Unique identifier for the calculation.
        period (Optional[str]): Not used in initial Proof of Concept (PoC). Assumes current period.
        total (float): Original value returned for the total.
        components (List[Component_list]): List of components that should equal the total or predictive value.
        amend_total (bool): Specifies whether the total or components should be corrected when an error is detected.
        predictive (Optional[float]): The predictive value, typically the total for the current period.
        predictive_period (Optional[str]): Not used in initial PoC. Assumes current period.
        auxiliary (Optional[float]): The value to be used in the absence of a predictive value.
        absolute_difference_threshold (Optional[float]): Value used to check if the difference between the predictive
                                                        total and sum of components requires an automatic update.
        percentage_difference_threshold (Optional[float]): If the predictive total is within the specified percentage
                                                           of the sum of the components, the method will automatically
                                                           correct.

    Returns:
        Totals_and_Components_Output: An object containing the calculated totals and components along with the
                                      TCC marker indicating the type of correction (if any) that took place.
    Returns:
        Totals_and_Components_Output: An object containing the following attributes:
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
            - tcc_marker (str): Indicates what correction (if any) was necessary. Possible values: T (totals corrected),
                                 C (components corrected), N (no correction required), M (manual correction required),
                                 S (method stopped due to lack of data or zero values).

    Raises:
        [As we add exceptions we should note them here]

    """

    print("Running totals_and_components")

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
        percentage_difference_threshold=percentage_difference_threshold
    )

    component_total = sum_components(components=components)

    thresholds = calculate_percent_threshold(component_total, percentage_difference_threshold)

    output: Totals_and_Components_Output = Totals_and_Components_Output(
                                                identifier=identifier,
                                                period=period,
                                                absolute_difference=abs(component_total - predictive),
                                                low_percent_threshold=thresholds[Index.LOW_THRESHOLD.value],
                                                high_percent_threshold=thresholds[Index.HIGH_THRESHOLD.value],
                                                final_total=predictive,
                                                final_components=components,
                                                tcc_marker="T"
                                            )

    output.print_output_table()

    return output
