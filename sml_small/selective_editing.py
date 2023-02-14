"""
For Copyright information, please see LICENCE.
"""

from typing import List

import numpy as np
import pandas as pd


def selective_editing(input_dataframe: pd.DataFrame,
                      reference_col: str,
                      design_weight_col: str,
                      threshold_col: str,
                      question_list: List,
                      combination_method='maximum',
                      minkowski_distance=0,
                      show_sums=0) -> pd.DataFrame:
    """
    A selective editing score will be calculated for each reporting unit i at each time period t.

    :param input_dataframe:  DataFrame - Input DataFrame.
    :param reference_col: String - Column that holds the contributor reference.
    :param design_weight_col: String - Column that holds the design weight for the contributor.
    :param threshold_col: String - Column that holds the threshold for the contributor.
    :param question_list: List of strings - Column that holds the question names that are to be scored.
    :param combination_method: String - The combination method to be used, defaults to 'maximum'
    :param minkowski_distance: The minkowski distance to be used when calculating final score with the minkowski
    combination method; Defaults to 0.
    :param show_sums: 0/1 switch to provide additional data on score calculation for bau support, defaults to 0 (off).

    :return: DataFrame
    """
    suffix_list = ['_ar', '_pv', '_apv', '_sf']
    basic_reference_data = [reference_col, design_weight_col, threshold_col]

    # Validate input is a dataframe
    if not isinstance(input_dataframe, pd.DataFrame):
        msg = f'Param "input_dataframe" should be of type DataFrame, ' \
              f'not{type(input_dataframe)}.'
        raise TypeError(msg)

    input_columns = list(input_dataframe.columns)
    input_dataframe = input_dataframe.fillna(np.nan)
    output_dataframe = pd.DataFrame

    # Validate reference data columns are present as specified, and contain data
    for col_name in basic_reference_data:
        if not isinstance(col_name, str):
            msg = f'Values for column names should be of type string, ' \
                  f'not{type(col_name)}.'
            raise TypeError(msg)
        if col_name not in input_columns:
            msg = f'Column "{col_name}" not present in input_dataframe.'
            raise KeyError(msg)
        if input_dataframe[col_name].isnull().values.any():
            msg = f'Column "{col_name}" has rows with blank values.'
            raise ValueError(msg)

        # Put basic reference data at start of output dataframe
        if output_dataframe.empty:
            output_dataframe = input_dataframe.filter([col_name], axis=1)
        else:
            col_df = input_dataframe.filter([col_name], axis=1)
            output_dataframe = pd.concat([output_dataframe, col_df], axis=1)

    # Validate combination_method.

    if not isinstance(combination_method, str):
        msg = f'Param "combination_method" should be of type string, ' \
              f'not{type(combination_method)}.'
        raise TypeError(msg)

    combination_method = combination_method.lower()

    if combination_method not in ['maximum', 'mean', 'weighted', 'minkowski']:
        msg = f"Param 'combination_method' must be one of 'maximum', 'mean', " \
              f"'weighted' or 'minkowski'. " \
              f"It was passed as {combination_method}"
        raise ValueError(msg)

    if combination_method == "weighted":
        suffix_list.append('_wt')

    if combination_method == "minkowski":
        if (not isinstance(minkowski_distance, int) and
                not isinstance(minkowski_distance, float)):
            msg = f'Param "minkowski_distance" should be of type int or float, ' \
                  f'not{type(minkowski_distance)}.'
            raise TypeError(msg)

        if minkowski_distance < 1:
            msg = f'Param "minkowski_distance" must be a value >= 1, ' \
                  f'not{minkowski_distance}.'
            raise ValueError(msg)

    # Validate question_list is a list
    if not isinstance(question_list, list):
        msg = f'Param "question_list" should be of type List, ' \
              f'not{type(question_list)}.'
        raise TypeError(msg)

    if not question_list:
        msg = 'Param "question_list" should not be empty.'
        raise ValueError(msg)

    for question_name in question_list:
        # Validate question references are strings
        if not isinstance(question_name, str):
            msg = f'Values in parameter question_list" should be of type string, ' \
                  f'not{type(question_name)}.'
            raise TypeError(msg)

        # Validate reference data columns are present as specified.
        # NB: content validation carried out at top of _process_single_question function.
        for suffix in suffix_list:
            col_name = f"{question_name}{suffix}"
            if col_name not in input_columns:
                msg = f'Column "{col_name}" not present in input_dataframe.'
                raise KeyError(msg)

    # Check cols for reserved names (ones that method adds later) to prevent overwrite.
    cols = list(input_dataframe.columns)
    reserved = ['final_score',
                'input_flag',
                'output_flag']
    for col in cols:
        if col in reserved:
            msg = f"Reserved column name of {col} found in input dataframe column names."
            raise ValueError(msg)

    # Loop through questions in question_list to score them singularly.

    for question_name in question_list:
        question_dataframe = input_dataframe.filter(basic_reference_data, axis=1)
        for suffix in suffix_list:
            col_name = f"{question_name}{suffix}"
            col_df = input_dataframe.filter([col_name], axis=1)
            question_dataframe = pd.concat([question_dataframe, col_df], axis=1)

        question_dataframe = _process_single_question(question_dataframe,
                                                      question_name,
                                                      design_weight_col,
                                                      threshold_col,
                                                      reference_col,
                                                      combination_method,
                                                      minkowski_distance)

        output_dataframe = pd.concat([output_dataframe, question_dataframe], axis=1)

    # Process scores according to selected combination method
    #  NB: Not using list comprehension on the dataframe as _s in the question name can
    #  spoof it. ie: score_cols = [col for col in output_dataframe.columns if '_s' in col]
    score_cols = [f"{question}_s"for question in question_list]

    if combination_method == "maximum":
        output_dataframe['final_score'] = output_dataframe[score_cols].max(axis=1)

    elif combination_method == "mean":
        output_dataframe['final_score'] = output_dataframe[score_cols].mean(axis=1)

    elif combination_method == "weighted":
        weight_cols = [f"{question}_wt"for question in question_list]
        score_cols = [f"{question}_wts" for question in question_list]

        if show_sums:
            output_dataframe['sum_scores'] = output_dataframe[score_cols].sum(axis=1)
            output_dataframe['sum_weights'] = output_dataframe[weight_cols].sum(axis=1)

        output_dataframe['final_score'] = (output_dataframe[score_cols].sum(axis=1)
                                           / output_dataframe[weight_cols].sum(axis=1))

    else:  # combination_method == "minkowski"
        score_cols = [f"{question}_mks" for question in question_list]
        if show_sums:
            output_dataframe['sum_scores'] = (output_dataframe[score_cols].sum(axis=1))
        minkowski_inverted = 1 / minkowski_distance
        output_dataframe['final_score'] = (output_dataframe[score_cols].sum(axis=1)
                                           ** minkowski_inverted)

    # Assess the final score against the threshold
    output_dataframe['selective_editing_marker'] = (np.where(
        output_dataframe['final_score'] <
        output_dataframe[threshold_col], True, False))

    return output_dataframe


def _process_single_question(question_dataframe: pd.DataFrame,
                             question_name: str,
                             design_weight_col: str,
                             threshold_col: str,
                             reference_col: str,
                             combination_method: str,
                             minkowski_distance: float) -> pd.DataFrame:
    """
    :param question_dataframe:  DataFrame - The data needed to process a single question.
    :param question_name:  String - The base column name of the question to be scored.
    :param design_weight_col: String - Column that holds the design weight for the contributor.
    :param threshold_col: String - Column that holds the threshold for the contributor.
    :param reference_col: String - Column that holds the contributor reference.
    :param combination_method: String - The combination method to be used.
    :param minkowski_distance: The minkowski distance to be used when calculating final score with the minkowski
    combination method.

    :return: DataFrame
    """

    q_df = question_dataframe
    # Input
    ar_col = f"{question_name}_ar"  # actual return
    apv_col = f"{question_name}_apv"  # auxiliary predicted value
    pv_col = f"{question_name}_pv"  # predicted value
    sf_col = f"{question_name}_sf"  # standardising factor
    wt_col = f"{question_name}_wt"  # question score weight (weighted combi mode only)
    # Output
    s_col = f"{question_name}_s"  # score
    wts_col = f"{question_name}_wts"  # weighted score (weighted combi mode only)
    mks_col = f"{question_name}_mks"  # minkowski score (minkowski combi mode only)
    pm_col = f"{question_name}_pm"  # predicted marker

    # Validate that we have either/both the pv and the apv. Raise exception if we dont.
    check_df = q_df[(q_df[apv_col].isna()) & (q_df[pv_col].isna())]
    if not check_df.empty:
        ref_list = check_df[reference_col].values.tolist()
        msg = f'Reference(s) "{ref_list}" have neither PV nor APV.'
        raise ValueError(msg)

    # Validate that we have the returned value. Raise exception if we dont.
    check_df = q_df[(q_df[ar_col].isna())]
    if not check_df.empty:
        ref_list = check_df[reference_col].values.tolist()
        msg = f'Reference(s) "{ref_list}" do not have an AR value.'
        raise ValueError(msg)

    # Validate that we have the standardising factor value. Raise exception if we dont.
    check_df = q_df[(q_df[sf_col].isna())]
    if not check_df.empty:
        ref_list = check_df[reference_col].values.tolist()
        msg = f'Reference(s) "{ref_list}" do not have an SF value.'
        raise ValueError(msg)

    # Validate that we have the question weight value if using weighted mean .
    # Raise exception if we dont.
    if combination_method == 'weighted':
        check_df = q_df[(q_df[wt_col].isna())]
        if not check_df.empty:
            ref_list = check_df[reference_col].values.tolist()
            msg = f'Reference(s) "{ref_list}" do not have an WT value.'
            raise ValueError(msg)

    # Calculate the score for the question
    q_df[s_col] = np.where(q_df[pv_col].isna(),
                           (100 * abs(q_df[ar_col] - q_df[apv_col])
                           * q_df[design_weight_col] / q_df[sf_col]),
                           (100 * abs(q_df[ar_col] - q_df[pv_col])
                           * q_df[design_weight_col] / q_df[sf_col]))

    # Calculate the alternate if using minkowski or weighted.
    # NB: Yes, these could have been used to overwrite the base score, but no one but
    # methodology will ever see them, and they will want to assess them against the
    # base score, so best to include both and point final score calc appropriately.
    if combination_method == "weighted":
        q_df[wts_col] = q_df[s_col] * q_df[wt_col]
    elif combination_method == "minkowski":
        q_df[mks_col] = q_df[s_col] ** minkowski_distance

    q_df[pm_col] = np.where(q_df[pv_col].isna(), False, True)

    q_df = q_df.drop([reference_col,
                      design_weight_col,
                      threshold_col],
                     axis=1)

    return q_df
