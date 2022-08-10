import calendar as cal
from unittest import TestCase

import numpy as np
import pandas as pd

# noinspection PyProtectedMember
from sml_small.date_adjustment import (_convert_question_string_to_list, _generate_error_code_list, _set_dtypes,
                                       average_weekly_subfunction, date_adjustment, date_adjustment_subfunction,
                                       generate_average_weekly_questions, midpoint_subfunction,
                                       missing_value_subfunction, primary_wrangler_subfunction,
                                       secondary_wrangler_subfunction)

pd.options.mode.chained_assignment = None
pd.set_option('display.max_columns', 30)
pd.set_option('display.max_colwidth', 999)

target_columns = ['variable_to_be_date_adjusted_Q20',
                  'variable_to_be_date_adjusted_Q21',
                  'variable_to_be_date_adjusted_Q22',
                  'variable_to_be_date_adjusted_Q23',
                  'variable_to_be_date_adjusted_Q24',
                  'variable_to_be_date_adjusted_Q25',
                  'variable_to_be_date_adjusted_Q26']

contributor_returned_start_date_col = 'contributors_returned_period_start_date'
contributor_returned_end_date_col = 'contributors_returned_period_end_date'
expected_start_date_col = 'expected_period_start_date'
expected_end_date_col = 'expected_period_end_date'
da_error_flag_col = 'date_adjustment_error_flag'
equal_weighted_col = 'set_to_equal_weighted'
domain_col = 'domain_SIC_code'
set_to_mid_point_col = 'set_to_mid_point'
use_calendar_days_col = 'use_calendar_days'
short_period_parameter_col = 'short_period_parameter'
long_period_parameter_col = 'long_period_parameter'
average_weekly_col = 'average_weekly'
trading_domain_col = 'domain'
trading_date_col = 'date'
trading_weights_col = 'weight'
trading_period_start_col = 'period_start'
trading_period_end_col = 'period_end'
ignore_multi_aw_param_error = True

average_weekly_questions = generate_average_weekly_questions("A", target_columns)
error_codes_list = _generate_error_code_list()
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

filter_err = "No test was performed, all data was filtered out by criteria."
wcr_col = 'sum_of_trading_day_weights_over_contributors_returned_period'
dcr_col = 'number_of_days_in_contributors_returned_period'
war_col = 'sum_of_trading_day_weights_over_actual_returned_period'
dar_col = 'number_of_days_in_actual_returned_period'


def load_csv(filepath):
    # read in base info
    df = pd.read_csv(filepath)
    # Check df dtypes and change where necessary
    df = _set_dtypes(df, dtype_dict, target_columns)
    return df


fxt = "fixtures/date_adjustment"
trading_weights = load_csv(f"{fxt}/da_trading_weights_data.csv")


# ====================================================================================
# --------------- TESTING TEMPLATE ---------------------------
# ====================================================================================
# --- Test fails with type error if no input ---
# --- Test type validation on the input dataframe(s) ---
# --- Test type validation on the target column lists(s) ---
# --- Test if cols missing from input dataframe(s) ---
# --- Test if output is a dataframe (or the expected type)---
# --- Test if output contents is as expected, both new columns and data content ---
# --- Test any other error based outputs ---

# IMPORTANT:
# 1) If the test contains any form of condition or loop, you must test the logical
#    branches to ensure that each assert is actually being performed.
# 2) Do not test internal structure of functions, it may be refactored. Stick
#    to the inputs and outputs.
# 3) Avoid referring to specific rows of test data where possible, they may change.
#    Instead, follow the existing templates to add conditional tests.
# 4) If you load the test data in for each test rather than as a module level
#    constant, you can amend data in the tests without needing new test data.
# ====================================================================================

# --------------------------------------------------------------------------------------
# TESTS: DATE ADJUSTMENT MAIN METHOD
# --------------------------------------------------------------------------------------

# noinspection PyTypeChecker
class TestDateAdjustment(TestCase):

    # --- Test fails with type error if no input. ---

    def test_input_provided(self):
        self.assertRaises(TypeError)

    # --- Test type validation on the input dataframe(s)  ---

    def test_validate_input_dataframe_type(self):
        with self.assertRaises(TypeError):
            date_adjustment(
                ["Not_A_Dataframe"], trading_weights, target_columns,
                contributor_returned_start_date_col, contributor_returned_end_date_col,
                expected_start_date_col, expected_end_date_col, domain_col,
                short_period_parameter_col, long_period_parameter_col, equal_weighted_col,
                set_to_mid_point_col, use_calendar_days_col, average_weekly_col,
                da_error_flag_col, trading_date_col, trading_weights_col,
                trading_domain_col, trading_period_start_col, trading_period_end_col,
                ignore_multi_aw_param_error)

    def test_validate_trading_weights_type(self):
        with self.assertRaises(TypeError):
            df_loc = f"{fxt}/da_date_adjustment_method_input.csv"
            test_dataframe = load_csv(df_loc)
            date_adjustment(
                test_dataframe, ["Not_A_Dataframe"], target_columns,
                contributor_returned_start_date_col, contributor_returned_end_date_col,
                expected_start_date_col, expected_end_date_col, domain_col,
                short_period_parameter_col, long_period_parameter_col, equal_weighted_col,
                set_to_mid_point_col, use_calendar_days_col, average_weekly_col,
                da_error_flag_col, trading_date_col, trading_weights_col,
                trading_domain_col, trading_period_start_col, trading_period_end_col,
                ignore_multi_aw_param_error)

    # --- Test type validation on the target column lists(s) ---

    def test_validate_target_columns_type(self):
        with self.assertRaises(TypeError):
            df_loc = f"{fxt}/da_date_adjustment_method_input.csv"
            test_dataframe = load_csv(df_loc)
            date_adjustment(
                test_dataframe, trading_weights, "Not  list",
                contributor_returned_start_date_col, contributor_returned_end_date_col,
                expected_start_date_col, expected_end_date_col, domain_col,
                short_period_parameter_col, long_period_parameter_col, equal_weighted_col,
                set_to_mid_point_col, use_calendar_days_col, average_weekly_col,
                da_error_flag_col, trading_date_col, trading_weights_col,
                trading_domain_col, trading_period_start_col, trading_period_end_col,
                ignore_multi_aw_param_error)

    # --- Test if cols missing from input dataframe(s) ---

    def test_validate_required_cols_in_input_dataframe(self):
        df_loc = f"{fxt}/da_date_adjustment_method_input.csv"
        test_dataframe = load_csv(df_loc)
        bad_dataframe = test_dataframe.drop(short_period_parameter_col, axis=1)
        with self.assertRaises(KeyError):
            date_adjustment(
                bad_dataframe, trading_weights, target_columns,
                contributor_returned_start_date_col, contributor_returned_end_date_col,
                expected_start_date_col, expected_end_date_col, domain_col,
                short_period_parameter_col, long_period_parameter_col, equal_weighted_col,
                set_to_mid_point_col, use_calendar_days_col, average_weekly_col,
                da_error_flag_col, trading_date_col, trading_weights_col,
                trading_domain_col, trading_period_start_col, trading_period_end_col,
                ignore_multi_aw_param_error)

    def test_validate_reserved_column_names_in_input_dataframe(self):
        df_loc = f"{fxt}/da_date_adjustment_method_input.csv"
        test_dataframe = load_csv(df_loc)
        bad_dataframe = test_dataframe.drop(set_to_mid_point_col, axis=1)
        bad_dataframe['midpoint'] = 'Y'
        with self.assertRaises(ValueError):
            date_adjustment(
                bad_dataframe, trading_weights, target_columns,
                contributor_returned_start_date_col, contributor_returned_end_date_col,
                expected_start_date_col, expected_end_date_col, domain_col,
                short_period_parameter_col, long_period_parameter_col, equal_weighted_col,
                'midpoint', use_calendar_days_col, average_weekly_col,
                da_error_flag_col, trading_date_col, trading_weights_col,
                trading_domain_col, trading_period_start_col, trading_period_end_col,
                ignore_multi_aw_param_error)

    def test_validate_target_columns_in_input_dataframe(self):
        bad_target_list = target_columns.copy()
        bad_target_list.append('this_col_doesnt_exist_in_input')
        with self.assertRaises(KeyError):
            df_loc = f"{fxt}/da_date_adjustment_method_input.csv"
            test_dataframe = load_csv(df_loc)
            date_adjustment(
                test_dataframe, trading_weights, bad_target_list,
                contributor_returned_start_date_col, contributor_returned_end_date_col,
                expected_start_date_col, expected_end_date_col, domain_col,
                short_period_parameter_col, long_period_parameter_col, equal_weighted_col,
                set_to_mid_point_col, use_calendar_days_col, average_weekly_col,
                da_error_flag_col, trading_date_col, trading_weights_col,
                trading_domain_col, trading_period_start_col, trading_period_end_col,
                ignore_multi_aw_param_error)

    def test_validate_required_cols_in_trading_weight(self):
        df_loc = f"{fxt}/da_date_adjustment_method_input.csv"
        tw_loc = f"{fxt}/da_trading_weights_data.csv"
        test_dataframe = load_csv(df_loc)
        test_weights = load_csv(tw_loc)
        bad_weights = test_weights.drop(trading_domain_col, axis=1)
        with self.assertRaises(KeyError):
            date_adjustment(
                test_dataframe, bad_weights, target_columns,
                contributor_returned_start_date_col, contributor_returned_end_date_col,
                expected_start_date_col, expected_end_date_col, domain_col,
                short_period_parameter_col, long_period_parameter_col, equal_weighted_col,
                set_to_mid_point_col, use_calendar_days_col, average_weekly_col,
                da_error_flag_col, trading_date_col, trading_weights_col,
                trading_domain_col, trading_period_start_col, trading_period_end_col,
                ignore_multi_aw_param_error)

    # --- Test if output is a dataframe ---

    def test_return_is_dataframe(self):
        df_loc = f"{fxt}/da_date_adjustment_method_input.csv"
        test_dataframe = load_csv(df_loc)
        ret_val = date_adjustment(
            test_dataframe, trading_weights, target_columns,
            contributor_returned_start_date_col, contributor_returned_end_date_col,
            expected_start_date_col, expected_end_date_col, domain_col,
            short_period_parameter_col, long_period_parameter_col, equal_weighted_col,
            set_to_mid_point_col, use_calendar_days_col, average_weekly_col,
            da_error_flag_col, trading_date_col, trading_weights_col, trading_domain_col,
            trading_period_start_col, trading_period_end_col,
            ignore_multi_aw_param_error)
        assert isinstance(ret_val, type(pd.DataFrame()))
        # Not part of the actual test, but a good place to record the output as a CSV.
        ret_val.to_csv('testing_output.csv', index=False)

    # --- Test if output(s) are as expected. ---

    def test_da_columns_are_correct(self):
        actually_tested = 0
        df_loc = f"{fxt}/da_date_adjustment_method_input.csv"
        test_dataframe = load_csv(df_loc)
        ret_val = date_adjustment(
            test_dataframe, trading_weights, target_columns,
            contributor_returned_start_date_col, contributor_returned_end_date_col,
            expected_start_date_col, expected_end_date_col, domain_col,
            short_period_parameter_col, long_period_parameter_col, equal_weighted_col,
            set_to_mid_point_col, use_calendar_days_col, average_weekly_col,
            da_error_flag_col, trading_date_col, trading_weights_col, trading_domain_col,
            trading_period_start_col, trading_period_end_col, ignore_multi_aw_param_error)
        sum_actual = war_col
        sum_returned = wcr_col
        for _idx, row in ret_val.iterrows():
            if row[da_error_flag_col] not in error_codes_list:
                for col_name in target_columns:
                    calc_col = 'date_adjusted_' + col_name
                    returned_value = row[calc_col]
                    expected_value = (
                            row[col_name] * (row[sum_actual] / row[sum_returned])
                    )
                    actually_tested = 1
                    assert returned_value == expected_value
        if not actually_tested:
            raise AssertionError(filter_err)

    def test_da_q27_not_present(self):
        df_loc = f"{fxt}/da_date_adjustment_method_input.csv"
        test_dataframe = load_csv(df_loc)
        ret_val = date_adjustment(
            test_dataframe, trading_weights, target_columns,
            contributor_returned_start_date_col, contributor_returned_end_date_col,
            expected_start_date_col, expected_end_date_col, domain_col,
            short_period_parameter_col, long_period_parameter_col, equal_weighted_col,
            set_to_mid_point_col, use_calendar_days_col, average_weekly_col,
            da_error_flag_col, trading_date_col, trading_weights_col, trading_domain_col,
            trading_period_start_col, trading_period_end_col, ignore_multi_aw_param_error)
        bad_col = 'date_adjusted_variable_to_be_date_adjusted_Q27'
        assert bad_col not in ret_val.columns.tolist()

    def test_aw_columns_are_correct(self):
        actually_tested = 0
        df_loc = f"{fxt}/da_date_adjustment_method_input.csv"
        test_dataframe = load_csv(df_loc)
        ret_val = date_adjustment(
            test_dataframe, trading_weights, target_columns,
            contributor_returned_start_date_col, contributor_returned_end_date_col,
            expected_start_date_col, expected_end_date_col, domain_col,
            short_period_parameter_col, long_period_parameter_col, equal_weighted_col,
            set_to_mid_point_col, use_calendar_days_col, average_weekly_col,
            da_error_flag_col, trading_date_col, trading_weights_col, trading_domain_col,
            trading_period_start_col, trading_period_end_col, ignore_multi_aw_param_error)
        act_days = dar_col
        for _idx, row in ret_val.iterrows():
            if row[da_error_flag_col] not in error_codes_list:
                for base_col in average_weekly_questions:
                    check_col = 'average_weekly_' + base_col
                    source_col = 'date_adjusted_' + base_col
                    actually_tested = 1
                    assert row[check_col] == (7 * row[source_col]) / row[act_days]
        if not actually_tested:
            if not average_weekly_questions:
                msg = "No test was performed, average_weekly_questions is empty list."
                raise AssertionError(msg)
            else:
                raise AssertionError(filter_err)

    def test_aw_q27_not_present(self):
        df_loc = f"{fxt}/da_date_adjustment_method_input.csv"
        test_dataframe = load_csv(df_loc)
        ret_val = date_adjustment(
            test_dataframe, trading_weights, target_columns,
            contributor_returned_start_date_col, contributor_returned_end_date_col,
            expected_start_date_col, expected_end_date_col, domain_col,
            short_period_parameter_col, long_period_parameter_col, equal_weighted_col,
            set_to_mid_point_col, use_calendar_days_col, average_weekly_col,
            da_error_flag_col, trading_date_col, trading_weights_col, trading_domain_col,
            trading_period_start_col, trading_period_end_col, ignore_multi_aw_param_error)
        bad_col = 'average_weekly_variable_to_be_date_adjusted_Q27'
        assert bad_col not in ret_val.columns.tolist()

    def test_mid_point_bypass_actual_dates(self):
        actually_tested = 0
        df_loc = f"{fxt}/da_date_adjustment_method_input.csv"
        test_dataframe = load_csv(df_loc)
        ret_val = date_adjustment(
            test_dataframe, trading_weights, target_columns,
            contributor_returned_start_date_col, contributor_returned_end_date_col,
            expected_start_date_col, expected_end_date_col, domain_col,
            short_period_parameter_col, long_period_parameter_col, equal_weighted_col,
            set_to_mid_point_col, use_calendar_days_col, average_weekly_col,
            da_error_flag_col, trading_date_col, trading_weights_col, trading_domain_col,
            trading_period_start_col, trading_period_end_col, ignore_multi_aw_param_error)
        for _idx, row in ret_val.iterrows():
            if (row[set_to_mid_point_col] == 'N' and
                    row[da_error_flag_col] not in error_codes_list):
                actually_tested = 1
                assert row['actual_period_start_date'] == row[expected_start_date_col]
                assert row['actual_period_end_date'] == row[expected_end_date_col]

        if not actually_tested:
            raise AssertionError(filter_err)

    def test_basic_mid_point_use_gives_actual_equals_expected(self):
        actually_tested = 0
        df_loc = f"{fxt}/da_date_adjustment_method_input.csv"
        test_dataframe = load_csv(df_loc)
        ret_val = date_adjustment(
            test_dataframe, trading_weights, target_columns,
            contributor_returned_start_date_col, contributor_returned_end_date_col,
            expected_start_date_col, expected_end_date_col, domain_col,
            short_period_parameter_col, long_period_parameter_col, equal_weighted_col,
            set_to_mid_point_col, use_calendar_days_col, average_weekly_col,
            da_error_flag_col, trading_date_col, trading_weights_col, trading_domain_col,
            trading_period_start_col, trading_period_end_col, ignore_multi_aw_param_error)
        for _idx, row in ret_val.iterrows():
            if (row[set_to_mid_point_col] == 'Y' and
                    row[equal_weighted_col] == 'Y' and
                    row[da_error_flag_col] not in error_codes_list and
                    (row[expected_start_date_col] <=
                     row['midpoint_date'] <=
                     row[expected_end_date_col])):
                actually_tested = 1
                assert row['date_change_in_return_period_flag'] != 'C'
                assert row['actual_period_start_date'] == row[expected_start_date_col]
                assert row['actual_period_end_date'] == row[expected_end_date_col]

        if not actually_tested:
            raise AssertionError(filter_err)

    def test_mid_point_change_actual_use_calendar_month_dates(self):
        actually_tested = 0
        df_loc = f"{fxt}/da_date_adjustment_method_input.csv"
        test_dataframe = load_csv(df_loc)
        ret_val = date_adjustment(
            test_dataframe, trading_weights, target_columns,
            contributor_returned_start_date_col, contributor_returned_end_date_col,
            expected_start_date_col, expected_end_date_col, domain_col,
            short_period_parameter_col, long_period_parameter_col, equal_weighted_col,
            set_to_mid_point_col, use_calendar_days_col, average_weekly_col,
            da_error_flag_col, trading_date_col, trading_weights_col, trading_domain_col,
            trading_period_start_col, trading_period_end_col, ignore_multi_aw_param_error)
        for _idx, row in ret_val.iterrows():
            if (row[use_calendar_days_col] == 'Y' and
                    row[da_error_flag_col] not in error_codes_list and
                    not (row[expected_start_date_col] <=
                         row['midpoint_date'] <=
                         row[expected_end_date_col])):
                actually_tested = 1
                first_day = 1
                last_day = cal.monthrange(
                    row['midpoint_date'].year,
                    row['midpoint_date'].month
                )[1]
                calculated_start_date = pd.Timestamp(
                    year=row['midpoint_date'].year,
                    month=row['midpoint_date'].month,
                    day=first_day
                )
                calculated_end_date = pd.Timestamp(
                    year=row['midpoint_date'].year,
                    month=row['midpoint_date'].month,
                    day=last_day
                )
                assert row['date_change_in_return_period_flag'] == 'C'
                assert row['actual_period_start_date'] == calculated_start_date
                assert row['actual_period_end_date'] == calculated_end_date
        if not actually_tested:
            raise AssertionError(filter_err)

    # Output via flowchart route 10c
    def test_mid_point_change_actual_use_trading_period_dates(self):
        actually_tested = 0
        df_loc = f"{fxt}/da_date_adjustment_method_input.csv"
        test_dataframe = load_csv(df_loc)
        ret_val = date_adjustment(
            test_dataframe, trading_weights, target_columns,
            contributor_returned_start_date_col, contributor_returned_end_date_col,
            expected_start_date_col, expected_end_date_col, domain_col,
            short_period_parameter_col, long_period_parameter_col, equal_weighted_col,
            set_to_mid_point_col, use_calendar_days_col, average_weekly_col,
            da_error_flag_col, trading_date_col, trading_weights_col, trading_domain_col,
            trading_period_start_col, trading_period_end_col, ignore_multi_aw_param_error)
        for _idx, row in ret_val.iterrows():
            if (row[set_to_mid_point_col] != 'N' and
                    row[use_calendar_days_col] == 'N' and
                    row[da_error_flag_col] not in error_codes_list and
                    not (row[expected_start_date_col] <=
                         row['midpoint_date'] <=
                         row[expected_end_date_col])):
                actually_tested = 1
                midpoint_data = trading_weights[
                    (trading_weights[trading_date_col] == row['midpoint_date']) &
                    (trading_weights[trading_domain_col] == row[domain_col])
                    ]
                calculated_start_date = \
                    midpoint_data[trading_period_start_col].values[0]
                calculated_end_date = \
                    midpoint_data[trading_period_end_col].values[0]
                assert row['date_change_in_return_period_flag'] == 'C'
                assert row['actual_period_start_date'] == calculated_start_date
                assert row['actual_period_end_date'] == calculated_end_date
        if not actually_tested:
            raise AssertionError(filter_err)

    def test_equal_weighted_y_correct(self):
        actually_tested = 0
        df_loc = f"{fxt}/da_date_adjustment_method_input.csv"
        test_dataframe = load_csv(df_loc)
        ret_val = date_adjustment(
            test_dataframe, trading_weights, target_columns,
            contributor_returned_start_date_col, contributor_returned_end_date_col,
            expected_start_date_col, expected_end_date_col, domain_col,
            short_period_parameter_col, long_period_parameter_col, equal_weighted_col,
            set_to_mid_point_col, use_calendar_days_col, average_weekly_col,
            da_error_flag_col, trading_date_col, trading_weights_col, trading_domain_col,
            trading_period_start_col, trading_period_end_col, ignore_multi_aw_param_error)
        returned_weights = wcr_col
        returned_days = dcr_col
        for _idx, row in ret_val.iterrows():
            if (row[equal_weighted_col] == 'Y' and
                    row[da_error_flag_col] not in error_codes_list):
                actually_tested = 1
                assert (row[returned_weights] == row[returned_days]), \
                    "The m weight should be summed correctly"
        if not actually_tested:
            raise AssertionError(filter_err)

    def test_long_period_marker_set_on_warning(self):
        actually_tested = 0
        df_loc = f"{fxt}/da_date_adjustment_method_input.csv"
        test_dataframe = load_csv(df_loc)
        ret_val = date_adjustment(
            test_dataframe, trading_weights, target_columns,
            contributor_returned_start_date_col, contributor_returned_end_date_col,
            expected_start_date_col, expected_end_date_col, domain_col,
            short_period_parameter_col, long_period_parameter_col, equal_weighted_col,
            set_to_mid_point_col, use_calendar_days_col, average_weekly_col,
            da_error_flag_col, trading_date_col, trading_weights_col, trading_domain_col,
            trading_period_start_col, trading_period_end_col, ignore_multi_aw_param_error)
        for _idx, row in ret_val.iterrows():
            if (row[dcr_col]
                    > row[long_period_parameter_col]
                    > row[short_period_parameter_col]
                    and row[da_error_flag_col] not in error_codes_list):
                actually_tested = 1
                assert row['date_adjustment_length_flag'] == 'L'
        if not actually_tested:
            raise AssertionError(filter_err)

    def test_short_period_marker_set_on_warning(self):
        actually_tested = 0
        df_loc = f"{fxt}/da_date_adjustment_method_input.csv"
        test_dataframe = load_csv(df_loc)
        ret_val = date_adjustment(
            test_dataframe, trading_weights, target_columns,
            contributor_returned_start_date_col, contributor_returned_end_date_col,
            expected_start_date_col, expected_end_date_col, domain_col,
            short_period_parameter_col, long_period_parameter_col, equal_weighted_col,
            set_to_mid_point_col, use_calendar_days_col, average_weekly_col,
            da_error_flag_col, trading_date_col, trading_weights_col, trading_domain_col,
            trading_period_start_col, trading_period_end_col, ignore_multi_aw_param_error)
        for _idx, row in ret_val.iterrows():
            if (row[dcr_col]
                    < row[short_period_parameter_col]
                    < row[long_period_parameter_col]
                    and row[da_error_flag_col] not in error_codes_list):
                actually_tested = 1
                assert row['date_adjustment_length_flag'] == 'S'
        if not actually_tested:
            raise AssertionError(filter_err)

    def test_double_period_marker_set_on_warning(self):
        actually_tested = 0
        df_loc = f"{fxt}/da_date_adjustment_method_input.csv"
        test_dataframe = load_csv(df_loc)
        ret_val = date_adjustment(
            test_dataframe, trading_weights, target_columns,
            contributor_returned_start_date_col, contributor_returned_end_date_col,
            expected_start_date_col, expected_end_date_col, domain_col,
            short_period_parameter_col, long_period_parameter_col, equal_weighted_col,
            set_to_mid_point_col, use_calendar_days_col, average_weekly_col,
            da_error_flag_col, trading_date_col, trading_weights_col, trading_domain_col,
            trading_period_start_col, trading_period_end_col, ignore_multi_aw_param_error)
        for _idx, row in ret_val.iterrows():
            if (row[short_period_parameter_col] > row[long_period_parameter_col]
                    and row[da_error_flag_col] not in error_codes_list):
                actually_tested = 1
                assert row['date_adjustment_length_flag'] == 'SL'
        if not actually_tested:
            raise AssertionError(filter_err)

    # --- Test any other error based outputs ---

    def test_bad_average_weekly_param_fast_fail(self):
        df_loc = f"{fxt}/da_date_adjustment_method_input.csv"
        bad_param_df = load_csv(df_loc)
        bad_param_df[average_weekly_col] = 'Badly formatted parameter'
        ret_val = date_adjustment(
            bad_param_df, trading_weights, target_columns,
            contributor_returned_start_date_col, contributor_returned_end_date_col,
            expected_start_date_col, expected_end_date_col, domain_col,
            short_period_parameter_col, long_period_parameter_col, equal_weighted_col,
            set_to_mid_point_col, use_calendar_days_col, average_weekly_col,
            da_error_flag_col, trading_date_col, trading_weights_col, trading_domain_col,
            trading_period_start_col, trading_period_end_col, ignore_multi_aw_param_error)
        assert (ret_val[da_error_flag_col] == 'E00').all()

    def test_multi_aw_param_fast_fail(self):
        df_loc = f"{fxt}/da_date_adjustment_method_input.csv"
        test_dataframe = load_csv(df_loc)
        ret_val = date_adjustment(
            test_dataframe, trading_weights, target_columns,
            contributor_returned_start_date_col, contributor_returned_end_date_col,
            expected_start_date_col, expected_end_date_col, domain_col,
            short_period_parameter_col, long_period_parameter_col, equal_weighted_col,
            set_to_mid_point_col, use_calendar_days_col, average_weekly_col,
            da_error_flag_col, trading_date_col, trading_weights_col, trading_domain_col,
            trading_period_start_col, trading_period_end_col)
        assert (ret_val[da_error_flag_col] == 'E00').all()

    def test_multi_midpoint_param_fast_fail(self):
        df_loc = f"{fxt}/da_date_adjustment_method_input.csv"
        test_dataframe = load_csv(df_loc)
        test_dataframe = test_dataframe.loc[test_dataframe[average_weekly_col] == 'N']
        test_dataframe = test_dataframe.loc[test_dataframe[equal_weighted_col] == 'N']
        with self.assertRaises(ValueError):
            date_adjustment(
                test_dataframe, trading_weights, target_columns,
                contributor_returned_start_date_col, contributor_returned_end_date_col,
                expected_start_date_col, expected_end_date_col, domain_col,
                short_period_parameter_col, long_period_parameter_col, equal_weighted_col,
                set_to_mid_point_col, use_calendar_days_col, average_weekly_col,
                da_error_flag_col, trading_date_col, trading_weights_col, trading_domain_col,
                trading_period_start_col, trading_period_end_col)

    def test_multi_equal_weight_param_fast_fail(self):
        df_loc = f"{fxt}/da_date_adjustment_method_input.csv"
        test_dataframe = load_csv(df_loc)
        test_dataframe = test_dataframe.loc[test_dataframe[average_weekly_col] == 'N']
        test_dataframe = test_dataframe.loc[test_dataframe[set_to_mid_point_col] == 'Y']
        with self.assertRaises(ValueError):
            date_adjustment(
                test_dataframe, trading_weights, target_columns,
                contributor_returned_start_date_col, contributor_returned_end_date_col,
                expected_start_date_col, expected_end_date_col, domain_col,
                short_period_parameter_col, long_period_parameter_col, equal_weighted_col,
                set_to_mid_point_col, use_calendar_days_col, average_weekly_col,
                da_error_flag_col, trading_date_col, trading_weights_col, trading_domain_col,
                trading_period_start_col, trading_period_end_col)

    def test_all_error_codes_generated_as_expected(self):
        df_loc = f"{fxt}/da_date_adjustment_method_input.csv"
        test_dataframe = load_csv(df_loc)
        ret_val = date_adjustment(
            test_dataframe, trading_weights, target_columns,
            contributor_returned_start_date_col, contributor_returned_end_date_col,
            expected_start_date_col, expected_end_date_col, domain_col,
            short_period_parameter_col, long_period_parameter_col, equal_weighted_col,
            set_to_mid_point_col, use_calendar_days_col, average_weekly_col,
            da_error_flag_col, trading_date_col, trading_weights_col, trading_domain_col,
            trading_period_start_col, trading_period_end_col, ignore_multi_aw_param_error)
        assert error_codes_list
        error_frame = ret_val.loc[ret_val[da_error_flag_col].isin(error_codes_list)]
        error_list = error_frame[da_error_flag_col].to_list()
        test_list = error_codes_list.copy()
        test_list.remove('E00')
        for code in test_list:
            err_msg = 'Error code ' + str(code) + ' not tested by data.'
            assert code in error_list, err_msg


# ---------------------------------------------------------------------------------------
# TESTS: GENERATE AVERAGE WEEKLY QUESTION LIST SUB-FUNCTION
# ---------------------------------------------------------------------------------------

class TestGenerateAverageWeeklyQuestions(TestCase):

    # --- Test fails with type error if no input. ---

    # noinspection PyArgumentList
    def test_failure_on_no_input(self):
        with self.assertRaises(TypeError):
            generate_average_weekly_questions()

    # --- Test type validation on the input strings ---

    # noinspection PyMethodMayBeStatic
    def test_validate_average_weekly_param(self):
        empty_df = pd.DataFrame.empty
        for test_param in ['X', 20, {"Q20": 20}, ['Not a string'], empty_df]:
            ret_val = generate_average_weekly_questions(test_param, target_columns)
            assert ret_val == 'ERROR: invalid average_weekly parameter contents.'

    # --- Test type validation on the target column lists(s) ---

    # noinspection PyMethodMayBeStatic
    def test_validate_target_columns_param(self):
        with self.assertRaises(TypeError):
            # noinspection PyTypeChecker
            generate_average_weekly_questions('A', 'Not a list')

    # --- Test if output is a List ---

    # noinspection PyMethodMayBeStatic
    def test_output_is_list(self):
        ret_val = generate_average_weekly_questions('A', target_columns)
        assert isinstance(ret_val, list)

    # --- Test if output contents is as expected ---

    # noinspection PyMethodMayBeStatic
    def test_output_for_A(self):
        ret_val = generate_average_weekly_questions('A', target_columns)
        assert ret_val == target_columns

    # noinspection PyMethodMayBeStatic
    def test_output_for_N(self):
        ret_val = generate_average_weekly_questions('N', target_columns)
        assert ret_val == []

    # noinspection PyMethodMayBeStatic
    def test_output_for_question_strings(self):
        check_list = []
        df_loc = f"{fxt}/"
        df_loc += "da_validate_average_weekly_param_subfunction.csv"
        aw_param_test_df = load_csv(df_loc)
        for index, row in aw_param_test_df.iterrows():
            test_string = row['test_input']
            ret_val = generate_average_weekly_questions(test_string, target_columns)
            if row['expected_output'] == "ERROR":
                check_list.append('A')
                assert ret_val[:5] == "ERROR"
            if row['expected_output'] != "ERROR":
                expected_output = _convert_question_string_to_list(row['expected_output'])
                check_list.append('B')
                assert ret_val == expected_output
        if 'A' not in check_list:
            msg = 'No test was performed for the "ERROR" branch. Check test data.'
            raise AssertionError(msg)
        if 'B' not in check_list:
            msg = 'No test was performed for the expected output branch. Check test data.'
            raise AssertionError(msg)


# ---------------------------------------------------------------------------------------
# TESTS: MISSING VALUE SUB-FUNCTION
# ---------------------------------------------------------------------------------------

class MissingValueSubfunction(TestCase):

    # --- Test fails with type error if no input ---

    # noinspection PyArgumentList
    def test_failure_on_no_input(self):
        with self.assertRaises(TypeError):
            missing_value_subfunction()

    # --- Test type validation on the input dataframe(s) ---
    def test_validate_input_dataframe_type(self):
        with self.assertRaises(TypeError):
            # noinspection PyTypeChecker
            missing_value_subfunction(
                ["Not_A_Dataframe"], target_columns, da_error_flag_col)

    # --- Test type validation on the target column list(s) ---

    def test_validate_target_columns_type(self):
        with self.assertRaises(TypeError):
            df_loc = f"{fxt}/da_missing_value_subfunction_input.csv"
            test_dataframe = load_csv(df_loc)
            # noinspection PyTypeChecker
            missing_value_subfunction(test_dataframe, 'Not a list', da_error_flag_col)

    # --- Test if cols missing from input dataframe(s) ---

    def test_validate_required_cols_in_input_dataframe(self):
        df_loc = f"{fxt}/da_missing_value_subfunction_input.csv"
        test_dataframe = load_csv(df_loc)
        bad_dataframe = test_dataframe.drop(columns=target_columns[1])
        with self.assertRaises(KeyError):
            missing_value_subfunction(bad_dataframe, target_columns, da_error_flag_col)

    # --- Test if output is a dataframe ---

    # noinspection PyMethodMayBeStatic
    def test_output_is_dataframe(self):
        df_loc = f"{fxt}/da_missing_value_subfunction_input.csv"
        test_dataframe = load_csv(df_loc)
        ret_val = missing_value_subfunction(
            test_dataframe, target_columns, da_error_flag_col)
        assert isinstance(ret_val, type(pd.DataFrame()))

    # --- Test if output contents is as expected, both new columns and data content ---

    # noinspection PyMethodMayBeStatic
    def test_error_flag_column_exist(self):
        df_loc = f"{fxt}/da_missing_value_subfunction_input.csv"
        test_dataframe = load_csv(df_loc)
        ret_val = missing_value_subfunction(
            test_dataframe, target_columns, da_error_flag_col)
        assert (da_error_flag_col in ret_val.columns)

    # noinspection PyMethodMayBeStatic
    def test_nothing_filtered(self):
        df_loc = f"{fxt}/da_missing_value_subfunction_input.csv"
        test_dataframe = load_csv(df_loc)
        ret_val = missing_value_subfunction(
            test_dataframe, target_columns, da_error_flag_col)
        assert (len(ret_val) == len(test_dataframe)), \
            "should have the same amount of rows that went in"

    # --- Test any other error based outputs ---

    # noinspection PyMethodMayBeStatic
    def test_error_flag_set_correctly_where_appropriate(self):
        check_list = []
        df_loc = f"{fxt}/da_missing_value_subfunction_input.csv"
        test_dataframe = load_csv(df_loc)
        ret_val = missing_value_subfunction(
            test_dataframe, target_columns, da_error_flag_col)
        for _idx, row in ret_val.iterrows():
            flagged = 0
            for col_name in target_columns:
                if np.isnan(float(row[col_name])):
                    flagged = 1
            if flagged:
                check_list.append('A')
                assert (row[da_error_flag_col] == 'E01'), \
                    'error flag should be set to E01'
            else:
                check_list.append('B')
                assert (np.isnan(row[da_error_flag_col])), \
                    'error flag should be blank (nan).'
        if 'A' not in check_list:
            msg = 'No test was performed for the E flag branch. Check test data.'
            raise AssertionError(msg)
        if 'B' not in check_list:
            msg = 'No test was performed for the E flag branch. Check test data.'
            raise AssertionError(msg)


# ---------------------------------------------------------------------------------------
# TESTS: PRIMARY WRANGLER SUB-FUNCTION
# ---------------------------------------------------------------------------------------

class TestPrimaryWranglerSubfunction(TestCase):

    # --- Test fails with type error if no input ---

    # noinspection PyArgumentList
    def test_failure_on_no_input(self):
        with self.assertRaises(TypeError):
            primary_wrangler_subfunction()

    # --- Test type validation on the input dataframe(s) ---

    def test_validate_input_dataframe_type(self):
        with self.assertRaises(TypeError):
            # noinspection PyTypeChecker
            primary_wrangler_subfunction(
                ["Not_A_Dataframe"], trading_weights, target_columns,
                contributor_returned_start_date_col, contributor_returned_end_date_col,
                expected_start_date_col, expected_end_date_col, domain_col,
                equal_weighted_col, da_error_flag_col, trading_domain_col,
                trading_date_col, trading_weights_col)

    def test_validate_trading_weights_type(self):
        df_loc = f"{fxt}/da_primary_wrangler_subfunction_input.csv"
        test_dataframe = load_csv(df_loc)
        with self.assertRaises(TypeError):
            # noinspection PyTypeChecker
            primary_wrangler_subfunction(
                test_dataframe, ["Not_A_Dataframe"], target_columns,
                contributor_returned_start_date_col, contributor_returned_end_date_col,
                expected_start_date_col, expected_end_date_col, domain_col,
                equal_weighted_col, da_error_flag_col, trading_domain_col,
                trading_date_col, trading_weights_col)

    # --- Test type validation on the target column lists(s) ---

    def test_dataframe(self):
        df_loc = f"{fxt}/da_primary_wrangler_subfunction_input.csv"
        test_dataframe = load_csv(df_loc)
        with self.assertRaises(TypeError):
            # noinspection PyTypeChecker
            primary_wrangler_subfunction(
                test_dataframe, trading_weights, "Not a list",
                contributor_returned_start_date_col, contributor_returned_end_date_col,
                expected_start_date_col, expected_end_date_col, domain_col,
                equal_weighted_col, da_error_flag_col, trading_domain_col,
                trading_date_col, trading_weights_col)

    # --- Test if cols missing from input dataframe(s) ---

    def test_validate_required_cols_in_input_dataframe(self):
        df_loc = f"{fxt}/da_primary_wrangler_subfunction_input.csv"
        test_dataframe = load_csv(df_loc)
        bad_dataframe = test_dataframe.drop(columns=target_columns[1])
        with self.assertRaises(KeyError):
            primary_wrangler_subfunction(
                bad_dataframe, trading_weights, target_columns,
                contributor_returned_start_date_col, contributor_returned_end_date_col,
                expected_start_date_col, expected_end_date_col, domain_col,
                equal_weighted_col, da_error_flag_col, trading_domain_col,
                trading_date_col, trading_weights_col)

    def test_validate_required_cols_in_trading_weight(self):
        df_loc = f"{fxt}/da_primary_wrangler_subfunction_input.csv"
        tw_loc = f"{fxt}/da_trading_weights_data.csv"
        test_dataframe = load_csv(df_loc)
        test_weights = load_csv(tw_loc)
        bad_weights = test_weights.drop(trading_domain_col, axis=1)
        with self.assertRaises(KeyError):
            primary_wrangler_subfunction(
                test_dataframe, bad_weights, target_columns,
                contributor_returned_start_date_col, contributor_returned_end_date_col,
                expected_start_date_col, expected_end_date_col, domain_col,
                equal_weighted_col, da_error_flag_col, trading_domain_col,
                trading_date_col, trading_weights_col)

    # --- Test if output is a dataframe ---

    def test_output_is_dataframe(self):
        df_loc = f"{fxt}/da_primary_wrangler_subfunction_input.csv"
        test_dataframe = load_csv(df_loc)
        ret_val = primary_wrangler_subfunction(
            test_dataframe, trading_weights, target_columns,
            contributor_returned_start_date_col, contributor_returned_end_date_col,
            expected_start_date_col, expected_end_date_col, domain_col,
            equal_weighted_col, da_error_flag_col, trading_domain_col,
            trading_date_col, trading_weights_col)
        assert isinstance(ret_val, type(pd.DataFrame())), "should be a dataframe"

    # -- Test if output is as expected, both new columns being created and data content --

    # Rule 3.1 , 3.2

    def test_no_blank_contributor_starts(self):
        df_loc = f"{fxt}/da_primary_wrangler_subfunction_input.csv"
        test_dataframe = load_csv(df_loc)
        ret_val = primary_wrangler_subfunction(
            test_dataframe, trading_weights, target_columns,
            contributor_returned_start_date_col, contributor_returned_end_date_col,
            expected_start_date_col, expected_end_date_col, domain_col,
            equal_weighted_col, da_error_flag_col, trading_domain_col,
            trading_date_col, trading_weights_col)
        nan_rows = ret_val[ret_val[contributor_returned_start_date_col].isnull()]
        assert (nan_rows.shape[0] == 0)

    def test_no_bank_contributor_ends(self):
        df_loc = f"{fxt}/da_primary_wrangler_subfunction_input.csv"
        test_dataframe = load_csv(df_loc)
        ret_val = primary_wrangler_subfunction(
            test_dataframe, trading_weights, target_columns,
            contributor_returned_start_date_col, contributor_returned_end_date_col,
            expected_start_date_col, expected_end_date_col, domain_col,
            equal_weighted_col, da_error_flag_col, trading_domain_col,
            trading_date_col, trading_weights_col)
        nan_rows = ret_val[ret_val['contributors_returned_period_end_date'].isnull()]
        assert (nan_rows.shape[0] == 0)

    # Rule 3.3, 3.4, 3.5, 3.6, 3.7

    def test_weights_m_column_created(self):
        df_loc = f"{fxt}/da_primary_wrangler_subfunction_input.csv"
        test_dataframe = load_csv(df_loc)
        ret_val = primary_wrangler_subfunction(
            test_dataframe, trading_weights, target_columns,
            contributor_returned_start_date_col, contributor_returned_end_date_col,
            expected_start_date_col, expected_end_date_col, domain_col,
            equal_weighted_col, da_error_flag_col, trading_domain_col,
            trading_date_col, trading_weights_col)
        assert wcr_col in ret_val.columns, \
            "sum of trading day weights column should be created"

    def test_num_days_column_created(self):
        df_loc = f"{fxt}/da_primary_wrangler_subfunction_input.csv"
        test_dataframe = load_csv(df_loc)
        ret_val = primary_wrangler_subfunction(
            test_dataframe, trading_weights, target_columns,
            contributor_returned_start_date_col, contributor_returned_end_date_col,
            expected_start_date_col, expected_end_date_col, domain_col,
            equal_weighted_col, da_error_flag_col, trading_domain_col,
            trading_date_col, trading_weights_col)
        assert (dcr_col in ret_val.columns)

    def test_num_days_calculation_correct(self):
        actually_tested = 0
        df_loc = f"{fxt}/da_primary_wrangler_subfunction_input.csv"
        test_dataframe = load_csv(df_loc)
        ret_val = primary_wrangler_subfunction(
            test_dataframe, trading_weights, target_columns,
            contributor_returned_start_date_col, contributor_returned_end_date_col,
            expected_start_date_col, expected_end_date_col, domain_col,
            equal_weighted_col, da_error_flag_col, trading_domain_col,
            trading_date_col, trading_weights_col)
        for _idx, row in ret_val.iterrows():
            if row[da_error_flag_col] not in error_codes_list:
                actually_tested = 1
                assert (row[dcr_col]
                        == (row[contributor_returned_end_date_col]
                            - row[contributor_returned_start_date_col]).days + 1), \
                    "Days in contributor period should be start to end dates inclusive."
        if not actually_tested:
            raise AssertionError(filter_err)

    def test_equal_weighted_y_correct(self):
        actually_tested = 0
        df_loc = f"{fxt}/da_primary_wrangler_subfunction_input.csv"
        test_dataframe = load_csv(df_loc)
        ret_val = primary_wrangler_subfunction(
            test_dataframe, trading_weights, target_columns,
            contributor_returned_start_date_col, contributor_returned_end_date_col,
            expected_start_date_col, expected_end_date_col, domain_col,
            equal_weighted_col, da_error_flag_col, trading_domain_col,
            trading_date_col, trading_weights_col)
        for _idx, row in ret_val.iterrows():
            if (row[equal_weighted_col] == 'Y' and
                    row[da_error_flag_col] not in error_codes_list):
                actually_tested = 1
                assert (row[wcr_col] == row[dcr_col]), \
                    "The m weight should be summed correctly"
        if not actually_tested:
            raise AssertionError(filter_err)

    def test_weights_m_set_correctly(self):
        actually_tested = 0
        df_loc = f"{fxt}/da_primary_wrangler_subfunction_input.csv"
        test_dataframe = load_csv(df_loc)
        ret_val = primary_wrangler_subfunction(
            test_dataframe, trading_weights, target_columns,
            contributor_returned_start_date_col, contributor_returned_end_date_col,
            expected_start_date_col, expected_end_date_col, domain_col,
            equal_weighted_col, da_error_flag_col, trading_domain_col,
            trading_date_col, trading_weights_col)
        for _idx, row in ret_val.iterrows():
            if (row[equal_weighted_col] != 'Y' and
                    row[da_error_flag_col] not in error_codes_list):
                actually_tested = 1
                mask = (trading_weights[trading_date_col] >=
                        row[contributor_returned_start_date_col]) & \
                       (trading_weights[trading_date_col] <=
                        row[contributor_returned_end_date_col]) & \
                       (trading_weights[trading_domain_col] == str((row[domain_col])))
                filtered_weights = trading_weights.loc[mask]
                sum_ret = wcr_col
                assert (row[sum_ret] == filtered_weights[trading_weights_col].sum()), \
                    "The m weight should be summed correctly"
        if not actually_tested:
            raise AssertionError(filter_err)

    # --- Test any other error based outputs ---

    # E2: Contributor returned end date is earlier than contributor returned start date.

    def test_outputs_zeroed_when_E02_generated(self):
        actually_tested = 0
        df_loc = f"{fxt}/da_primary_wrangler_subfunction_input.csv"
        test_dataframe = load_csv(df_loc)
        ret_val = primary_wrangler_subfunction(
            test_dataframe, trading_weights, target_columns,
            contributor_returned_start_date_col, contributor_returned_end_date_col,
            expected_start_date_col, expected_end_date_col, domain_col,
            equal_weighted_col, da_error_flag_col, trading_domain_col,
            trading_date_col, trading_weights_col)
        for _idx, row in ret_val.iterrows():
            if row[da_error_flag_col] == 'E02':
                actually_tested = 1
                assert (row[dcr_col] == 0), \
                    "The number of days in the contributor period " + \
                    "should be zeroed when CRPE < CRPS"
                assert (row[wcr_col] == 0), \
                    "The m weight should be zeroed when CRPE < CRPS"
        if not actually_tested:
            raise AssertionError(filter_err)

    # E3: A required record is missing from the trading weights table.

    def test_m_weight_zero_when_E03_generated(self):
        actually_tested = 0
        df_loc = f"{fxt}/da_primary_wrangler_subfunction_input.csv"
        test_dataframe = load_csv(df_loc)
        ret_val = primary_wrangler_subfunction(
            test_dataframe, trading_weights, target_columns,
            contributor_returned_start_date_col, contributor_returned_end_date_col,
            expected_start_date_col, expected_end_date_col, domain_col,
            equal_weighted_col, da_error_flag_col, trading_domain_col,
            trading_date_col, trading_weights_col)
        for _idx, row in ret_val.iterrows():
            if row[da_error_flag_col] == 'E03':
                actually_tested = 1
                assert (row[wcr_col] == 0), \
                    "The m weight should be zeroed if any contributing " + \
                    "weight records are missing"
        if not actually_tested:
            raise AssertionError(filter_err)

    # E4: A required trading weight is null or blank.

    def test_m_weight_zero_when_E04_generated(self):
        actually_tested = 0
        df_loc = f"{fxt}/da_primary_wrangler_subfunction_input.csv"
        test_dataframe = load_csv(df_loc)
        ret_val = primary_wrangler_subfunction(
            test_dataframe, trading_weights, target_columns,
            contributor_returned_start_date_col, contributor_returned_end_date_col,
            expected_start_date_col, expected_end_date_col, domain_col,
            equal_weighted_col, da_error_flag_col, trading_domain_col,
            trading_date_col, trading_weights_col)
        for _idx, row in ret_val.iterrows():
            if row[da_error_flag_col] == 'E04':
                actually_tested = 1
                assert (row[wcr_col] == 0), \
                    "The m weight should be zeroed if any contributing " + \
                    "weight values are missing"
        if not actually_tested:
            raise AssertionError(filter_err)

    # E5: A required trading weight has a negative value.

    def test_m_weight_zero_when_E05_generated(self):
        actually_tested = 0
        df_loc = f"{fxt}/da_primary_wrangler_subfunction_input.csv"
        test_dataframe = load_csv(df_loc)
        ret_val = primary_wrangler_subfunction(
            test_dataframe, trading_weights, target_columns,
            contributor_returned_start_date_col, contributor_returned_end_date_col,
            expected_start_date_col, expected_end_date_col, domain_col,
            equal_weighted_col, da_error_flag_col, trading_domain_col,
            trading_date_col, trading_weights_col)
        for _idx, row in ret_val.iterrows():
            if row[da_error_flag_col] == 'E05':
                actually_tested = 1
                assert (row[wcr_col] == 0), \
                    "The m weight should be zeroed if any contributing " + \
                    "weight values are negative"
        if not actually_tested:
            raise AssertionError(filter_err)

    # E14: Null or invalid expected start date.

    def test_E14_when_expected_start_date_is_invalid(self):
        actually_tested = 0
        df_loc = f"{fxt}/da_primary_wrangler_subfunction_input.csv"
        test_dataframe = load_csv(df_loc)
        ret_val = primary_wrangler_subfunction(
            test_dataframe, trading_weights, target_columns,
            contributor_returned_start_date_col, contributor_returned_end_date_col,
            expected_start_date_col, expected_end_date_col, domain_col,
            equal_weighted_col, da_error_flag_col, trading_domain_col,
            trading_date_col, trading_weights_col)
        for _idx, row in ret_val.iterrows():
            if pd.isnull(row[expected_start_date_col]):
                actually_tested = 1
                assert (row[da_error_flag_col] == 'E14'), \
                    "Error E14 should be recorded when the expected start date " + \
                    f"is invalid or missing. Ref:{row['enterprise_reference_number']} " \
                    f"EPS:{row[expected_start_date_col]} Flag:{row[da_error_flag_col]}"
        if not actually_tested:
            raise AssertionError(filter_err)

    # E15: Null or invalid expected end date.

    def test_E15_when_expected_end_date_is_invalid(self):
        actually_tested = 0
        df_loc = f"{fxt}/da_primary_wrangler_subfunction_input.csv"
        test_dataframe = load_csv(df_loc)
        ret_val = primary_wrangler_subfunction(
            test_dataframe, trading_weights, target_columns,
            contributor_returned_start_date_col, contributor_returned_end_date_col,
            expected_start_date_col, expected_end_date_col, domain_col,
            equal_weighted_col, da_error_flag_col, trading_domain_col,
            trading_date_col, trading_weights_col)
        for _idx, row in ret_val.iterrows():
            if pd.isnull(row[expected_end_date_col]):
                actually_tested = 1
                assert (row[da_error_flag_col] == 'E15'), \
                    "Error E15 should be recorded when the expected start date " + \
                    f"is invalid or missing. Ref:{row['enterprise_reference_number']}"
        if not actually_tested:
            raise AssertionError(filter_err)


# ---------------------------------------------------------------------------------------
# SECTION: MIDPOINT SUB-FUNCTION
# ---------------------------------------------------------------------------------------

class TestMidpointSubfunction(TestCase):

    # --- Test fails with type error if no input ---

    def test_input_provided(self):
        self.assertRaises(TypeError)

    # --- Test type validation on the input dataframe(s) ---

    def test_input_is_a_dataframe(self):
        with self.assertRaises(TypeError):
            # noinspection PyTypeChecker
            midpoint_subfunction(
                ["Not_A_Dataframe"], trading_weights, target_columns, domain_col,
                expected_start_date_col, expected_end_date_col,
                contributor_returned_start_date_col,
                contributor_returned_end_date_col, set_to_mid_point_col,
                equal_weighted_col, use_calendar_days_col, trading_date_col,
                trading_period_start_col, trading_period_end_col,
                trading_weights_col, trading_domain_col, da_error_flag_col)

    # --- Test if cols missing from input dataframe(s) ---

    def test_required_cols_missing_from_input(self):
        df_loc = f"{fxt}/da_midpoint_subfunction_input.csv"
        test_dataframe = load_csv(df_loc)
        bad_dataframe = test_dataframe.drop([expected_start_date_col], axis=1)
        with self.assertRaises(KeyError):
            midpoint_subfunction(
                bad_dataframe, trading_weights, target_columns, domain_col,
                expected_start_date_col, expected_end_date_col,
                contributor_returned_start_date_col,
                contributor_returned_end_date_col, set_to_mid_point_col,
                equal_weighted_col, use_calendar_days_col, trading_date_col,
                trading_period_start_col, trading_period_end_col,
                trading_weights_col, trading_domain_col, da_error_flag_col)

    # --- Test if output is a dataframe ---

    def test_output_is_dataframe(self):
        df_loc = f"{fxt}/da_midpoint_subfunction_input.csv"
        test_dataframe = load_csv(df_loc)
        ret_val = midpoint_subfunction(
            test_dataframe, trading_weights, target_columns, domain_col,
            expected_start_date_col, expected_end_date_col,
            contributor_returned_start_date_col,
            contributor_returned_end_date_col, set_to_mid_point_col,
            equal_weighted_col, use_calendar_days_col, trading_date_col,
            trading_period_start_col, trading_period_end_col,
            trading_weights_col, trading_domain_col, da_error_flag_col)
        assert isinstance(ret_val, type(pd.DataFrame())), "Output should be a dataframe"

    # --- Test if output contents is as expected, both new columns and data content ---

    def test_required_output_cols_present_in_output(self):
        df_loc = f"{fxt}/da_midpoint_subfunction_input.csv"
        test_dataframe = load_csv(df_loc)
        ret_val = midpoint_subfunction(
            test_dataframe, trading_weights, target_columns, domain_col,
            expected_start_date_col, expected_end_date_col,
            contributor_returned_start_date_col,
            contributor_returned_end_date_col, set_to_mid_point_col,
            equal_weighted_col, use_calendar_days_col, trading_date_col,
            trading_period_start_col, trading_period_end_col,
            trading_weights_col, trading_domain_col, da_error_flag_col)
        cols = list(ret_val.columns)
        assert 'actual_period_start_date' in cols
        assert 'actual_period_end_date' in cols

    # Output via bypass to flowchart route 9
    def test_output_mid_point_equal_n_route(self):
        actually_tested = 0
        df_loc = f"{fxt}/da_midpoint_subfunction_input.csv"
        test_dataframe = load_csv(df_loc)
        ret_val = midpoint_subfunction(
            test_dataframe, trading_weights, target_columns, domain_col,
            expected_start_date_col, expected_end_date_col,
            contributor_returned_start_date_col,
            contributor_returned_end_date_col, set_to_mid_point_col,
            equal_weighted_col, use_calendar_days_col, trading_date_col,
            trading_period_start_col, trading_period_end_col,
            trading_weights_col, trading_domain_col, da_error_flag_col)
        for _idx, row in ret_val.iterrows():
            if row[set_to_mid_point_col] == 'N':
                actually_tested = 1
                assert row['actual_period_start_date'] == row[expected_start_date_col]
                assert row['actual_period_end_date'] == row[expected_end_date_col]
        if not actually_tested:
            raise AssertionError(filter_err)

    # Output via flowchart route 9, part 1.
    def test_equal_weight_overrides_trimming(self):
        actually_tested = 0
        df_loc = f"{fxt}/da_midpoint_subfunction_input.csv"
        test_dataframe = load_csv(df_loc)
        ret_val = midpoint_subfunction(
            test_dataframe, trading_weights, target_columns, domain_col,
            expected_start_date_col, expected_end_date_col,
            contributor_returned_start_date_col,
            contributor_returned_end_date_col, set_to_mid_point_col,
            equal_weighted_col, use_calendar_days_col, trading_date_col,
            trading_period_start_col, trading_period_end_col,
            trading_weights_col, trading_domain_col, da_error_flag_col)
        for idx, row in ret_val.iterrows():
            if row[set_to_mid_point_col] == 'YT':
                actually_tested = 1
                assert row[equal_weighted_col] == 'N', \
                    "Equal weighting needs to prevent trimming being used."
        if not actually_tested:
            raise AssertionError(filter_err)

    # Output via flowchart route 9, part 2.
    def test_output_mid_point_actual_equals_expected(self):
        actually_tested = 0
        df_loc = f"{fxt}/da_midpoint_subfunction_input.csv"
        test_dataframe = load_csv(df_loc)
        ret_val = midpoint_subfunction(
            test_dataframe, trading_weights, target_columns, domain_col,
            expected_start_date_col, expected_end_date_col,
            contributor_returned_start_date_col,
            contributor_returned_end_date_col, set_to_mid_point_col,
            equal_weighted_col, use_calendar_days_col, trading_date_col,
            trading_period_start_col, trading_period_end_col,
            trading_weights_col, trading_domain_col, da_error_flag_col)
        for _idx, row in ret_val.iterrows():
            if (row[set_to_mid_point_col] == 'Y' and
                    row[equal_weighted_col] == 'Y' and
                    (row[expected_start_date_col] <=
                     row['midpoint_date'] <=
                     row[expected_end_date_col])):
                actually_tested = 1
                assert row['date_change_in_return_period_flag'] != 'C'
                assert row['actual_period_start_date'] == row[expected_start_date_col]
                assert row['actual_period_end_date'] == row[expected_end_date_col]

        if not actually_tested:
            raise AssertionError(filter_err)

    # Output via flowchart route 10b
    def test_output_mid_point_changed_dates_calendar_days(self):
        actually_tested = 0
        df_loc = f"{fxt}/da_midpoint_subfunction_input.csv"
        test_dataframe = load_csv(df_loc)
        ret_val = midpoint_subfunction(
            test_dataframe, trading_weights, target_columns, domain_col,
            expected_start_date_col, expected_end_date_col,
            contributor_returned_start_date_col,
            contributor_returned_end_date_col, set_to_mid_point_col,
            equal_weighted_col, use_calendar_days_col, trading_date_col,
            trading_period_start_col, trading_period_end_col,
            trading_weights_col, trading_domain_col, da_error_flag_col)
        for _idx, row in ret_val.iterrows():
            if (row[use_calendar_days_col] == 'Y' and
                    not (row[expected_start_date_col] <=
                         row['midpoint_date'] <=
                         row[expected_end_date_col])):
                actually_tested = 1
                first_day = 1
                last_day = cal.monthrange(
                    row['midpoint_date'].year,
                    row['midpoint_date'].month
                )[1]
                calculated_start_date = pd.Timestamp(
                    year=row['midpoint_date'].year,
                    month=row['midpoint_date'].month,
                    day=first_day
                )
                calculated_end_date = pd.Timestamp(
                    year=row['midpoint_date'].year,
                    month=row['midpoint_date'].month,
                    day=last_day
                )
                assert row['date_change_in_return_period_flag'] == 'C'
                assert row['actual_period_start_date'] == calculated_start_date
                assert row['actual_period_end_date'] == calculated_end_date
        if not actually_tested:
            raise AssertionError(filter_err)

    # Output via flowchart route 10c
    def test_output_mid_point_changed_dates_trading_period(self):
        actually_tested = 0
        df_loc = f"{fxt}/da_midpoint_subfunction_input.csv"
        test_dataframe = load_csv(df_loc)
        ret_val = midpoint_subfunction(
            test_dataframe, trading_weights, target_columns, domain_col,
            expected_start_date_col, expected_end_date_col,
            contributor_returned_start_date_col,
            contributor_returned_end_date_col, set_to_mid_point_col,
            equal_weighted_col, use_calendar_days_col, trading_date_col,
            trading_period_start_col, trading_period_end_col,
            trading_weights_col, trading_domain_col, da_error_flag_col)

        for _idx, row in ret_val.iterrows():
            if (row[set_to_mid_point_col] != 'N' and
                    row[use_calendar_days_col] == 'N' and
                    row[da_error_flag_col] not in error_codes_list and
                    not (row[expected_start_date_col] <=
                         row['midpoint_date'] <=
                         row[expected_end_date_col])):
                actually_tested = 1

                midpoint_data = trading_weights[
                    (trading_weights[trading_date_col] == row['midpoint_date']) &
                    (trading_weights[trading_domain_col] == row[domain_col])
                    ]

                calculated_start_date = \
                    midpoint_data[trading_period_start_col].values[0]
                calculated_end_date = \
                    midpoint_data[trading_period_end_col].values[0]

                assert row['date_change_in_return_period_flag'] == 'C'
                assert row['actual_period_start_date'] == calculated_start_date
                assert row['actual_period_end_date'] == calculated_end_date
        if not actually_tested:
            raise AssertionError(filter_err)

    # --- Test any other error based outputs ---

    def test_E12_on_empty_non_zero_after_crps_dataframe(self):
        actually_tested = 0
        df_loc = f"{fxt}/da_midpoint_subfunction_input.csv"
        test_dataframe = load_csv(df_loc)
        ret_val = midpoint_subfunction(
            test_dataframe, trading_weights, target_columns, domain_col,
            expected_start_date_col, expected_end_date_col,
            contributor_returned_start_date_col,
            contributor_returned_end_date_col, set_to_mid_point_col,
            equal_weighted_col, use_calendar_days_col, trading_date_col,
            trading_period_start_col, trading_period_end_col,
            trading_weights_col, trading_domain_col, da_error_flag_col)
        for _idx, row in ret_val.iterrows():
            if (row[set_to_mid_point_col] != 'N' and
                    row[equal_weighted_col] == 'N'):

                non_zero_after_crps = trading_weights[
                    (trading_weights[trading_weights_col] > 0) &
                    (trading_weights[trading_date_col] >= row[
                        contributor_returned_start_date_col]) &
                    (trading_weights[trading_domain_col] == row[domain_col])
                    ].sort_values(by=trading_date_col, ascending=True)

                if len(non_zero_after_crps) == 0:
                    actually_tested = 1
                    assert row[da_error_flag_col] == 'E12'
        if not actually_tested:
            raise AssertionError(filter_err)

    def test_E12_on_empty_non_zero_before_crpe_dataframe(self):
        actually_tested = 0
        df_loc = f"{fxt}/da_midpoint_subfunction_input.csv"
        test_dataframe = load_csv(df_loc)
        ret_val = midpoint_subfunction(
            test_dataframe, trading_weights, target_columns, domain_col,
            expected_start_date_col, expected_end_date_col,
            contributor_returned_start_date_col,
            contributor_returned_end_date_col, set_to_mid_point_col,
            equal_weighted_col, use_calendar_days_col, trading_date_col,
            trading_period_start_col, trading_period_end_col,
            trading_weights_col, trading_domain_col, da_error_flag_col)
        for _idx, row in ret_val.iterrows():
            if (row[set_to_mid_point_col] != 'N' and
                    row[equal_weighted_col] == 'N'):

                non_zero_before_crpe = trading_weights[
                    (trading_weights[trading_weights_col] > 0) &
                    (trading_weights[trading_date_col] <= row[
                        contributor_returned_end_date_col]) &
                    (trading_weights[trading_domain_col] == row[domain_col])
                    ].sort_values(by=trading_date_col, ascending=True)

                if len(non_zero_before_crpe) == 0:
                    actually_tested = 1
                    assert row[da_error_flag_col] == 'E12'
        if not actually_tested:
            raise AssertionError(filter_err)

    def test_E13(self):
        actually_tested = 0
        df_loc = f"{fxt}/da_midpoint_subfunction_input.csv"
        test_dataframe = load_csv(df_loc)
        ret_val = midpoint_subfunction(
            test_dataframe, trading_weights, target_columns, domain_col,
            expected_start_date_col, expected_end_date_col,
            contributor_returned_start_date_col,
            contributor_returned_end_date_col, set_to_mid_point_col,
            equal_weighted_col, use_calendar_days_col, trading_date_col,
            trading_period_start_col, trading_period_end_col,
            trading_weights_col, trading_domain_col, da_error_flag_col)
        for _idx, row in ret_val.iterrows():
            if (row['date_change_in_return_period_flag'] == 'C' and
                    row[use_calendar_days_col] == 'N'):

                midpoint_data = trading_weights[
                    (trading_weights[trading_date_col] == row['midpoint_date']) &
                    (trading_weights[trading_domain_col] == row[domain_col])
                    ]

                if len(midpoint_data) != 1:
                    actually_tested = 1
                    assert row[da_error_flag_col] == 'E13'
        if not actually_tested:
            raise AssertionError(filter_err)

    # TODO: Assert that E12 and E13 are being created when expected period
    #       start and end dates are missing.


# ---------------------------------------------------------------------------------------
# SECTION: SECONDARY WRANGLER SUB-FUNCTION
# ---------------------------------------------------------------------------------------

class TestSecondaryWranglerSubfunction(TestCase):

    def test_input_provided(self):
        self.assertRaises(TypeError)

    # --- Test type validation on the input dataframe(s) ---

    def test_input_not_dataframe(self):
        with self.assertRaises(TypeError):
            # noinspection PyTypeChecker
            secondary_wrangler_subfunction(
                ["Not_A_Dataframe"], target_columns, trading_weights,
                contributor_returned_start_date_col, contributor_returned_end_date_col,
                expected_start_date_col, expected_end_date_col, domain_col,
                equal_weighted_col, set_to_mid_point_col, short_period_parameter_col,
                long_period_parameter_col, da_error_flag_col, trading_date_col,
                trading_domain_col, trading_weights_col)

    def test_trading_weights_not_dataframe(self):
        with self.assertRaises(TypeError):
            df_loc = f"{fxt}/"
            df_loc += "da_secondary_wrangler_subfunction_input.csv"
            test_dataframe = load_csv(df_loc)
            # noinspection PyTypeChecker
            secondary_wrangler_subfunction(
                test_dataframe, target_columns, ["Not_A_Dataframe"],
                contributor_returned_start_date_col, contributor_returned_end_date_col,
                expected_start_date_col, expected_end_date_col, domain_col,
                equal_weighted_col, set_to_mid_point_col, short_period_parameter_col,
                long_period_parameter_col, da_error_flag_col, trading_date_col,
                trading_domain_col, trading_weights_col)

    # --- Test type validation on the target column lists(s) ---

    def test_target_columns_not_list(self):
        with self.assertRaises(TypeError):
            df_loc = f"{fxt}/da_secondary_wrangler_subfunction_input.csv"
            test_dataframe = load_csv(df_loc)
            # noinspection PyTypeChecker
            secondary_wrangler_subfunction(
                test_dataframe, "Not a list", trading_weights,
                contributor_returned_start_date_col, contributor_returned_end_date_col,
                expected_start_date_col, expected_end_date_col, domain_col,
                equal_weighted_col, set_to_mid_point_col, short_period_parameter_col,
                long_period_parameter_col, da_error_flag_col, trading_date_col,
                trading_domain_col, trading_weights_col)

    # --- Test if cols missing from input dataframe(s) ---

    def test_required_cols_missing_from_input(self):
        df_loc = f"{fxt}/da_secondary_wrangler_subfunction_input.csv"
        test_dataframe = load_csv(df_loc)
        bad_dataframe = test_dataframe.drop([contributor_returned_end_date_col], axis=1)
        with self.assertRaises(KeyError):
            secondary_wrangler_subfunction(
                bad_dataframe, trading_weights, target_columns,
                contributor_returned_start_date_col, contributor_returned_end_date_col,
                expected_start_date_col, expected_end_date_col, domain_col,
                equal_weighted_col, set_to_mid_point_col, short_period_parameter_col,
                long_period_parameter_col, da_error_flag_col, trading_date_col,
                trading_domain_col, trading_weights_col)

    def test_validate_required_cols_missing_from_trading_weight(self):
        test_dataframe = load_csv(f"{fxt}/da_date_adjustment_method_input.csv")
        test_weights = load_csv(f"{fxt}/da_trading_weights_data.csv")
        bad_weights = test_weights.drop(trading_domain_col, axis=1)
        with self.assertRaises(KeyError):
            secondary_wrangler_subfunction(
                test_dataframe, bad_weights, target_columns,
                contributor_returned_start_date_col, contributor_returned_end_date_col,
                expected_start_date_col, expected_end_date_col, domain_col,
                equal_weighted_col, set_to_mid_point_col, short_period_parameter_col,
                long_period_parameter_col, da_error_flag_col, trading_date_col,
                trading_domain_col, trading_weights_col)

    # --- Test if output is a dataframe ---

    def test_output_is_dataframe(self):
        df_loc = f"{fxt}/da_secondary_wrangler_subfunction_input.csv"
        test_dataframe = load_csv(df_loc)
        ret_val = secondary_wrangler_subfunction(
            test_dataframe, trading_weights, target_columns,
            contributor_returned_start_date_col, contributor_returned_end_date_col,
            expected_start_date_col, expected_end_date_col, domain_col,
            equal_weighted_col, set_to_mid_point_col, short_period_parameter_col,
            long_period_parameter_col, da_error_flag_col, trading_date_col,
            trading_domain_col, trading_weights_col)
        assert isinstance(ret_val, type(pd.DataFrame())), "Output should be a dataframe"

    # --- Test if output contents is as expected, both new columns and data content ---

    def test_output_mid_point_not_equal_yt(self):
        actually_tested = 0
        df_loc = f"{fxt}/da_secondary_wrangler_subfunction_input.csv"
        test_dataframe = load_csv(df_loc)
        ret_val = secondary_wrangler_subfunction(
            test_dataframe, trading_weights, target_columns,
            contributor_returned_start_date_col, contributor_returned_end_date_col,
            expected_start_date_col, expected_end_date_col, domain_col,
            equal_weighted_col, set_to_mid_point_col, short_period_parameter_col,
            long_period_parameter_col, da_error_flag_col, trading_date_col,
            trading_domain_col, trading_weights_col)
        for _idx, row in ret_val.iterrows():
            if (row[set_to_mid_point_col] != 'YT' and
                    row[da_error_flag_col] not in error_codes_list):
                actually_tested = 1
                assert (row[dar_col] ==
                        (row['actual_period_end_date'] -
                         row['actual_period_start_date']).days + 1)
        if not actually_tested:
            raise AssertionError(filter_err)

    def test_days_in_contributors_return_period_exists(self):
        df_loc = f"{fxt}/da_secondary_wrangler_subfunction_input.csv"
        test_dataframe = load_csv(df_loc)
        ret_val = secondary_wrangler_subfunction(
            test_dataframe, trading_weights, target_columns,
            contributor_returned_start_date_col, contributor_returned_end_date_col,
            expected_start_date_col, expected_end_date_col, domain_col,
            equal_weighted_col, set_to_mid_point_col, short_period_parameter_col,
            long_period_parameter_col, da_error_flag_col, trading_date_col,
            trading_domain_col, trading_weights_col)
        cols = list(ret_val.columns)
        assert dcr_col in cols

    def test_long_period_marker_set_on_warning(self):
        actually_tested = 0
        df_loc = f"{fxt}/da_secondary_wrangler_subfunction_input.csv"
        test_dataframe = load_csv(df_loc)
        ret_val = secondary_wrangler_subfunction(
            test_dataframe, trading_weights, target_columns,
            contributor_returned_start_date_col, contributor_returned_end_date_col,
            expected_start_date_col, expected_end_date_col, domain_col,
            equal_weighted_col, set_to_mid_point_col, short_period_parameter_col,
            long_period_parameter_col, da_error_flag_col, trading_date_col,
            trading_domain_col, trading_weights_col)
        for _idx, row in ret_val.iterrows():
            if (row[dcr_col]
                    > row[long_period_parameter_col]
                    > row[short_period_parameter_col]
                    and row[da_error_flag_col] not in error_codes_list):
                actually_tested = 1
                assert row['date_adjustment_length_flag'] == 'L'
        if not actually_tested:
            raise AssertionError(filter_err)

    def test_short_period_marker_set_on_warning(self):
        actually_tested = 0
        df_loc = f"{fxt}/da_secondary_wrangler_subfunction_input.csv"
        test_dataframe = load_csv(df_loc)
        ret_val = secondary_wrangler_subfunction(
            test_dataframe, trading_weights, target_columns,
            contributor_returned_start_date_col, contributor_returned_end_date_col,
            expected_start_date_col, expected_end_date_col, domain_col,
            equal_weighted_col, set_to_mid_point_col, short_period_parameter_col,
            long_period_parameter_col, da_error_flag_col, trading_date_col,
            trading_domain_col, trading_weights_col)
        for _idx, row in ret_val.iterrows():
            if (row[dcr_col]
                    < row[short_period_parameter_col]
                    < row[long_period_parameter_col]
                    and row[da_error_flag_col] not in error_codes_list):
                actually_tested = 1
                assert row['date_adjustment_length_flag'] == 'S'
        if not actually_tested:
            raise AssertionError(filter_err)

    def test_double_period_marker_set_on_warning(self):
        actually_tested = 0
        df_loc = f"{fxt}/da_secondary_wrangler_subfunction_input.csv"
        test_dataframe = load_csv(df_loc)
        ret_val = secondary_wrangler_subfunction(
            test_dataframe, trading_weights, target_columns,
            contributor_returned_start_date_col, contributor_returned_end_date_col,
            expected_start_date_col, expected_end_date_col, domain_col,
            equal_weighted_col, set_to_mid_point_col, short_period_parameter_col,
            long_period_parameter_col, da_error_flag_col, trading_date_col,
            trading_domain_col, trading_weights_col)
        for _idx, row in ret_val.iterrows():
            if (row[short_period_parameter_col] > row[long_period_parameter_col]
                    and row[da_error_flag_col] not in error_codes_list):
                actually_tested = 1
                assert row['date_adjustment_length_flag'] == 'SL'
        if not actually_tested:
            raise AssertionError(filter_err)

    def test_equal_weighted_sets_weight_n_correctly(self):
        actually_tested = 0
        df_loc = f"{fxt}/da_secondary_wrangler_subfunction_input.csv"
        test_dataframe = load_csv(df_loc)
        ret_val = secondary_wrangler_subfunction(
            test_dataframe, trading_weights, target_columns,
            contributor_returned_start_date_col, contributor_returned_end_date_col,
            expected_start_date_col, expected_end_date_col, domain_col,
            equal_weighted_col, set_to_mid_point_col, short_period_parameter_col,
            long_period_parameter_col, da_error_flag_col, trading_date_col,
            trading_domain_col, trading_weights_col)
        for _idx, row in ret_val.iterrows():
            if (row[equal_weighted_col] == 'Y' and
                    row[da_error_flag_col] not in error_codes_list):
                actually_tested = 1
                assert row[war_col] == row[dar_col]
        if not actually_tested:
            raise AssertionError(filter_err)

    def test_weights_n_set_correctly(self):
        actually_tested = 0
        df_loc = f"{fxt}/da_secondary_wrangler_subfunction_input.csv"
        test_dataframe = load_csv(df_loc)
        ret_val = secondary_wrangler_subfunction(
            test_dataframe, trading_weights, target_columns,
            contributor_returned_start_date_col,
            contributor_returned_end_date_col, expected_start_date_col,
            expected_end_date_col, domain_col, equal_weighted_col,
            set_to_mid_point_col, short_period_parameter_col,
            long_period_parameter_col, da_error_flag_col, trading_date_col,
            trading_domain_col, trading_weights_col)
        for _idx, row in ret_val.iterrows():
            if (row[equal_weighted_col] != 'Y'
                    and row[da_error_flag_col] not in error_codes_list):
                actually_tested = 1
                mask = (trading_weights[trading_date_col] >=
                        row['actual_period_start_date']) & \
                       (trading_weights[trading_date_col] <=
                        row['actual_period_end_date']) & \
                       (trading_weights[trading_domain_col] ==
                        str(row[domain_col]))
                filtered_weights = trading_weights.loc[mask]
                assert (row[war_col] ==
                        filtered_weights[trading_weights_col].sum()), \
                    "The n weight should be summed correctly"
        if not actually_tested:
            raise AssertionError(filter_err)

    def test_output_still_contains_target_columns(self):
        actually_tested = 0
        df_loc = f"{fxt}/da_secondary_wrangler_subfunction_input.csv"
        test_dataframe = load_csv(df_loc)
        ret_val = secondary_wrangler_subfunction(
            test_dataframe, trading_weights, target_columns,
            contributor_returned_start_date_col,
            contributor_returned_end_date_col, expected_start_date_col,
            expected_end_date_col, domain_col, equal_weighted_col,
            set_to_mid_point_col, short_period_parameter_col,
            long_period_parameter_col, da_error_flag_col, trading_date_col,
            trading_domain_col, trading_weights_col)
        cols = list(ret_val.columns)
        for col_name in target_columns:
            actually_tested = 1
            assert col_name in cols
        if not actually_tested:
            msg = "No test was performed, there are no columns to assert on."
            raise AssertionError(msg)

    # --- Test any other error based outputs ---

    # E6: A required record for calculating weight n
    #     is missing from the trading weights table.

    def test_n_weight_zero_when_E06_generated(self):
        actually_tested = 0
        df_loc = f"{fxt}/da_secondary_wrangler_subfunction_input.csv"
        test_dataframe = load_csv(df_loc)
        ret_val = secondary_wrangler_subfunction(
            test_dataframe, trading_weights, target_columns,
            contributor_returned_start_date_col, contributor_returned_end_date_col,
            expected_start_date_col, expected_end_date_col, domain_col,
            equal_weighted_col, set_to_mid_point_col, short_period_parameter_col,
            long_period_parameter_col, da_error_flag_col, trading_date_col,
            trading_domain_col, trading_weights_col)
        for _idx, row in ret_val.iterrows():
            if row[da_error_flag_col] == 'E06':
                actually_tested = 1
                assert (row[war_col] == 0), \
                    f"The n weight should be zeroed if any contributing " \
                    f"weight records are missing. {row['enterprise_reference_number']} " \
                    f"war_col = {row[war_col]}"
        if not actually_tested:
            raise AssertionError(filter_err)

    #  E7: A required trading weight for calculating weight n is null or blank.

    def test_m_weight_zero_when_E07_generated(self):
        actually_tested = 0
        df_loc = f"{fxt}/da_secondary_wrangler_subfunction_input.csv"
        test_dataframe = load_csv(df_loc)
        ret_val = secondary_wrangler_subfunction(
            test_dataframe, trading_weights, target_columns,
            contributor_returned_start_date_col, contributor_returned_end_date_col,
            expected_start_date_col, expected_end_date_col, domain_col,
            equal_weighted_col, set_to_mid_point_col, short_period_parameter_col,
            long_period_parameter_col, da_error_flag_col, trading_date_col,
            trading_domain_col, trading_weights_col)
        for _idx, row in ret_val.iterrows():
            if row[da_error_flag_col] == 'E07':
                actually_tested = 1
                assert (row[war_col] == 0), \
                    "The m weight should be zeroed if any contributing " + \
                    "weight values are missing"
        if not actually_tested:
            raise AssertionError(filter_err)

    # E8: A required trading weight for calculating weight n has a negative value.

    def test_m_weight_zero_when_E08_generated(self):
        actually_tested = 0
        df_loc = f"{fxt}/da_secondary_wrangler_subfunction_input.csv"
        test_dataframe = load_csv(df_loc)
        ret_val = secondary_wrangler_subfunction(
            test_dataframe, trading_weights, target_columns,
            contributor_returned_start_date_col, contributor_returned_end_date_col,
            expected_start_date_col, expected_end_date_col, domain_col,
            equal_weighted_col, set_to_mid_point_col, short_period_parameter_col,
            long_period_parameter_col, da_error_flag_col, trading_date_col,
            trading_domain_col, trading_weights_col)
        for _idx, row in ret_val.iterrows():
            if row[da_error_flag_col] == 'E08':
                actually_tested = 1
                assert (row[war_col] == 0), \
                    "The m weight should be zeroed if any contributing " + \
                    "weight values are negative"
        if not actually_tested:
            raise AssertionError(filter_err)

    # TODO: Assert that E12 and E13 are being created when expected period
    #       start and end dates are missing.


# ---------------------------------------------------------------------------------------
# SECTION: DATE ADJUSTMENT SUB-FUNCTION
# ---------------------------------------------------------------------------------------

class TestDateAdjustmentSubfunction(TestCase):

    # --- Test fails with type error if no input ---

    def test_input_provided(self):
        self.assertRaises(TypeError)

    # --- Test type validation on the input dataframe(s) ---

    def test_input_is_not_dataframe(self):
        with self.assertRaises(TypeError):
            # noinspection PyTypeChecker
            date_adjustment_subfunction(
                ["Not_A_Dataframe"], target_columns, da_error_flag_col)

    # --- Test type validation on the target column lists(s) ---

    def test_dataframe(self):
        with self.assertRaises(TypeError):
            df_loc = f"{fxt}/da_date_adjustment_subfunction_input.csv"
            test_dataframe = load_csv(df_loc)
            # noinspection PyTypeChecker
            date_adjustment_subfunction(test_dataframe, 'Not a list', da_error_flag_col)

    # --- Test if cols missing from input dataframe(s) ---

    def test_required_cols_missing_from_input(self):
        df_loc = f"{fxt}/da_date_adjustment_subfunction_input.csv"
        test_dataframe = load_csv(df_loc)
        bad_dataframe = test_dataframe.drop(target_columns[0], axis=1)
        with self.assertRaises(KeyError):
            date_adjustment_subfunction(bad_dataframe, target_columns, da_error_flag_col)

    # --- Test if output is a dataframe ---
    def test_return_is_dataframe(self):
        df_loc = f"{fxt}/da_date_adjustment_subfunction_input.csv"
        test_dataframe = load_csv(df_loc)
        ret_val = date_adjustment_subfunction(
            test_dataframe, target_columns, da_error_flag_col)
        assert isinstance(ret_val, type(pd.DataFrame())), "Output should be a dataframe"

    # --- Test if output contents is as expected, both new columns and data content ---

    def test_date_adjustment_calculation(self):
        actually_tested = 0
        df_loc = f"{fxt}/da_date_adjustment_subfunction_input.csv"
        test_dataframe = load_csv(df_loc)
        ret_val = date_adjustment_subfunction(
            test_dataframe, target_columns, da_error_flag_col)
        for _idx, row in ret_val.iterrows():
            if row[da_error_flag_col] not in error_codes_list:
                for col_name in target_columns:
                    calc_col = 'date_adjusted_' + col_name
                    returned_value = row[calc_col]
                    expected_value = (row[col_name] * (row[war_col] / row[wcr_col]))
                    actually_tested = 1
                    assert returned_value == expected_value
        if not actually_tested:
            raise AssertionError(filter_err)

    def test_output_contains_cols_for_next_function(self):
        actually_tested = 0
        df_loc = f"{fxt}/da_date_adjustment_subfunction_input.csv"
        test_dataframe = load_csv(df_loc)
        ret_val = date_adjustment_subfunction(
            test_dataframe, target_columns, da_error_flag_col)
        cols = list(ret_val.columns)
        assert average_weekly_col in cols
        assert da_error_flag_col in cols
        for col_name in target_columns:
            actually_tested = 1
            assert col_name in cols
        if not actually_tested:
            raise AssertionError(filter_err)

    # --- Test any other error based outputs ---

    def test_weights_m_equals_null_on_E10(self):
        df_loc = f"{fxt}/da_date_adjustment_subfunction_input.csv"
        test_dataframe = load_csv(df_loc)
        bad_dataframe = test_dataframe.copy()
        bad_dataframe[wcr_col].iloc[0] = 0
        bad_dataframe[war_col].iloc[0] = 1
        ret_val = date_adjustment_subfunction(
            bad_dataframe, target_columns, da_error_flag_col)
        actually_tested = 0
        for _idx, row in ret_val.iterrows():
            if row[da_error_flag_col] == 'E10':
                actually_tested = 1
                for col_name in target_columns:
                    temp_name = 'date_adjusted_' + col_name
                    assert (np.isnan(row[temp_name])), "Should be null when flagged E10"
        if not actually_tested:
            raise AssertionError(filter_err)

    def test_weights_n_equals_null_on_E11(self):
        df_loc = f"{fxt}/da_date_adjustment_subfunction_input.csv"
        test_dataframe = load_csv(df_loc)
        bad_dataframe = test_dataframe.copy()
        bad_dataframe[wcr_col].iloc[0] = 1
        bad_dataframe[war_col].iloc[0] = 0
        ret_val = date_adjustment_subfunction(
            bad_dataframe, target_columns, da_error_flag_col)
        actually_tested = 0
        for _idx, row in ret_val.iterrows():
            if row[da_error_flag_col] == 'E11':
                actually_tested = 1
                for col_name in target_columns:
                    temp_name = 'date_adjusted_' + col_name
                    assert (np.isnan(row[temp_name])), "Should be null when flagged E11"
        if not actually_tested:
            raise AssertionError(filter_err)


# ---------------------------------------------------------------------------------------
# SECTION: AVERAGE WEEKLY SUB-FUNCTION
# ---------------------------------------------------------------------------------------

class TestAverageWeeklySubfunction(TestCase):

    # --- Test fails with type error if no input ---

    def test_input_provided(self):
        self.assertRaises(TypeError)

    # --- Test type validation on the input dataframe(s) ---

    def test_validate_first_input_is_dataframe(self):
        with self.assertRaises(TypeError):
            # noinspection PyTypeChecker
            average_weekly_subfunction(
                ["Not_A_Dataframe"], average_weekly_questions, da_error_flag_col)

    # --- Test type validation on the target column lists(s) ---

    def test_validate_second_input_is_list(self):
        with self.assertRaises(TypeError):
            df_loc = f"{fxt}/da_average_weekly_subfunction_input.csv"
            test_dataframe = load_csv(df_loc)
            # noinspection PyTypeChecker
            average_weekly_subfunction(test_dataframe, 'Not_a_list', da_error_flag_col)

    # --- Test if cols missing from input dataframe(s) ---

    def test_required_cols_missing_from_input(self):
        df_loc = f"{fxt}/da_average_weekly_subfunction_input.csv"
        test_dataframe = load_csv(df_loc)
        bad_dataframe = test_dataframe.drop(average_weekly_questions[0:-1], axis=1)
        with self.assertRaises(KeyError):
            date_adjustment_subfunction(
                bad_dataframe, average_weekly_questions, da_error_flag_col)

    # --- Test if output is a dataframe ---
    def test_return_is_dataframe(self):
        df_loc = f"{fxt}/da_average_weekly_subfunction_input.csv"
        test_dataframe = load_csv(df_loc)
        ret_val = average_weekly_subfunction(
            test_dataframe, average_weekly_questions, da_error_flag_col)
        assert isinstance(ret_val, type(pd.DataFrame()))

    # --- Test if output contents is as expected, both new columns and data content ---

    def test_no_aw_cols_when_no_question_list(self):
        df_loc = f"{fxt}/da_average_weekly_subfunction_input.csv"
        test_dataframe = load_csv(df_loc)
        ret_val = average_weekly_subfunction(test_dataframe, [], da_error_flag_col)
        for base_col_name in target_columns:
            new_col_name = 'average_weekly_' + base_col_name
            assert new_col_name not in ret_val.columns

    def test_output_contains_all_expected_cols(self):
        df_loc = f"{fxt}/da_average_weekly_subfunction_input.csv"
        test_dataframe = load_csv(df_loc)
        ret_val = average_weekly_subfunction(
            test_dataframe, average_weekly_questions, da_error_flag_col)
        cols = list(ret_val.columns)
        expected_cols = list(ret_val.columns)
        for base_col_name in average_weekly_questions:
            new_col_name = ('average_weekly_' + base_col_name)
            expected_cols.append(new_col_name)
        for col_name in expected_cols:
            assert (col_name in cols)

    def test_output_contains_no_unexpected_cols(self):
        df_loc = f"{fxt}/da_average_weekly_subfunction_input.csv"
        test_dataframe = load_csv(df_loc)
        ret_val = average_weekly_subfunction(
            test_dataframe, average_weekly_questions, da_error_flag_col)
        actual_cols = list(ret_val.columns)
        expected_cols = list(ret_val.columns)
        for base_col_name in average_weekly_questions:
            new_col_name = ('average_weekly_' + base_col_name)
            expected_cols.append(new_col_name)
        for col_name in expected_cols:
            if col_name in actual_cols:
                actual_cols = [x for x in actual_cols if x != col_name]
        assert actual_cols == []

    def test_aw_data_content_is_correct(self):
        df_loc = f"{fxt}/da_average_weekly_subfunction_input.csv"
        test_dataframe = load_csv(df_loc)
        ret_val = average_weekly_subfunction(
            test_dataframe, average_weekly_questions, da_error_flag_col)
        actually_tested = 0
        for _idx, row in ret_val.iterrows():
            if row[da_error_flag_col] not in error_codes_list:
                for base_col in average_weekly_questions:
                    check_col = 'average_weekly_' + base_col
                    source_col = 'date_adjusted_' + base_col
                    actually_tested = 1
                    assert row[check_col] == (7 * row[source_col]) / row[dar_col]
        if not actually_tested:
            if not average_weekly_questions:
                msg = "No test was performed, average_weekly_questions is empty list."
                raise AssertionError(msg)
            else:
                raise AssertionError(filter_err)

    # --- Test any other error based outputs ---
    # None at the moment


# ---------------------------------------------------------------------------------------
# UAT ISSUES
# ---------------------------------------------------------------------------------------

class UserAcceptanceTesting(TestCase):

    # noinspection PyMethodMayBeStatic
    def test_uat_fix_1(self):
        # Failure caused by all rows being in error flagged stat before secondary
        # wrangler could add required columns.
        # Fix is to return dataframe as is, as soon as all columns are carrying flags.
        # Decided against raising ValueError as we want to return the dataframe to users
        # so that they can see error codes.
        test_dataframe = load_csv(f"{fxt}/da_uat_1_data.csv")
        test_weights = load_csv(f"{fxt}/da_uat_1_weights.csv")
        ret_val = date_adjustment(
            input_dataframe=test_dataframe,
            trading_weights=test_weights,
            target_columns=['Q20'],
            contributor_returned_start_date_col="Contributor's returned Start date",
            contributor_returned_end_date_col="Contributor's returned End Date",
            expected_start_date_col="Expected start date",
            expected_end_date_col="Expected End date",
            domain_col="Domain input",
            short_period_parameter_col="Short period parameter",
            long_period_parameter_col="Long period parameter",
            equal_weighted_col="Equal weighted",
            set_to_mid_point_col="Mid-point",
            use_calendar_days_col="Calendar days",
            average_weekly_col="Average weekly",
            da_error_flag_col="Date Adjustment error",
            trading_date_col="date",
            trading_weights_col="weight",
            trading_domain_col="domain",
            trading_period_start_col='start',
            trading_period_end_col='end'
        )
        assert isinstance(ret_val, type(pd.DataFrame()))
        for _idx, row in ret_val.iterrows():
            assert (row["Date Adjustment error"] in ['E14', 'E15'] and
                    wcr_col not in row.keys() and
                    dcr_col not in row.keys()), \
                f"All rows should be in error (14/15) and output returned " \
                f"before {wcr_col} and {dcr_col} are created. " \
                f"Ref:{row['RU']}"

    # noinspection PyMethodMayBeStatic
    def test_uat_fix_2(self):
        test_dataframe = load_csv(f"{fxt}/da_uat_2_data.csv")
        test_weights = load_csv(f"{fxt}/da_uat_2_weights.csv")
        ret_val = date_adjustment(
            input_dataframe=test_dataframe,
            trading_weights=test_weights,
            target_columns=['Q20'],
            contributor_returned_start_date_col="Contributor's returned Start date",
            contributor_returned_end_date_col="Contributor's returned End Date",
            expected_start_date_col="Expected start date",
            expected_end_date_col="Expected End date",
            domain_col="Domain input",
            short_period_parameter_col="Short period parameter",
            long_period_parameter_col="Long period parameter",
            equal_weighted_col="Equal weighted",
            set_to_mid_point_col="Mid-point",
            use_calendar_days_col="Calendar days",
            average_weekly_col="Average weekly",
            da_error_flag_col="Date Adjustment error",
            trading_date_col="date",
            trading_weights_col="weight",
            trading_domain_col="domain",
            trading_period_start_col='start',
            trading_period_end_col='end'
        )
        assert isinstance(ret_val, type(pd.DataFrame()))
        for _idx, row in ret_val.iterrows():
            assert row["Date Adjustment error"] != "E03"

    # noinspection PyMethodMayBeStatic
    def test_uat_fix_3(self):
        # Failure caused by average_weekly calculation using base value
        # rather than date_adjusted value.
        # Fix is to correct calculations in code and unit tests, and utilise a hard
        # coded comparison for this UAT test.
        test_dataframe = load_csv(f"{fxt}/da_uat_3_data.csv")
        test_weights = load_csv(f"{fxt}/da_uat_3_weights.csv")
        ret_val = date_adjustment(
            input_dataframe=test_dataframe,
            trading_weights=test_weights,
            target_columns=['Q20'],
            contributor_returned_start_date_col="Contributor's returned Start date",
            contributor_returned_end_date_col="Contributor's returned End Date",
            expected_start_date_col="Expected start date",
            expected_end_date_col="Expected End date",
            domain_col="Domain input",
            short_period_parameter_col="Short period parameter",
            long_period_parameter_col="Long period parameter",
            equal_weighted_col="Equal weighted",
            set_to_mid_point_col="Mid-point",
            use_calendar_days_col="Calendar days",
            average_weekly_col="Average weekly",
            da_error_flag_col="Date Adjustment error",
            trading_date_col="date",
            trading_weights_col="weight",
            trading_domain_col="domain",
            trading_period_start_col='start',
            trading_period_end_col='end'
        )
        expected_values = [308.5,
                           454.76190476190476,
                           2755.0000000000005,
                           1912.5,
                           1615.9374999999998,
                           414.75,
                           1933.9473684210523,
                           1576.3999999999999,
                           870.25,
                           1005.4545454545458]
        assert isinstance(ret_val, type(pd.DataFrame()))
        returned_values = list(ret_val["average_weekly_Q20"])
        assert returned_values == expected_values

    # noinspection PyMethodMayBeStatic
    def test_uat_fix_4(self):
        # Failure caused by hardcoded reference to record['weight'] not being picked up
        # as test data column was also named 'weight'. Mea culpa, should have spotted
        # that earlier.
        # Fix is to correct hard coded references to 'weight into references to
        # trading_weight_col.
        test_dataframe = load_csv(f"{fxt}/da_uat_4_data.csv")
        test_weights = load_csv(f"{fxt}/da_uat_4_weights.csv")
        ret_val = date_adjustment(
            input_dataframe=test_dataframe,
            trading_weights=test_weights,
            target_columns=['q20'],
            contributor_returned_start_date_col="contributors_returned_start_date",
            contributor_returned_end_date_col="contributors_returned_end_date",
            expected_start_date_col="expected_start_date",
            expected_end_date_col="expected_end_date",
            domain_col="domain_input",
            short_period_parameter_col="short_period_parameter",
            long_period_parameter_col="long_period_parameter",
            equal_weighted_col="use_equal_weighted",
            set_to_mid_point_col="use_midpoint",
            use_calendar_days_col="use_calendar_days",
            average_weekly_col="average_weekly",
            da_error_flag_col="date_adjustment_error",
            trading_date_col="date",
            trading_weights_col="weight",
            trading_domain_col="domain",
            trading_period_start_col='start',
            trading_period_end_col='end'
        )
        assert isinstance(ret_val, type(pd.DataFrame()))

    # noinspection PyMethodMayBeStatic
    def test_uat_fix_5(self):
        # Failure (wrong E code) caused by invalid time being provided for expected
        # period start and end dates.
        # Fix is to validate on a row basis during primary wrangler, midpoint and
        # secondary wrangler sub functions.
        # As it is row by row, error flags need to be used, so generate two new E codes
        # and validate / update tests where TO-DO placeholders have been left.

        # NB: Initial investigations done but unable to complete due to
        # dev resourcing for SML. - Dom Ford ~ May 2021

        test_dataframe = load_csv(f"{fxt}/da_uat_5_data.csv")
        test_weights = load_csv(f"{fxt}/da_uat_5_weights.csv")
        ret_val = date_adjustment(
            input_dataframe=test_dataframe,
            trading_weights=test_weights, target_columns=['q20'],
            contributor_returned_start_date_col="contributors_returned_start_date",
            contributor_returned_end_date_col="contributors_returned_end_date",
            expected_start_date_col="expected_start_date",
            expected_end_date_col="expected_end_date",
            domain_col="domain_input",
            short_period_parameter_col="short_period_parameter",
            long_period_parameter_col="long_period_parameter",
            equal_weighted_col="use_equal_weighted",
            set_to_mid_point_col="use_midpoint",
            use_calendar_days_col="use_calendar_days",
            average_weekly_col="average_weekly",
            da_error_flag_col="date_adjustment_error",
            trading_date_col="date",
            trading_weights_col="weight",
            trading_domain_col="domain",
            trading_period_start_col='start',
            trading_period_end_col='end'
        )
        assert isinstance(ret_val, type(pd.DataFrame()))
        actually_tested = 0
        for _idx, row in ret_val.iterrows():
            if pd.isnull(row['expected_start_date']):
                actually_tested = 1
                assert (row['date_adjustment_error'] == 'E14'), \
                    "Error E14 should be recorded when the expected start date " + \
                    f"is invalid or missing. Ref:{row['ru']} " \
                    f"EPS:{row['expected_start_date']} " \
                    f"Flag:{row['date_adjustment_error']}"
        if not actually_tested:
            raise AssertionError(filter_err)
        actually_tested = 0
        for _idx, row in ret_val.iterrows():
            if (pd.isnull(row['expected_end_date']) and
                    row['date_adjustment_error'] != 'E14'):
                actually_tested = 1
                assert (row["date_adjustment_error"] == 'E15'), \
                    "Error E15 should be recorded when the expected start date " + \
                    f"is invalid or missing. Ref:{row['ru']} " \
                    f"EPS:{row['expected_start_date']} " \
                    f"Flag:{row['date_adjustment_error']}"
        if not actually_tested:
            raise AssertionError(filter_err)

    # noinspection PyMethodMayBeStatic
    def test_uat_fix_6(self):
        # Notified of 1 day discrepancy when calculating midpoint for 10 Nov to 18 Dec.
        # Actual is 30 Nov, Peter Davies (Methodology) believes it should be 29 Nov.
        test_dataframe = load_csv(f"{fxt}/da_uat_6_data.csv")
        test_weights = load_csv(f"{fxt}/da_uat_6_weights.csv")
        ret_val = midpoint_subfunction(
            test_dataframe,
            trading_weights=test_weights,
            target_columns=['q20'],
            domain_col='domain_SIC_code',
            expected_start_date_col='expected_period_start_date',
            expected_end_date_col='expected_period_end_date',
            contributor_returned_start_date_col='contributors_returned_period_start_date',
            contributor_returned_end_date_col='contributors_returned_period_end_date',
            set_to_mid_point_col='set_to_mid_point',
            equal_weighted_col='set_to_equal_weighted',
            use_calendar_days_col='use_calendar_days',
            trading_date_col="date",
            trading_weights_col="weight",
            trading_domain_col="domain",
            trading_period_start_col='start',
            trading_period_end_col='end',
            da_error_flag_col='date_adjustment_error_flag'
        )
        for _idx, row in ret_val.iterrows():
            assert str(row['midpoint_date']) == '2019-11-29 00:00:00'
