"""
For Copyright information, please see LICENCE.
"""

import pandas as pd
from numpy import where

from sml_small.totals_and_components import totals_and_components


def run_method(row, index_number, components_list, inputs_dictionary):
    """
    Runs the Totals & Components method against the input row of data.
    ...
    :param row: Current row of data from the dataframe.
    :type row: Series
    :param index_number: Current index from the dataframe, used to join the output
    and input together.
    :type index_number: int
    :param components_list: list containing the names of each component's column so
     the data can be merged together
    before running method.
    :type components_list: list[String]
    :param inputs_dictionary: dictionary containing all columns passed to original
    method.
    :type inputs_dictionary: dictionary
    ...
    :return: totals_and_components_output, a dataframe containing the output of the
     totals and components method.
    """
    new_list = []
    # loop through the components columns and create a single input
    for i in components_list:
        new_list.append(row[i])

    final_inputs = {}
    for key, value in inputs_dictionary.items():
        if value is not None:
            final_inputs[key] = row[value]
    # run totals and components on current row
    output = totals_and_components.totals_and_components(
        **final_inputs, components=new_list
    )

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


def wrapper(
    input_frame,
    unique_identifier_column,
    total_column,
    components_list_columns,
    amend_total_column,
    predictive_column=None,
    auxiliary_column=None,
    absolute_threshold_column=None,
    percentage_threshold_column=None,
    precision_column=None,
    identifier_range=None,
    amend_predictive=False,
):
    """
    Wrapper function to run Totals & Components over a pandas dataframe structure.
    Takes a Dataframe and relevant column names as input and outputs an amended
    dataframe with the results of Totals & Components appended to each
    row.
    ...
    :param input_frame: Pandas Dataframe to run method against.
    :type input_frame: Dataframe
    :param unique_identifier_column: Name of Unique Identifier column.
    :type unique_identifier_column: String
    :param total_column: Name of Total column.
    :type total_column: String
    :param components_list_columns: List containing the names of all
    Components columns.
    :type components_list_columns list[String]
    :param amend_total_column: Name of Amend Total column.
    :type amend_total_column: String
    :param predictive_column: Name of  Predictive column.
    :type precision_column: String
    :param auxiliary_column: Name of Auxiliary column.
    :type auxiliary_column: String
    :param absolute_threshold_column: Name of Absolute Threshold column.
    :type absolute_threshold_column: String
    :param percentage_threshold_column: Name of Percentage Threshold
    column.
    :type percentage_threshold_column: String
    :param precision_column: Name of Precision column.
    :type precision_column: String
    :param identifier_range: A range of identifiers to filter the input
    frame against before running method.
    :type identifier_range: list[String]
    :param amend_predictive: If True will replace predictive in rows with
    total value when both predictive and auxiliary are missing.
    :type amend_predictive: bool
    ...
    :return: output_dataframe, the amended input frame containing both
    original input and Totals & Components output for each row run.
    """
    input_dict = {
        "identifier": unique_identifier_column,
        "total": total_column,
        "amend_total": amend_total_column,
        "predictive": predictive_column,
        "precision": precision_column,
        "auxiliary": auxiliary_column,
        "absolute_difference_threshold": absolute_threshold_column,
        "percentage_difference_threshold": percentage_threshold_column,
    }
    # filter against identifier
    if identifier_range:
        input_frame = input_frame.loc[
            input_frame[unique_identifier_column].isin(identifier_range)
        ]
    # fill in predictive with total value when predictive and auxiliary is nan
    if amend_predictive is True:
        input_frame[predictive_column] = where(
            (pd.isnull(input_frame[predictive_column]))
            & (pd.isnull(input_frame[auxiliary_column])),
            input_frame[total_column],
            input_frame[predictive_column],
        )
    # replace nan with None as float version of nan will pass validation it should fail,
    # for components list use "Nan"
    input_frame[components_list_columns] = input_frame[components_list_columns].fillna(
        "Nan"
    )
    input_frame = input_frame.astype(object).where(pd.notnull(input_frame), None)
    # apply our wrapper function per row, adding each row to output dataframe
    output_dataframe = input_frame.apply(
        lambda row: run_method(row, row.name, components_list_columns, input_dict),
        axis=1,
    )
    output_dataframe = pd.concat([r for r in output_dataframe], ignore_index=True)
    frames = [input_frame, output_dataframe]
    # concatenate the two dataframes together and output
    output_dataframe = pd.concat([df.stack() for df in frames]).unstack()
    # during concat above the two dataframes become unordered, the below reorders them
    # into input followed by output
    column_order = [
        unique_identifier_column,
        total_column,
        *components_list_columns,
        amend_total_column,
        predictive_column,
        auxiliary_column,
        absolute_threshold_column,
        percentage_threshold_column,
        "Absolute Difference",
        "Low Percent Threshold",
        "High Percent Threshold",
        "TCC Marker",
        "Final Total",
        "Final Components",
    ]
    output_dataframe = output_dataframe.reindex(columns=column_order)
    return output_dataframe
