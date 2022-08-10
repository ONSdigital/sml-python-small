import sys
from calendar import monthrange
from datetime import timedelta
from typing import List, Union

import numpy as np
import pandas as pd


def date_adjustment(input_dataframe: pd.DataFrame,
                    trading_weights: pd.DataFrame,
                    target_columns: List,
                    contributor_returned_start_date_col: str,
                    contributor_returned_end_date_col: str,
                    expected_start_date_col: str,
                    expected_end_date_col: str,
                    domain_col: str,
                    short_period_parameter_col: str,
                    long_period_parameter_col: str,
                    equal_weighted_col: str,
                    set_to_mid_point_col: str,
                    use_calendar_days_col: str,
                    average_weekly_col: str,
                    da_error_flag_col: str,
                    trading_date_col: str,
                    trading_weights_col: str,
                    trading_domain_col: str,
                    trading_period_start_col: str,
                    trading_period_end_col: str,
                    ignore_multi_aw_param_error=False) -> pd.DataFrame:
    """
    **Description**:

    The controlling function validates that validates input and steps the data through
    the sub-functions in the following order:

    1. generate_average_weekly_questions.
    2. missing_value_subfunction.
    3. primary_wrangler_subfunction.
    4. midpoint_subfunction.
    5. secondary_wrangler_subfunction.
    6. date_adjustment_subfunction.
    7. average_weekly_subfunction.

    All calculations are done on a row by row basis. Full documentation can be found in
    the readme.md file in the docs directory.
----
    **Parameters**

    :param input_dataframe: The dataframe containing the data to be processed plus processing options.
    :param trading_weights: The trading day weight reference data required for processing.
    :param target_columns: The names of the columns in input_dataframe to be date_adjusted.
    :param contributor_returned_start_date_col: Name of the column holding the contributors returned period start date.
    :param contributor_returned_end_date_col: Name of the column holding the contributors returned period end date.
    :param expected_start_date_col: Name of the column holding the expected period start date in input_dataframe.
    :param expected_end_date_col: Name of the column holding the expected period end date in input_dataframe.
    :param domain_col: Name of the column holding the Domain in input_dataframe.
    :param short_period_parameter_col: Name of the column holding the "short period parameter" in input_dataframe.
    :param long_period_parameter_col: Name of the column holding the "long period parameter" in input_dataframe.
    :param set_to_mid_point_col: Name of the column holding the "Set to mid-point" option in input_dataframe.
    :param use_calendar_days_col: Name of the column holding the "use calendar days" option in input_dataframe.
    :param equal_weighted_col: Name of the column holding the "Set to equal weighted" option in input_dataframe.
    :param average_weekly_col: Name of the column holding the "average_weekly" in input_dataframe.
    :param da_error_flag_col: Name of the column that the user wishes the error flag column to be called in the output.
    :param trading_date_col: Name of the column holding the dates in trading_weights.
    :param trading_weights_col: Name of the column holding the weights in the trading_weights DataFrame.
    :param trading_domain_col: Name of the column holding the domain in the trading_weights DataFrame.
    :param trading_period_start_col: Name of the column holding the trading period start date in the trading_weights DataFrame.
    :param trading_period_end_col: Name of the column holding the trading period end date in the trading_weights DataFrame.
    :param ignore_multi_aw_param_error: Used in testing only. Leave blank so it defaults to False.

    :raises TypeError: If the input dataframe is not a DataFrame.
    :raises TypeError: If the trading weights reference data is not a DataFrame.
    :raises TypeError: If the target columns parameter is not a List.
    :raises KeyError: If required columns referenced in the parameters cannot be found in the input dataframe or the trading weights dataframe as appropriate.
    :raises KeyError: If columns referenced in target_columns parameter cannot be found in the input dataframe.
    :raises ValueError: If mixed values found in the input dataframe for equal_weighted_col, set_to_mid_point_col or average_weekly_col.

    :returns: The input data with the method output appended as extra columns as necessary

----
    **Error Flags**

    If a row of data is not able to be processed, an error flag will be raised to
    indicate the issue with the data.
    The error flags are as follows:
        * E00: Average Weekly parameter is invalid.
        * E01: The value to be date adjusted is missing from one of the target columns.
        * E02: The contributor returned end date is earlier than the contributor returned
                start date.
        * E03: A required record for calculating weight m is missing from the trading
                weights table.
        * E04: A required trading weight for calculating weight m is null or blank.
        * E05: A required trading weight for calculating weight m has a negative value.
        * E06: A required record for calculating weight n is missing from or duplicated in
                the trading  weights table.
        * E07: A required trading weight for calculating weight n is null or blank.
        * E08: A required trading weight for calculating weight n has a negative value.
        * E09: Contributors return does not cover any of expected period.
        * E10: The sum of trading day weights over contributors returned period is zero.
        * E11: The sum of trading day weights over contributors returned period is zero.
        * E12: A required record for calculating midpoint date is missing from the
                trading weights table.
        * E13: A required record for setting APS and APE by midpoint is missing from or 
                duplicated in the trading  weights table.
        * E14: Expected period start date is missing or an invalid date.
        * E15: Expected period end date is missing or an invalid date.

        ** NOTE: **
        These are NOT exceptions and do not cause the method to fail. Once an error flag
        has been placed on a row of data, no further processing is done to that row,
        preserving the data in the state it was when the flag was raised.

        If at any point in processing an error flag is set on all rows, processing will
        stop after that sub-function and the dataframe will be returned as it is at that
        point to allow the user to 'debug' their data.

----
    **Warning Flags**

    If a row of data is able to be processed, but requires the user to be notified of a
    potential issue, a warning flag is raised for that row. The following warning flags
    are applied in the given circumstances:

            *  S: The contributors returned period is less than the threshold supplied
                  in the short period parameter.
            *  L: The contributors returned period is greater than the threshold supplied
                  in the long period parameter.
            * SL: The supplied short period parameter is greater than or equal to the
                  supplied long period parameter.

        **NOTE:**
        A warning flag does not stop the method running, and the row will continue to be
        processed as normal.

    """

    # Initialise dtypes for input columns
    dtype_dict = {
        contributor_returned_start_date_col: 'datetime64[ns]',
        contributor_returned_end_date_col: 'datetime64[ns]',
        expected_start_date_col: 'datetime64[ns]',
        expected_end_date_col: 'datetime64[ns]',
        'actual_period_start_date': 'datetime64[ns]',
        'actual_period_end_date': 'datetime64[ns]',
        equal_weighted_col: 'object',
        domain_col: 'object',
        set_to_mid_point_col: 'object',
        use_calendar_days_col: 'object',
        short_period_parameter_col: 'int64',
        long_period_parameter_col: 'int64',
        average_weekly_col: 'object',
        da_error_flag_col: 'object',
        trading_date_col: 'datetime64[ns]',
        trading_weights_col: 'object',
        trading_domain_col: 'object',
        trading_period_start_col: 'datetime64[ns]',
        trading_period_end_col: 'datetime64[ns]',
        'domain_col_list': [domain_col, trading_domain_col]
    }

    # Basic validation
    # noinspection PyProtectedMember,PyUnresolvedReferences
    this_place = sys._getframe().f_code.co_name
    _basic_input_validation(this_place,
                            input_dataframe=input_dataframe,
                            trading_weights=trading_weights,
                            target_columns=target_columns)

    # Check df dtypes and change where necessary
    # noinspection PyTypeChecker
    input_dataframe = _set_dtypes(input_dataframe, dtype_dict, target_columns)

    # Validate required columns in input_dataframe
    required_columns = [contributor_returned_start_date_col,
                        contributor_returned_end_date_col,
                        contributor_returned_end_date_col,
                        expected_start_date_col,
                        expected_end_date_col,
                        equal_weighted_col,
                        domain_col,
                        set_to_mid_point_col,
                        use_calendar_days_col,
                        short_period_parameter_col,
                        long_period_parameter_col,
                        average_weekly_col]
    for col_name in target_columns:
        required_columns.append(col_name)
    _required_column_validation(
        this_place, 'input_dataframe', input_dataframe, required_columns)

    # Validate required columns are in trading_weights dataframe
    required_columns = [trading_weights_col,
                        trading_date_col,
                        trading_domain_col,
                        trading_period_start_col,
                        trading_period_end_col
                        ]
    _required_column_validation(
        this_place, 'trading_weights', trading_weights, required_columns)

    # Ensure only one average_weekly_param value present
    check_list = list(input_dataframe[average_weekly_col].unique())
    if not ignore_multi_aw_param_error:
        if len(check_list) != 1:
            # Initiate fast fail with AW error flag in error flag column
            df_aw_param_error = input_dataframe
            df_aw_param_error[da_error_flag_col] = 'E00'
            return df_aw_param_error

    # Ensure only one set_to_mid_point_col value present
    check_list = list(input_dataframe[set_to_mid_point_col].unique())
    if not ignore_multi_aw_param_error:
        if len(check_list) != 1:
            msg = f"the use mid-point method parameter from {set_to_mid_point_col} " \
                  f"has more than one unique value set in the input dataframe."
            raise ValueError(msg)

    # Ensure only one equal_weighted_col value present
    check_list = list(input_dataframe[equal_weighted_col].unique())
    if not ignore_multi_aw_param_error:
        if len(check_list) != 1:
            msg = f"the use equal weights parameter from {equal_weighted_col} " \
                  f"has more than one unique value set in the input dataframe."
            raise ValueError(msg)

    # Check cols for reserved names (ones that method adds later) to prevent overwrite.
    cols = list(input_dataframe.columns)
    reserved = ['midpoint',
                'actual_period_start_date',
                'actual_period_end_date',
                'date_change_in_return_period_flag',
                'number_of_days_in_contributors_returned_period'
                'sum_of_trading_day_weights_over_actual_returned_period',
                'sum_of_trading_day_weights_over_contributors_returned_period']
    for col in cols:
        if col in reserved:
            msg = f"Reserved column name of {col} found in input dataframe column names."
            raise ValueError(msg)

    # Initialise 'average_weekly_questions_list' to hold list of questions that will
    # use average weekly functionality
    average_weekly_param = input_dataframe.loc[0][average_weekly_col]
    average_weekly_questions_list = generate_average_weekly_questions(
        average_weekly_param, target_columns)
    # indirectly validate contents of average_weekly parameter
    if not isinstance(average_weekly_questions_list, list):
        # Initiate fast fail with AW error flag in error flag column
        df_aw_param_error = input_dataframe
        df_aw_param_error[da_error_flag_col] = 'E00'
        return df_aw_param_error

    # Send dataframe through missing value subfunction
    df_stage_one = missing_value_subfunction(
        input_dataframe, target_columns, da_error_flag_col)

    # Check df_stage_one dtypes and change where necessary
    # noinspection PyTypeChecker
    df_stage_one = _set_dtypes(df_stage_one, dtype_dict, target_columns)

    # Check trading_weights dtypes and change where necessary
    trading_weights = _set_dtypes(trading_weights, dtype_dict)

    # If all rows error flagged, output dataframe as is.
    if df_stage_one[da_error_flag_col].notnull().values.all():
        return df_stage_one

    df_stage_two = primary_wrangler_subfunction(df_stage_one,
                                                trading_weights,
                                                target_columns,
                                                contributor_returned_start_date_col,
                                                contributor_returned_end_date_col,
                                                expected_start_date_col,
                                                expected_end_date_col,
                                                domain_col,
                                                equal_weighted_col,
                                                da_error_flag_col,
                                                trading_domain_col,
                                                trading_date_col,
                                                trading_weights_col)

    # If all rows error flagged, output dataframe as is.
    if df_stage_two[da_error_flag_col].notnull().values.all():
        return df_stage_two

    # Send dataframe through midpoint method
    df_stage_three = midpoint_subfunction(df_stage_two,
                                          trading_weights,
                                          target_columns,
                                          domain_col,
                                          expected_start_date_col,
                                          expected_end_date_col,
                                          contributor_returned_start_date_col,
                                          contributor_returned_end_date_col,
                                          set_to_mid_point_col,
                                          equal_weighted_col,
                                          use_calendar_days_col,
                                          trading_date_col,
                                          trading_period_start_col,
                                          trading_period_end_col,
                                          trading_weights_col,
                                          trading_domain_col,
                                          da_error_flag_col)

    # If all rows error flagged, output dataframe as is.
    if df_stage_three[da_error_flag_col].notnull().values.all():
        return df_stage_three

    # Send dataframe through secondary wrangler
    df_stage_four = secondary_wrangler_subfunction(df_stage_three,
                                                   trading_weights,
                                                   target_columns,
                                                   contributor_returned_start_date_col,
                                                   contributor_returned_end_date_col,
                                                   expected_start_date_col,
                                                   expected_end_date_col,
                                                   domain_col,
                                                   equal_weighted_col,
                                                   set_to_mid_point_col,
                                                   short_period_parameter_col,
                                                   long_period_parameter_col,
                                                   da_error_flag_col,
                                                   trading_date_col,
                                                   trading_domain_col,
                                                   trading_weights_col)

    # If all rows error flagged, output dataframe as is.
    if df_stage_four[da_error_flag_col].notnull().values.all():
        return df_stage_four

    # Send dataframe through date adjustment method.
    df_stage_five = date_adjustment_subfunction(df_stage_four,
                                                target_columns,
                                                da_error_flag_col)

    # If all rows error flagged, output dataframe as is.
    if df_stage_five[da_error_flag_col].notnull().values.all():
        return df_stage_five

    # Send dataframe through average weekly method.
    df_stage_six = average_weekly_subfunction(df_stage_five,
                                              average_weekly_questions_list,
                                              da_error_flag_col)

    output_dataframe = df_stage_six.copy()

    return output_dataframe


# -------------------------------------------------------------------------------------------------------------
# SECTION: GENERATE AVERAGE WEEKLY QUESTION LIST SUB-FUNCTION
# -------------------------------------------------------------------------------------------------------------

def generate_average_weekly_questions(average_weekly: str,
                                      target_columns: List) -> Union[List, str]:
    """
    Generates the reference list that controls the average_weekly method.

    :param String average_weekly: The average weekly parameter for the run. (Not the column name, the actual value.)
    :param List[Strings] target_columns: The names of the columns in input_dataframe to be date_adjusted.

    :raises TypeError: If the data held in column referenced by the target_columns_col parameter is not a list.

    :returns: A list of validated columns to run the average_weekly method against.


    """
    # Validate target_columns is a list
    # noinspection PyProtectedMember,PyUnresolvedReferences
    this_place = sys._getframe().f_code.co_name
    if not isinstance(target_columns, list):
        msg = 'Param "target_columns" for function ' + this_place + ' '
        msg += 'should be of type List, not ' + str(type(target_columns)) + '.'
        raise TypeError(msg)

    if average_weekly == 'N':
        average_weekly_questions_list = []
    elif average_weekly == 'A':
        average_weekly_questions_list = target_columns.copy()
    else:
        average_weekly_questions_list = []
        submitted_questions = _convert_question_string_to_list(average_weekly)
        for column in target_columns:
            if column in submitted_questions:
                average_weekly_questions_list.append(column)
                submitted_questions = [x for x in submitted_questions if x != column]
        if submitted_questions:
            return "ERROR: invalid average_weekly parameter contents."

    return average_weekly_questions_list


# -------------------------------------------------------------------------------------------------------------
# SECTION: MISSING VALUE SUB-FUNCTION
# -------------------------------------------------------------------------------------------------------------=

def missing_value_subfunction(input_dataframe: pd.DataFrame,
                              target_columns: List,
                              da_error_flag_col: str) -> pd.DataFrame:
    """
    Checks the target columns for missing data.

    :param input_dataframe: The dataframe containing the data to be processed plus processing options.
    :param target_columns: The names of the columns in input_dataframe to be date_adjusted.
    :param da_error_flag_col: Name of the column that the user wishes the error flag column to be called in the output.

    :raises TypeError: If the input dataframe is not a DataFrame.
    :raises TypeError: If the target columns parameter is not a List.
    :raises KeyError: If required columns referenced in the parameters cannot be found in the input dataframe.
    :raises KeyError: If columns referenced in target_columns parameter cannot be found in the input dataframe.

    :returns: Data with rows that have missing data in the target columns marked with an error flag.

    """
    # noinspection PyProtectedMember,PyUnresolvedReferences
    this_place = sys._getframe().f_code.co_name

    # noinspection PyProtectedMember
    _basic_input_validation(this_place,
                            input_dataframe=input_dataframe,
                            target_columns=target_columns)

    # Validate required columns in input_dataframe
    _required_column_validation(this_place, 'input_dataframe', input_dataframe, target_columns)

    # Create working copy of input dataframe
    working_dataframe = input_dataframe.copy()

    # Add the error flag column for future use and output.
    working_dataframe[da_error_flag_col] = np.nan

    # Check and apply the error flag as appropriate
    def check_for_null(row):
        for target_column in target_columns:
            if pd.isnull(row[target_column]) or row[target_column] == '.':
                row[target_column] = np.nan
                row[da_error_flag_col] = 'E01'
        return row

    df_stage_one = working_dataframe.apply(check_for_null, axis=1)

    return df_stage_one


# -------------------------------------------------------------------------------------------------------------
# SECTION: PRIMARY WRANGLER SUB-FUNCTION
# -------------------------------------------------------------------------------------------------------------

def primary_wrangler_subfunction(df_stage_one: pd.DataFrame,
                                 trading_weights: pd.DataFrame,
                                 target_columns: List,
                                 contributor_returned_start_date_col: str,
                                 contributor_returned_end_date_col: str,
                                 expected_start_date_col: str,
                                 expected_end_date_col: str,
                                 domain_col: str,
                                 equal_weighted_col: str,
                                 da_error_flag_col: str,
                                 trading_domain_col: str,
                                 trading_date_col: str,
                                 trading_weights_col: str) -> pd.DataFrame:
    """
    Prepares the data for further processing by the midpoint method if required.

    :param df_stage_one: The dataframe containing the data as processed to this point.
    :param trading_weights: The trading day weight reference data required for processing.
    :param target_columns: The names of the columns in the input dataframe to be date_adjusted.
    :param contributor_returned_start_date_col: Name of the column holding the contributors returned period start date.
    :param contributor_returned_end_date_col: Name of the column holding the contributors returned period end date.
    :param expected_start_date_col: Name of the column holding the expected period start date in input_dataframe.
    :param expected_end_date_col: Name of the column holding the expected period end date in input_dataframe.
    :param domain_col: Name of the column holding the Domain in input_dataframe.
    :param equal_weighted_col: Name of the column holding the "Set to equal weighted" option in input_dataframe.
    :param da_error_flag_col: Name of the column that the user wishes the error flag column to be called in the output.
    :param trading_date_col: Name of the column holding the dates in trading_weights.
    :param trading_weights_col: Name of the column holding the weights in trading_weights.
    :param trading_domain_col: Name of the column holding the domain in trading_weights.

    :raises TypeError: If the input dataframe is not a DataFrame.
    :raises TypeError: If the trading weights reference data is not a DataFrame.
    :raises TypeError: If the target columns parameter is not a List.
    :raises KeyError: If required columns referenced in the parameters cannot be found in the input dataframe or the trading weights dataframe as appropriate.
    :raises KeyError: If columns referenced in target_columns parameter cannot be found in the input dataframe.

    :return: A dataframe holding data and structure ready to be passed into the midpoint method sub-function.

    """
    # noinspection PyProtectedMember,PyUnresolvedReferences
    this_place = sys._getframe().f_code.co_name

    # Basic validation checks
    # noinspection PyProtectedMember
    _basic_input_validation(this_place,
                            input_dataframe=df_stage_one,
                            trading_weights=trading_weights,
                            target_columns=target_columns)

    # Validate required columns are in input dataframe
    required_columns = [contributor_returned_start_date_col, contributor_returned_end_date_col, da_error_flag_col,
                        equal_weighted_col, expected_start_date_col, expected_end_date_col]
    for col_name in target_columns:
        required_columns.append(col_name)
    _required_column_validation(this_place, 'df_stage_one', df_stage_one, required_columns)

    # Validate required columns are in trading_weights dataframe
    required_columns = [trading_weights_col,
                        trading_date_col,
                        trading_domain_col]
    _required_column_validation(this_place, 'trading_weights', trading_weights, required_columns)

    working_dataframe = df_stage_one.copy()

    # Rule 3.1 & 3.2

    def fix_dates(row):

        #  Ensure we have the EPS and EPE dates and they are valid.
        if pd.isnull(row[expected_start_date_col]):
            row = _apply_error_flag(row, 'E14', da_error_flag_col, target_columns)
            return row
        if pd.isnull(row[expected_end_date_col]):
            row = _apply_error_flag(row, 'E15', da_error_flag_col, target_columns)
            return row

        # Fix NaT start date
        if pd.isna(row[contributor_returned_start_date_col]):
            row[contributor_returned_start_date_col] = row[expected_start_date_col]
            row[contributor_returned_start_date_col] = pd.to_datetime(
                row[contributor_returned_start_date_col], format='%Y%m%d', errors='coerce')

        # Fix NaT end date
        if pd.isna(row[contributor_returned_end_date_col]):
            row[contributor_returned_end_date_col] = row[expected_end_date_col]
            row[contributor_returned_end_date_col] = pd.to_datetime(
                row[contributor_returned_end_date_col], format='%Y%m%d', errors='coerce')

        return row

    working_dataframe = _run_apply(working_dataframe, fix_dates, da_error_flag_col)

    # Rule 3.3, 3.4, 3.5, 3.6, 3.7

    def preliminary_stages(row):
        # Set defaults
        row['sum_of_trading_day_weights_over_contributors_returned_period'] = 0
        row['number_of_days_in_contributors_returned_period'] = 0

        # Calculate actual or flags.
        if row[contributor_returned_end_date_col] < row[contributor_returned_start_date_col]:
            row = _apply_error_flag(row, 'E02', da_error_flag_col, target_columns)
            return row
        else:
            row['number_of_days_in_contributors_returned_period'] = \
                (row[contributor_returned_end_date_col] - row[contributor_returned_start_date_col]).days + 1

            if row[equal_weighted_col] == 'Y':
                row['sum_of_trading_day_weights_over_contributors_returned_period'] = \
                    row['number_of_days_in_contributors_returned_period']

            else:
                flagged = 0
                error_code_number = 0
                mask = (trading_weights[trading_date_col] >= row[contributor_returned_start_date_col]) & \
                       (trading_weights[trading_date_col] <= row[contributor_returned_end_date_col]) & \
                       (trading_weights[trading_domain_col] == row[domain_col])

                filtered_weights = trading_weights.loc[mask]

                if len(filtered_weights.index) != row['number_of_days_in_contributors_returned_period']:
                    flagged = 1
                    error_code_number = 3
                else:
                    for _idx, record in filtered_weights.iterrows():
                        if isinstance(record[trading_weights_col], str):
                            if not record[trading_weights_col].strip():
                                flagged = 1
                                error_code_number = 4
                            else:
                                if float(record[trading_weights_col]) < 0:
                                    flagged = 1
                                    error_code_number = 5
                        else:
                            if pd.isnull(record[trading_weights_col]):
                                flagged = 1
                                error_code_number = 4
                            if record[trading_weights_col] < 0:
                                flagged = 1
                                error_code_number = 5
                if flagged:
                    row = _apply_error_flag(row, 'E0' + str(error_code_number), da_error_flag_col, target_columns)
                else:
                    row['sum_of_trading_day_weights_over_contributors_returned_period'] = \
                        filtered_weights[trading_weights_col].sum()
            return row

    df_stage_two = _run_apply(working_dataframe, preliminary_stages, da_error_flag_col)

    return df_stage_two


# -------------------------------------------------------------------------------------------------------------
# SECTION: MIDPOINT SUB-FUNCTION
# -------------------------------------------------------------------------------------------------------------

def midpoint_subfunction(df_stage_two: pd.DataFrame,
                         trading_weights: pd.DataFrame,
                         target_columns: List,
                         domain_col: str,
                         expected_start_date_col: str,
                         expected_end_date_col: str,
                         contributor_returned_start_date_col: str,
                         contributor_returned_end_date_col: str,
                         set_to_mid_point_col: str,
                         equal_weighted_col: str,
                         use_calendar_days_col: str,
                         trading_date_col: str,
                         trading_period_start_col: str,
                         trading_period_end_col: str,
                         trading_weights_col: str,
                         trading_domain_col: str,
                         da_error_flag_col: str) -> pd.DataFrame:
    """
    Applies the midpoint method to the input data.

    :param df_stage_two: The dataframe containing the data as processed to this point.
    :param trading_weights: The trading day weight reference data required for processing.
    :param target_columns: The names of the columns in the input dataframe to be date_adjusted.
    :param domain_col: Name of the column holding the Domain in input_dataframe.
    :param set_to_mid_point_col: Name of the column holding the set to midpoint parameter.
    :param use_calendar_days_col: Name of the column holding the "use calendar days" option in input_dataframe.
    :param equal_weighted_col: Name of the column holding the "Set to equal weighted" option in input_dataframe.
    :param contributor_returned_start_date_col: Name of the column holding the contributors returned period start date.
    :param contributor_returned_end_date_col: Name of the column holding the contributors returned period end date.
    :param expected_start_date_col: Name of the column holding the expected period start date in input_dataframe.
    :param expected_end_date_col: Name of the column holding the expected period end date in input_dataframe.
    :param da_error_flag_col: Name of the column that the user wishes the error flag column to be called in the output.
    :param trading_date_col: Name of the column holding the dates in trading_weights.
    :param trading_weights_col: Name of the column holding the weights in the trading_weights DataFrame.
    :param trading_domain_col: Name of the column holding the domain in the trading_weights DataFrame.
    :param trading_period_start_col: Name of the column holding the trading period start date in the trading_weights DataFrame.
    :param trading_period_end_col: Name of the column holding the trading period end date in the trading_weights DataFrame.

    :raises TypeError: If the input dataframe is not a DataFrame.
    :raises TypeError: If the target columns parameter is not a List.
    :raises KeyError: If required columns referenced in the parameters cannot be found in the input dataframe.
    :raises KeyError: If columns referenced in target_columns parameter cannot be found in the input dataframe.

    :return: A dataframe holding data with the midpoint method applied.

    """

    # Basic validation checks
    # noinspection PyProtectedMember,PyUnresolvedReferences
    this_place = sys._getframe().f_code.co_name
    _basic_input_validation(this_place,
                            input_dataframe=df_stage_two,
                            target_columns=target_columns)

    # Validate required columns are in df_stage_two dataframe
    required_columns = [domain_col,
                        expected_start_date_col,
                        expected_end_date_col,
                        contributor_returned_start_date_col,
                        contributor_returned_end_date_col,
                        set_to_mid_point_col,
                        equal_weighted_col,
                        use_calendar_days_col,
                        da_error_flag_col
                        ]
    _required_column_validation(this_place, 'df_stage_two', df_stage_two, required_columns)

    working_dataframe = df_stage_two.copy()

    def mid_point_process(row):
        # Rule 3.3, flow chart 11,9: If midpoint not Y or YT, set defaults of APx = EPx.
        if row[set_to_mid_point_col] in ['Y', 'YT']:
            if row[equal_weighted_col] == 'Y':  # Flowchart 7a
                row[set_to_mid_point_col] = 'Y'
            else:  # Flowchart 7b
                # Set CRPS to earliest date >= CRPS with non-zero weight in same domain.
                non_zero_after_crps = trading_weights[
                    (trading_weights[trading_weights_col] > 0) &
                    (trading_weights[trading_date_col] >= row[contributor_returned_start_date_col]) &
                    (trading_weights[trading_domain_col] == row[domain_col])
                    ].sort_values(by=trading_date_col, ascending=True)

                # set CRPS, error if reference df is empty.
                if len(non_zero_after_crps) > 0:   # Flowchart 7c
                    min_date_index = non_zero_after_crps[trading_date_col].idxmin()
                    row[contributor_returned_start_date_col] = non_zero_after_crps.at[
                        min_date_index, trading_date_col]
                else:
                    row = _apply_error_flag(row, 'E12', da_error_flag_col, target_columns)
                    return row

                # CRPE = latest period <= CRPE with non-zero weight
                non_zero_before_crpe = trading_weights[
                    (trading_weights[trading_weights_col] > 0) &
                    (trading_weights[trading_date_col] <= row[contributor_returned_end_date_col]) &
                    (trading_weights[trading_domain_col] == row[domain_col])
                    ].sort_values(by=trading_date_col, ascending=True)

                # set CRPE, error if reference df is empty.
                if len(non_zero_before_crpe) > 0:   # Not on flowchart, added in testing.
                    max_date_index = non_zero_before_crpe[trading_date_col].idxmax()
                    row[contributor_returned_end_date_col] = non_zero_before_crpe.at[
                        max_date_index, trading_date_col]
                else:
                    row = _apply_error_flag(row, 'E12', da_error_flag_col, target_columns)
                    return row

            # Calculate midpoint  (Flowchart #8)
            date_diff = (
                row[contributor_returned_end_date_col] -
                row[contributor_returned_start_date_col]
            ).days + 1

            additional_days = int((date_diff / 2)
                                  if date_diff % 2 == 0
                                  else ((date_diff + 1) / 2))

            # Subtracting 1 from additional days as methodology count the the start date
            # as day one. (ie they add 20 to 10 and get 29! :)
            midpoint_date = (row[contributor_returned_start_date_col] +
                             timedelta(days=(additional_days-1)))

            row['midpoint_date'] = midpoint_date
            row['date_change_in_return_period_flag'] = ''

            # Use midpoint date value
            if not (row[expected_start_date_col] <=
                    midpoint_date <=
                    row[expected_end_date_col]):
                # Flowchart #10a
                row['date_change_in_return_period_flag'] = 'C'
                if row[use_calendar_days_col] == 'Y':
                    # Flowchart #10b
                    first_day = 1
                    last_day = monthrange(
                        midpoint_date.year,
                        midpoint_date.month
                    )[1]
                    row['actual_period_start_date'] = pd.Timestamp(
                        year=midpoint_date.year,
                        month=midpoint_date.month,
                        day=first_day
                    )
                    row['actual_period_end_date'] = pd.Timestamp(
                        year=midpoint_date.year,
                        month=midpoint_date.month,
                        day=last_day
                    )
                else:
                    # Flowchart #10c
                    midpoint_data = trading_weights[
                        (trading_weights[trading_date_col] == midpoint_date) &
                        (trading_weights[trading_domain_col] == row[domain_col])
                        ]
                    # Use midpoint date trading period dates.
                    if len(midpoint_data) == 1:  # Not on flowchart, added in testing.
                        row['actual_period_start_date'] = \
                            midpoint_data[trading_period_start_col].values[0]
                        row['actual_period_end_date'] = \
                            midpoint_data[trading_period_end_col].values[0]

                    # Error if it doesnt exist (or theres a duplicate row). This is
                    # normally picked up by E06 but in the case where a record had the
                    # wrong trading period date, there will be one missing, and one
                    # extra, which spoofs the tests for E06.
                    else:
                        row = _apply_error_flag(row,
                                                'E13',
                                                da_error_flag_col,
                                                target_columns)
                        return row
                return row  # From flowchart position 10b or 10c

        # Flowchart #9
        row['actual_period_start_date'] = row[expected_start_date_col]
        row['actual_period_end_date'] = row[expected_end_date_col]
        return row  # From flowchart position 9

    df_stage_three = _run_apply(working_dataframe, mid_point_process, da_error_flag_col)

    return df_stage_three


# -------------------------------------------------------------------------------------------------------------
# SECTION: SECONDARY WRANGLER SUB-FUNCTION
# -------------------------------------------------------------------------------------------------------------

def secondary_wrangler_subfunction(df_stage_three: pd.DataFrame,
                                   trading_weights: pd.DataFrame,
                                   target_columns: List,
                                   contributor_returned_start_date_col: str,
                                   contributor_returned_end_date_col: str,
                                   expected_start_date_col: str,
                                   expected_end_date_col: str,
                                   domain_col: str,
                                   equal_weighted_col: str,
                                   set_to_mid_point_col: str,
                                   short_period_parameter_col: str,
                                   long_period_parameter_col: str,
                                   da_error_flag_col: str,
                                   trading_date_col: str,
                                   trading_domain_col: str,
                                   trading_weights_col: str) -> pd.DataFrame:
    """
    Prepares the data for further processing by the date adjustment and average weekly methods as required.

    :param df_stage_three: The dataframe containing the data as processed to this point.
    :param trading_weights: The trading day weight reference data required for processing.
    :param target_columns: The names of the columns in the input dataframe to be date_adjusted.
    :param contributor_returned_start_date_col: Name of the column holding the contributors returned period start date.
    :param contributor_returned_end_date_col: Name of the column holding the contributors returned period end date.
    :param expected_start_date_col: Name of the column holding the expected period start date in input_dataframe.
    :param expected_end_date_col: Name of the column holding the expected period end date in input_dataframe.
    :param domain_col: Name of the column holding the Domain in input_dataframe.
    :param equal_weighted_col: Name of the column holding the "Set to equal weighted" option in input_dataframe.
    :param short_period_parameter_col: Name of the column holding the "short period parameter" in input_dataframe.
    :param long_period_parameter_col: Name of the column holding the "long period parameter" in input_dataframe.
    :param set_to_mid_point_col: Name of the column holding the "Set to mid-point" option in input_dataframe.
    :param da_error_flag_col: Name of the column that the user wishes the error flag column to be called in the output.
    :param trading_date_col: Name of the column holding the dates in trading_weights.
    :param trading_weights_col: Name of the column holding the weights in trading_weights.
    :param trading_domain_col: Name of the column holding the domain in trading_weights.

    :raises TypeError: If the input dataframe is not a DataFrame; If the trading weights reference data is not a DataFrame; If the target columns parameter is not a List.
    :raises KeyError: If required columns referenced in the parameters cannot be found in the input dataframe or the trading weights dataframe as appropriate; If columns referenced in target_columns parameter cannot be found in the input dataframe.

    :return: A dataframe holding data and structure ready to be passed into the midpoint method sub-function.

    """
    # Basic validation
    # noinspection PyProtectedMember,PyUnresolvedReferences
    this_place = sys._getframe().f_code.co_name
    _basic_input_validation(this_place,
                            input_dataframe=df_stage_three,
                            trading_weights=trading_weights,
                            target_columns=target_columns)

    # Validate required columns in input_dataframe
    required_columns = [contributor_returned_start_date_col, contributor_returned_end_date_col,
                        expected_start_date_col, expected_end_date_col, set_to_mid_point_col,
                        short_period_parameter_col, long_period_parameter_col, da_error_flag_col, domain_col]
    _required_column_validation(this_place, 'df_stage_three', df_stage_three, required_columns)

    # Validate required columns are in trading_weights dataframe
    required_columns = [trading_weights_col, trading_date_col, trading_domain_col]
    _required_column_validation(this_place, 'trading_weights', trading_weights, required_columns)

    working_df_1 = df_stage_three.copy()

    # Rule 3.3, flow chart 12a: If midpoint not YT, set N to APE - APN, 
    #   else 12b: set N to trimmed APE - APN.
    def mid_point_not_equal_yt(row):
        if row[set_to_mid_point_col] != 'YT':
            row['number_of_days_in_actual_returned_period'] = \
                (row['actual_period_end_date'] - (row['actual_period_start_date'])).days + 1
        else:
            # Set APS to earliest date >= APS with non-zero weight in same domain.
            non_zero_after_aps = trading_weights[
                (trading_weights[trading_weights_col] > 0) &
                (trading_weights[trading_date_col] >=
                    row['actual_period_start_date']) &
                (trading_weights[trading_domain_col] == row[domain_col])
                ].sort_values(by=trading_date_col, ascending=True)

            # set APS as weights will always exist due to earlier checks.
            min_date_index = non_zero_after_aps[trading_date_col].idxmin()
            aps = non_zero_after_aps.at[min_date_index, trading_date_col]

            # APE = latest period <= APE with non-zero weight
            non_zero_before_ape = trading_weights[
                (trading_weights[trading_weights_col] > 0) &
                (trading_weights[trading_date_col] <= 
                    row['actual_period_end_date']) &
                (trading_weights[trading_domain_col] == row[domain_col])
                ].sort_values(by=trading_date_col, ascending=True)

            # set APE as weights will always exist due to earlier checks.
            max_date_index = non_zero_before_ape[trading_date_col].idxmax()
            ape = non_zero_before_ape.at[max_date_index, trading_date_col]

            # Set N using trimmed APS and APE.
            row['number_of_days_in_actual_returned_period'] = (ape - aps).days + 1

        return row

    working_dataframe_2 = _run_apply(working_df_1, mid_point_not_equal_yt, da_error_flag_col)

    # Rule 5.4,5.5, flow chart 19:
    def short_and_long_parameter_validation(row):
        # 5.4 If less than short period parameter, mark length flag as 'S'
        if row['number_of_days_in_contributors_returned_period'] < int(row[short_period_parameter_col]):
            row['date_adjustment_length_flag'] = 'S'
        # 5.5 If greater than Long period parameter, mark length flag as 'L'
        if row['number_of_days_in_contributors_returned_period'] > int(row[long_period_parameter_col]):
            row['date_adjustment_length_flag'] = 'L'
        # 5.4,5.5 If params wrong way round, output 'SL' to flag.
        if int(row[short_period_parameter_col]) >= int(row[long_period_parameter_col]):
            row['date_adjustment_length_flag'] = 'SL'
        return row

    working_dataframe_3 = _run_apply(working_dataframe_2, short_and_long_parameter_validation,
                                     da_error_flag_col)

    def create_weights_n(row):

        if row[equal_weighted_col] == 'Y':
            row['sum_of_trading_day_weights_over_actual_returned_period'] = \
                row['number_of_days_in_actual_returned_period']
        else:
            flagged = 0
            error_code_number = 0
            mask = (trading_weights[trading_date_col] >= row['actual_period_start_date']) & \
                   (trading_weights[trading_date_col] <= row['actual_period_end_date']) & \
                   (trading_weights[trading_domain_col] == row[domain_col])
            filtered_weights = trading_weights.loc[mask]

            if len(filtered_weights.index) != row['number_of_days_in_actual_returned_period']:
                flagged = 1
                error_code_number = 6
            else:
                for _idx, record in filtered_weights.iterrows():
                    if isinstance(record[trading_weights_col], str):
                        if not record[trading_weights_col].strip():
                            flagged = 1
                            error_code_number = 7
                        else:
                            if float(record[trading_weights_col]) < 0:
                                flagged = 1
                                error_code_number = 8
                    else:
                        if pd.isnull(record[trading_weights_col]):
                            flagged = 1
                            error_code_number = 7
                        if record[trading_weights_col] < 0:
                            flagged = 1
                            error_code_number = 8
            if flagged:
                row['sum_of_trading_day_weights_over_actual_returned_period'] = 0
                row = _apply_error_flag(row, 'E0' + str(error_code_number), da_error_flag_col, target_columns)

            else:
                row['sum_of_trading_day_weights_over_actual_returned_period'] = \
                    filtered_weights[trading_weights_col].sum()
        return row

    working_dataframe_4 = _run_apply(working_dataframe_3, create_weights_n, da_error_flag_col)

    def span_overlap_less_than_one_day(row):
        latest_start = max(row[expected_start_date_col], row[contributor_returned_start_date_col])
        earliest_end = min(row[expected_end_date_col], row[contributor_returned_end_date_col])
        delta = (earliest_end - latest_start).days + 1
        span = max(0, delta)

        if row[set_to_mid_point_col] == 'N':
            if span < 1:
                row = _apply_error_flag(row, 'E09', da_error_flag_col, target_columns)
        return row

    df_stage_four = _run_apply(working_dataframe_4, span_overlap_less_than_one_day, da_error_flag_col)

    return df_stage_four


# -------------------------------------------------------------------------------------------------------------
# SECTION: DATE ADJUSTMENT SUB-FUNCTION
# -------------------------------------------------------------------------------------------------------------

def date_adjustment_subfunction(df_stage_four: pd.DataFrame,
                                target_columns: List,
                                da_error_flag_col: str) -> pd.DataFrame:
    """
    Prepares the data for further processing by the date adjustment and average weekly methods as required.

    :param df_stage_four: The dataframe containing the data as processed to this point.
    :param target_columns: The names of the columns in the input dataframe to be date_adjusted.
    :param da_error_flag_col: Name of the column that the user wishes the error flag column to be called in the output.

    :raises TypeError: If the input dataframe is not a DataFrame; If the target columns parameter is not a List.
    :raises KeyError: If required columns referenced in the parameters cannot be found in the input dataframe; If columns referenced in target_columns parameter cannot be found in the input dataframe.

    :return: A dataframe holding data with the date adjustment method applied.

    """

    # Basic validation
    # noinspection PyProtectedMember,PyUnresolvedReferences
    this_place = sys._getframe().f_code.co_name
    _basic_input_validation(this_place,
                            input_dataframe=df_stage_four,
                            target_columns=target_columns)

    # Validate required columns in input_dataframe
    required_columns = ['sum_of_trading_day_weights_over_contributors_returned_period',
                        'sum_of_trading_day_weights_over_actual_returned_period']
    _required_column_validation(this_place, 'df_stage_four', df_stage_four, required_columns)

    def da_method(row):

        # SPP83 - AC 3
        if row['sum_of_trading_day_weights_over_contributors_returned_period'] == 0:
            row = _apply_error_flag(row, 'E10', da_error_flag_col, target_columns)
            return row

        # SPP83 - AC 2
        if row['sum_of_trading_day_weights_over_actual_returned_period'] == 0:
            row = _apply_error_flag(row, 'E11', da_error_flag_col, target_columns)
            return row

        # SPP83 - AC 3
        for col in target_columns:
            da_col_name = 'date_adjusted_' + col
            row[da_col_name] = row[col] * \
                (row['sum_of_trading_day_weights_over_actual_returned_period'] /
                 row['sum_of_trading_day_weights_over_contributors_returned_period'])
        return row

    df_stage_five = _run_apply(df_stage_four, da_method, da_error_flag_col)

    return df_stage_five


# -------------------------------------------------------------------------------------------------------------
# SECTION: AVERAGE WEEKLY SUB-FUNCTION
# -------------------------------------------------------------------------------------------------------------

def average_weekly_subfunction(df_stage_five: pd.DataFrame,
                               average_weekly_questions_list: List,
                               da_error_flag_col: str) -> pd.DataFrame:
    """
    Applies the average weekly method to the input data.

    :param df_stage_five: The dataframe containing the data as processed to this point.
    :param average_weekly_questions_list: The names of the columns in the input dataframe to be processed by the average weekly method.
    :param da_error_flag_col: Name of the column that the user wishes the error flag column to be called in the output.

    :raises TypeError: If the input dataframe is not a DataFrame; If the average weekly questions list parameter is not a List.
    :raises KeyError: If required columns referenced in the parameters cannot be found in the input dataframe; If columns referenced in average_weekly_questions_list parameter cannot be found in the input dataframe.

    :return: A dataframe holding data with the average weekly method applied.

    """

    # Basic validation
    # noinspection PyProtectedMember,PyUnresolvedReferences
    this_place = sys._getframe().f_code.co_name
    _basic_input_validation(this_place,
                            input_dataframe=df_stage_five,
                            target_columns=average_weekly_questions_list)

    # Validate required columns in input_dataframe
    required_columns = average_weekly_questions_list.copy()
    _required_column_validation(this_place, 'df_stage_five', df_stage_five, required_columns)

    # Apply average weekly to average_weekly_questions_list, if any.

    def set_average_weekly(row):
        for base_col in average_weekly_questions_list:
            source_col = 'date_adjusted_' + base_col
            new_col = 'average_weekly_' + base_col
            row[new_col] = (7 * row[source_col]) / row['number_of_days_in_actual_returned_period']
        return row

    df_stage_six = _run_apply(df_stage_five, set_average_weekly, da_error_flag_col)

    return df_stage_six


# -------------------------------------------------------------------------------------------------------------
# GENERAL / PRIVATE FUNCTIONS: Module level functions needed in processing and by test suite.
#                             (Keep them simple, short and self-contained)
# -------------------------------------------------------------------------------------------------------------

def _convert_question_string_to_list(input_string: str) -> List:
    """
    :param input_string:
    :return string converted into a list:
    """
    # Validate input is string
    if not isinstance(input_string, str):
        input_string = str(input_string)

    # Remove spaces after commas
    input_string = input_string.replace(", ", ",")
    # Remove existing quotes, split will replace.
    input_string = input_string.replace("\"", "")
    input_string = input_string.replace("'", "")

    # Remove any leading and training []s
    if input_string:
        if input_string[0] == '[' and input_string[-1] == ']':
            input_string = input_string[1:-1]

    # Convert
    output_list = input_string.split(",")
    return output_list


def _basic_input_validation(this_place: str,
                            input_dataframe: pd.DataFrame,
                            target_columns: List = None,
                            trading_weights: pd.DataFrame = None) -> str:
    """
    :param this_place:
    :param input_dataframe:
    :param target_columns:
    :param trading_weights:

    :raises TypeError

    """
    # Validate input is a dataframe
    if not isinstance(input_dataframe, pd.DataFrame):
        msg = 'Param "input_dataframe" for function ' + this_place + ' '
        msg += 'should be of type DataFrame, not ' + str(type(input_dataframe)) + '.'
        raise TypeError(msg)

    # Validate target_columns is a list
    if target_columns is not None:
        if not isinstance(target_columns, list):
            msg = 'Param "target_columns" for function ' + this_place + ' '
            msg += 'should be of type List, not ' + str(type(target_columns)) + '.'
            raise TypeError(msg)

    # Validate trading_weights is a dataframe
    if trading_weights is not None:
        if not isinstance(trading_weights, pd.DataFrame):
            msg = 'Param "trading_weights" for function ' + this_place + ' '
            msg += 'should be of type DataFrame, not ' + str(type(trading_weights)) + '.'
            raise TypeError(msg)

    return 'OK'


def _required_column_validation(this_place: str,
                                dataframe_name: str,
                                dataframe_to_check: pd.DataFrame,
                                required_columns: List) -> str:
    """
    :param this_place:
    :param dataframe_name:
    :param dataframe_to_check:
    :param required_columns:

    :raises TypeError
    :raises KeyError

    :returns str

    """
    # Validate parameters
    if not isinstance(dataframe_name, str):
        msg = 'Param "dataframe_name" being sent to _required_column_validation from ' + this_place + ' '
        msg += 'should be of type String, not ' + str(type(dataframe_name)) + '.'
        raise TypeError(msg)

    if not isinstance(dataframe_to_check, pd.DataFrame):
        msg = 'Param "dataframe_to_check" being sent to _required_column_validation from ' + this_place + ' '
        msg += 'should be of type DataFrame, not ' + str(type(dataframe_to_check)) + '.'
        raise KeyError(msg)

    if not isinstance(required_columns, list):
        msg = 'Param "target_columns" being sent to _required_column_validation from' + this_place + ' '
        msg += 'should be of type List, not ' + str(type(required_columns)) + '.'
        raise TypeError(msg)

    # Validate columns are in dataframe
    for column_name in required_columns:
        if column_name not in dataframe_to_check:
            msg = 'Required column "' + column_name + '" not found in ' + dataframe_name + ' '
            msg += 'passed to _required_column_validation from ' + this_place + '.'
            raise KeyError(msg)

    return 'OK'


def _run_apply(input_df: pd.DataFrame,
               function_to_apply: any,
               da_error_flag_col: str) -> pd.DataFrame:
    """
    :param input_df:
    :param function_to_apply:
    :param da_error_flag_col:

    :returns DataFrame that results from function application:
    """

    error_code_list = _generate_error_code_list()
    output_df = input_df.apply(
            lambda row:
            function_to_apply(row)
            if row[da_error_flag_col] not in error_code_list
            else row,
            axis=1
        )
    return output_df


def _apply_error_flag(row: pd.Series,
                      error_code: str,
                      da_error_flag_col: str,
                      target_columns: List) -> pd.Series:
    """
    :param row:
    :param error_code:
    :param da_error_flag_col:
    :param target_columns:
    :return: row
    :rtype Series:
    """
    row_cols = row.index.values
    error_code_list = _generate_error_code_list()
    # Validate error code.
    if error_code not in error_code_list:
        msg = 'Error code "' + str(error_code) + '" not found in error_code_list.'
        raise KeyError(msg)

    # Set error code into correct column
    row[da_error_flag_col] = error_code

    # Set columns listed in zero_cols to 0 if they exist
    zero_cols = ['number_of_days_in_contributors_returned_period',
                 'sum_of_trading_day_weights_over_contributors_returned_period',
                 'sum_of_trading_day_weights_over_actual_returned_period']

    for col_name in zero_cols:
        if col_name in row_cols:
            row[col_name] = 0

    # Set columns listed in target_columns to nan
    for col in target_columns:
        # NB: We nullify output data if it exists.
        #     The users need to refer to the data in the target column itself.
        temp_name_1 = 'date_adjusted_' + col
        if temp_name_1 in row_cols:
            row[temp_name_1] = np.nan
        temp_name_2 = 'average_weekly_' + col
        if temp_name_2 in row_cols:
            row[temp_name_2] = np.nan
    return row


def _generate_error_code_list() -> List:
    """
    :return: List
    """
    error_code_list = []
    for x in range(0, 16):
        error_code_list.append('E' + str(x).zfill(2))
    return error_code_list


def _set_dtypes(df, dtype_dict, target_columns=tuple()):
    """
    :param df:
    :param dtype_dict:
    :param target_columns:
    :rtype: DataFrame
    """

    if not isinstance(dtype_dict, dict):
        raise TypeError("dtype_dict is not a dict so _set_dtypes function cannot run.")

    # Check dtypes and change where necessary
    col_names = df.columns.tolist()

    key = '?'
    try:
        for key, val in dtype_dict.items():
            if key in col_names:
                if df[key].dtype != val:
                    if val == 'datetime64[ns]':
                        df[key] = pd.to_datetime(df[key], format='%Y%m%d', errors='coerce')
                    elif val in ['int64', 'float64']:
                        df[key] = pd.to_numeric(df[key], errors='coerce')
                    else:
                        df = df.astype({key: val})
    except ValueError as err:
        raise ValueError('Could not process ' + str(key) + ', ' + str(err))

    try:
        for key, val in dtype_dict.items():
            if key in col_names:
                if key in dtype_dict['domain_col_list']:
                    df[key] = df[key].astype("string")
    except ValueError as err:
        raise ValueError('Could not stringify ' + str(key) + ', ' + str(err))

    col = '?'
    try:
        for col in target_columns:
            if col in col_names:
                if df[col].dtype != 'float64':
                    df[col] = pd.to_numeric(df[col], errors='coerce')
    except ValueError as err:
        raise ValueError('Could not process ' + str(col) + ', ' + str(err))

    return df
