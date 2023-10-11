"""
Defines a wrapper to allow specified methods to be run via a pandas Dataframe, applicable methods can be found
within the docstrings for wrapper()

For Copyright information, please see LICENCE.
"""

from typing import List, Optional

import pandas as pd

from sml_small.editing.thousand_pounds.thousand_pounds import thousand_pounds
from sml_small.editing.totals_and_components.totals_and_components import totals_and_components


# Runner methods, takes input csv, manipulates data into correct format as needed and runs method row by row
def run_totals_and_components(
    row: pd.Series,
    index_number: int,
    unique_identifier_column: str,
    components_list_columns: List[str],
    total_column: str,
    amend_total_column: str,
    predictive_column: Optional[str] = None,
    auxiliary_column: Optional[str] = None,
    absolute_threshold_column: Optional[str] = None,
    percentage_threshold_column: Optional[str] = None,
) -> pd.DataFrame:
    """
    Runs the Totals & Components method against the input row of data. All inputs except row and index_number
    should be supplied to the method by the user via the wrapper() method.
    ...

    :param row: A row of data from the dataframe to be processed
    :type row: Series
    :param index_number: Current index of the dataframe, so the output can be correctly appended later
    :type index_number: int
    :param unique_identifier_column: Column containing the unique_identifier value
    :type unique_identifier_column: str
    :param components_list_columns: List containing the components columns
    :type components_list_columns: list[str]
    :param total_column: Column containing the total value
    :type total_column: str
    :param amend_total_column: Column containing the amend_total value
    :type amend_total_column: str
    :param predictive_column: Column containing the predictive value
    :type predictive_column: str
    :param auxiliary_column: Column containing the auxiliary value
    :type auxiliary_column: str
    :param absolute_threshold_column: Column containing the absolute threshold value
    :type absolute_threshold_column: str
    :param percentage_threshold_column: Column containing the percentage threshold value
    :type percentage_threshold_column: str

    :return: totals_and_components_output, the  output of the totals_and_components method
    formatted into a pandas dataframe
    :rtype: Dataframe
    """
    new_list = []
    # loop through the components columns and create a single input
    for i in components_list_columns:
        if i is None:
            new_list.append('Nan')
        else:
            new_list.append(row[i])

    # create a dictionary defining the methods keyword names and the relevant columns they refer to
    input_dict = {
        "identifier": unique_identifier_column,
        "total": total_column,
        "amend_total": amend_total_column,
        "predictive": predictive_column,
        "auxiliary": auxiliary_column,
        "absolute_difference_threshold": absolute_threshold_column,
        "percentage_difference_threshold": percentage_threshold_column,
    }
    final_inputs = {}
    for key, value in input_dict.items():
        if value is not None:
            final_inputs[key] = row[value]
    # run totals and components on current row
    output = totals_and_components(**final_inputs, components=new_list)

    # construct a new dataframe containing our output data
    totals_and_components_output = pd.DataFrame(
        {
            "Identifier": output.identifier,
            "Absolute Difference": output.absolute_difference,
            "Low Percent Threshold": output.low_percent_threshold,
            "High Percent Threshold": output.high_percent_threshold,
            "Final Total": output.final_total,
            "Final Components": [output.final_components],
            "TCC Marker": output.tcc_marker,
        },
        index=[index_number],
    )
    return totals_and_components_output


def run_thousand_pounds(
    row: pd.Series,
    index_number: int,
    principal_variable_column: str,
    upper_limit_column: str,
    lower_limit_column: str,
    target_variables_columns: List[str],
    predictive_column: Optional[str] = None,
    auxiliary_column: Optional[str] = None,
    unique_identifier_column: Optional[str] = None,
) -> pd.DataFrame:
    """
    Runs the Thousand Pounds Correction method against the input row of data. All inputs except row and index_number
    should be supplied to the method by the user via the wrapper() method.
    ...

    :param row: Current index of the dataframe, so the output can be correctly appended later
    :type row: Series
    :param index_number: Current index of the dataframe, so the output can be correctly appended later
    :type index_number: int
    :param principal_variable_column: Column containing the principal variable value
    :param upper_limit_column: Column containing the upper limit value
    :param lower_limit_column: Column containing the lower limit value
    :param target_variables_columns: List of columns containing the target variables values
    :param predictive_column: Column containing the predictive value
    :param auxiliary_column: Column containing the auxiliary value
    :param unique_identifier_column: Column containing the principal identifier  column

    :return: thousand_pounds_output, the output of the thousand_pounds method stored within a
    pandas dataframe
    :rtype: dataframe
    """
    target_variables_list = {}
    for value in target_variables_columns:
        if row[value] is None:
            target_variables_list[value] = 'Nan'
        else:
            target_variables_list[value] = row[value]

    input_dict = {
        "unique_identifier": unique_identifier_column,
        "principal_variable": principal_variable_column,
        "upper_limit": upper_limit_column,
        "lower_limit": lower_limit_column,
        "predictive": predictive_column,
        "auxiliary": auxiliary_column,
    }
    final_inputs = {}
    for key, value in input_dict.items():
        if value is not None:
            final_inputs[key] = row[value]
    # run totals and components on current row
    output = thousand_pounds(**final_inputs, target_variables=target_variables_list)
    # construct a new dataframe containing our output data
    thousand_pounds_output = pd.DataFrame(
        {
            "Principal Identifier": output.unique_identifier,
            "Principal Final Value": output.principal_final_value,
            "Target Variables": [output.target_variables],
            "TPC Ratio": output.tpc_ratio,
            "TPC Marker": output.tpc_marker,
        },
        index=[index_number],
    )
    return thousand_pounds_output


# acceptable inputs for functions
function_mappings = {
    "totals_and_components": run_totals_and_components,
    "thousand_pounds": run_thousand_pounds,
}


# Main wrapper function
def wrapper(
    input_frame: pd.DataFrame,
    method: str,
    output_columns: List[str],
    identifier_column: Optional[str] = None,
    identifier_range: Optional[str] = None,
    **method_input
) -> pd.DataFrame:
    """
    Wrapper function to run a sml_small method over a pandas dataframe structure.
    Dataframe can be filtered against identifier column and range, allowing a column to be targeted, plus the
    values that it should filter against.

    Current methods: totals_and_components, thousand_pounds

    :param input_frame: Pandas dataframe containing the data to run a method against
    :type input_frame: Dataframe
    :param method: sml_small method to run, please refer to "current methods" section above
    :type method: str
    :param output_columns: List of columns to be taken from the method output and appended to the input frame
    :type output_columns: List[str]
    :param identifier_column: Name of column to apply filtering on
    :type identifier_column: str
    :param identifier_range: List of filtered values for the method to find
    :type identifier_range: List[str]
    :param method_input: Keyword arguments providing the data required to run an individual method, please refer
    to the run_ functions for more information
    :type method_input: **kwargs

    :return: output_dataframe, the original input data with the specified output data appended to it
    :rtype: Dataframe
    """

    # filter against identifier
    if identifier_range:
        input_frame = input_frame.loc[
            input_frame[identifier_column].isin(identifier_range)
        ]

    # input_frame.fillna("Nan", inplace=True)
    input_frame = input_frame.astype(object).where(pd.notnull(input_frame), None)
    # apply our wrapper function per row, adding each row to output dataframe
    output_dataframe = input_frame.apply(
        lambda row: function_mappings[method](row, row.name, **method_input),
        axis=1,
    )
    output_dataframe = pd.concat(list(output_dataframe), ignore_index=True)
    frames = [input_frame, output_dataframe]
    # concatenate the two dataframes together and output
    output_dataframe = pd.concat([df.stack() for df in frames]).unstack()
    # during concat above the two dataframes become unordered, the below reorders them
    # into input followed by output
    column_order = list(method_input.values())
    flat_list = []
    # Where input values are of type list, flatten these lists (currently only checks one deep as there
    # are no lists of lists expected
    for list_item in column_order:
        if type(list_item) is not list:
            flat_list.append(list_item)
        else:
            for sublist_item in list_item:
                flat_list.append(sublist_item)
    for i in output_columns:
        flat_list.append(i)
    output_dataframe = output_dataframe.reindex(columns=flat_list)
    return output_dataframe
