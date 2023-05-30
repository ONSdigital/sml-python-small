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
        percentage_difference_threshold: Optional[float]
        ) -> tuple[float | None, float | None, float | None, float | None, float | None, float | None, float | None]:
        """
        validate_input validating values are numbers and not none (if applicable)

        :param identifier: _description_
        :type identifier: Optional[str]
        :param period: _description_
        :type period: Optional[str]
        :param total: _description_
        :type total: float
        :param components: _description_
        :type components: List[Component_list]
        :param amend_total: _description_
        :type amend_total: bool
        :param predictive: _description_
        :type predictive: Optional[float]
        :param predictive_period: _description_
        :type predictive_period: Optional[str]
        :param auxiliary: _description_
        :type auxiliary: Optional[float]
        :param absolute_difference_threshold: _description_
        :type absolute_difference_threshold: Optional[float]
        :param percentage_difference_threshold: _description_
        :type percentage_difference_threshold: Optional[float]
        :raises ValueError: _description_
        :return: _description_
        :rtype: bool
        """        
        if total: 
           validate_number("total", total)
           float(total)
        if components == []:
            raise ValueError(f"The components is not populated")
        if components:
            for x in components:
               validate_number(f"component={x}", x)
               float(x)
        if predictive: 
           validate_number("predictive", predictive)
           float(predictive)
        if auxiliary: 
           validate_number("auxiliary", auxiliary)
           float(auxiliary)
        if absolute_difference_threshold is None and percentage_difference_threshold is None:
           raise ValueError("One or both of absolute/percentage difference thresholds must be specified")
        if absolute_difference_threshold: 
           validate_number("absolute difference threshold", absolute_difference_threshold)
           float(absolute_difference_threshold)
        if percentage_difference_threshold: 
           validate_number("percentage difference threshold", percentage_difference_threshold)
           float(percentage_difference_threshold)
        return total, components, predictive, auxiliary, absolute_difference_threshold, percentage_difference_threshold

def validate_number(tag: str, value) -> bool:
    """
    validate_number _summary_

    :param tag: _description_
    :type tag: _type_
    :param value: _description_
    :type value: _type_
    :raises ValueError: _description_
    :raises ValueError: _description_
    :return: _description_
    :rtype: bool
    """  
    if not isValueTypeNumber(value):
       raise ValueError(f"{tag} Not a number")
    return True

def isValueTypeNumber(value) -> bool:
    """
    isValueTypeNumber validate input is a number extension

    :param value: _description_
    :type value: _type_
    :return: _description_
    :rtype: bool
    """    
    try:
        float(value)
    except Exception:
           return False
    return True

def check_predictive_value(
        predictive: Optional[float],
        auxiliary: Optional[float]
        ) -> tuple[float | None, str | None]:
    """
    Checks if predictive and auxiliary values are input, when predictive is None and auxiliary is input set
    predictive to auxiliary, when both are None, set Tcc_Marker to S and stop calculation

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
            tcc_marker = 'S'
        else:
            predictive = auxiliary
    return predictive, tcc_marker


def check_zero_errors(predictive: float, components_sum: float) -> bool:
    raise NotImplementedError(f"{check_zero_errors.__name__}() not implemented yet")


def check_sum_components_predictive(predictive: float, components_sum: float) -> bool:
    raise NotImplementedError(f"{check_sum_components_predictive.__name__}() not implemented yet")


def determine_error_detection(absolute_difference_threshold: Optional[float],
                              percentage_difference_threshold: Optional[float],
                              absolute_difference: float,
                              components_sum: float
                              ) -> bool:
    raise NotImplementedError(f"{determine_error_detection.__name__}() not implemented yet")


def check_absolute_difference_threshold(absolute_difference_threshold: float, absolute_difference: float) -> bool:
    raise NotImplementedError(f"{check_absolute_difference_threshold.__name__}() not implemented yet")


def check_percentage_difference_threshold(percentage_difference_threshold: float,
                                          components_sum: float,
                                          predictive: float
                                          ) -> bool:
    raise NotImplementedError(f"{check_percentage_difference_threshold.__name__}() not implemented yet")


def error_correction(amend_total: bool,
                     components_sum: float,
                     original_components: List[Component_list],
                     predictive: float
                     ) -> bool:
    raise NotImplementedError(f"{error_correction.__name__}() not implemented yet")


def correct_total(components_sum: float,
                  original_components: List[Component_list]
                  ) -> bool:
    raise NotImplementedError(f"{correct_total.__name__}() not implemented yet")


def correct_components(components_sum: float,
                       original_components: List[Component_list],
                       predictive: float
                       ) -> bool:
    raise NotImplementedError(f"{correct_components.__name__}() not implemented yet")


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
            - Tcc_Marker (str): Indicates what correction (if any) was necessary. Possible values: T (totals corrected),
                                 C (components corrected), N (no correction required), M (manual correction required),
                                 S (method stopped due to lack of data or zero values).

    Raises:
        [As we add exceptions we should note them here]

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
        percentage_difference_threshold=percentage_difference_threshold
    )
    predictive, tcc_marker = check_predictive_value(predictive, auxiliary)

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
