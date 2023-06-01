from dataclasses import dataclass
from enum import Enum
from typing import List, Optional, Tuple


class Index(Enum):
    LOW_THRESHOLD = 0
    HIGH_THRESHOLD = 1


class TccMarker(Enum):
    STOP = 'S'
    MANUAL = 'M'
    TOTAL_CORRECTED = 'T'
    COMPONENTS_CORRECTED = 'C'
    NO_CORRECTION = 'N'


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
        ) -> bool:
        """
        validate_input is to ensure that the dataset input record has all the values 
        we need in the correct format. To do this we check to see if the data exists and is a number. If the data does not exist and is not a number we throw ValueError's as appropriate.
    

        :param identifier: Any e.g., Business Reporting Unit
        :type identifier: Optional[str]
        :param period: String in "YYYYMM" format
        :type period: Optional[str]
        :param total: Target period total, numeric – nulls allowed
        :type total: float
        :param components: Corresponding list of Total variable's components, numeric – nulls allowed
        :type components: List[Component_list]
        :param amend_total: This decided whether Total Variable should be automatically corrected, Boolean. FALSE = correct components, TRUE = correct total
        :type amend_total: bool
        :param predictive:A value used as a predictor for a contributor's target variable.
        :type predictive: Optional[float]
        :param predictive_period: The period containing predictive records; defined relative to the target period.
        :type predictive_period: Optional[str]
        :param auxiliary: The variable used as a predictor for a contributor’s target variable, where the predictive value is not available (e.g., where the contributor was not sampled in the predictive period).
        :type auxiliary: Optional[float]
        :param absolute_difference_threshold: Is the predefined threshold for the absolute difference
        :type absolute_difference_threshold: Optional[float]
        :param percentage_difference_threshold: Is the predefined percentage threshold represented as a decimal
        :type percentage_difference_threshold: Optional[float]
        :raises ValueError: ValueErrors are returned when data is missing or in the incorrect type/format.
        :return: The tuple is a returned list of values converted to floats (if possible).
        :rtype: tuple[float | None, float | None, float | None, float | None, float | None, float | None, float | None]
        """             
        if total: 
           validate_number("total", total)
           float(total)
        if components == []:
            raise ValueError("The components are not populated")
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
        return True

def validate_number(tag: str, value) -> bool:
    """
    validate_number will take a parsed tag and value and check ot see if the value is a number.
    If this is not the case it returns a ValueError.

    :param tag: The tag is a way of identifying the value and type entered and is used if a ValueError is returned.
    :type tag: str
    :param value: value is what is parsed to the function it can be many different types.
    :type value: float | optional
    :raises ValueError: ValueError is a means to raise error alerts.
    :return: This return a True boolean value if the value obtained is a number.
    :rtype: boolean
    """  
    if not isNumber(value):
       raise ValueError(f"{tag} is missing or not a number")
    return True

def isNumber(value) -> bool:
    """
    isNumber is a function which attempts to convert a entered type into a float.
    If will return a boolean dependent on whether it can or can't be converted.

    :param value: value is the parsed parameter which is to be converted to a float(if possible).
    :type value: float | optional
    :rtype: boolean to indicate if value is a number or not.
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
            tcc_marker = TccMarker.STOP.value
        else:
            predictive = auxiliary
    return predictive, tcc_marker


def check_zero_errors(predictive: float, components_sum: float) -> None | str:
    """
        Checks if when the predictive total is > 0, that the components sum is also > 0, adds a tcc_marker of 'S'
        when not true

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
    return tcc_marker


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

   :param identifier: Unique identifier for the calculation.
   :type identifier: Optional[str]
   :param period: Not used in initial Proof of Concept (PoC). Assumes current period.
   :type period: Optional[str]
   :param total: Original value returned for the total.
   :type total: float
   :param components: List of components that should equal the total or predictive value.
   :type components: List[Component_list]
   :param amend_total:Specifies whether the total or components should be corrected when an error is detected.
   :type amend_total:bool
   :param predictive: The predictive value, typically the total for the current period.
   :type predictive: Optional[float]
   :param predictive_period: Not used in initial PoC. Assumes current period.
   :type predictive_period: Optional[str]
   :param auxiliary: The value to be used in the absence of a predictive value.
   :type auxiliary: Optional[float]
   :param absolute_difference_threshold: Value used to check if the difference between the predictive
                                         total and sum of components requires an automatic update.
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
            - Tcc_Marker (str): Indicates what correction (if any) was necessary. Possible values: T (totals corrected),
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
        percentage_difference_threshold=percentage_difference_threshold
    )

    input_parameters = validate_input(total, components, predictive, auxiliary, absolute_difference_threshold, percentage_difference_threshold)

    predictive, tcc_marker = check_predictive_value(predictive, auxiliary)
    if tcc_marker != TccMarker.STOP.value:
        component_total = sum_components(components=components)
        tcc_marker = check_zero_errors(predictive, component_total)
        if tcc_marker != TccMarker.STOP.value:
            pass
        else:
            pass
    else:
        pass

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
