"""
Defines a wrapper to allow the Totals and Components method to be run with Pandas.

For Copyright information, please see LICENCE.
"""

import pandas as pd
from numpy import where

from sml_small.editing.totals_and_components import totals_and_components
from sml_small.editing.thousand_pounds import thousand_pounds


def run_totals_and_components(row, index_number, unique_identifier_column, components_list_columns,
                              total_column, amend_total_column, predictive_column, auxiliary_column,
                              absolute_threshold_column, percentage_threshold_column):
    """
    Runs the Totals & Components method against the input row of data.
    ...

    """
    new_list = []
    # loop through the components columns and create a single input
    for i in components_list_columns:
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


def run_thousand_pounds():
    return 0


function_mappings = {
        'totals_and_components': run_totals_and_components,
        'thousand_pounds': run_thousand_pounds,
}


def wrapper(
    input_frame,
    method,
    identifier_column=None,
    identifier_range=None,
    **method_input
):
    """
    Wrapper function to run Totals & Components over a pandas dataframe structure.
    Takes a Dataframe and relevant column names as input and outputs an amended
    dataframe with the results of Totals & Components appended to each
    row.
    ...
    """
    # filter against identifier
    if identifier_range:
        input_frame = input_frame.loc[
            input_frame[identifier_column].isin(identifier_range)
        ]

    input_frame.fillna('Nan', inplace=True)
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
    # column_order = [
    #     unique_identifier_column,
    #     total_column,
    #     *components_list_columns,
    #     amend_total_column,
    #     predictive_column,
    #     auxiliary_column,
    #     absolute_threshold_column,
    #     percentage_threshold_column,
    #     "Absolute Difference",
    #     "Low Percent Threshold",
    #     "High Percent Threshold",
    #     "TCC Marker",
    #     "Final Total",
    #     "Final Components",
    # ]
    # output_dataframe = output_dataframe.reindex(columns=column_order)
    return output_dataframe
