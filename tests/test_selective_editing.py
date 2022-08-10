from unittest import TestCase

import numpy as np
import pandas as pd

# noinspection PyProtectedMember
from methods.selective_editing import selective_editing

pd.options.mode.chained_assignment = None
pd.set_option('display.max_columns', 30)
pd.set_option('display.max_colwidth', 999)

reference_col = 'reference'
design_weight_col = 'design_weight'
threshold_col = 'threshold'
question_list = ['question_1', 'question_2', 'question_3']
combination_method = 'mean'

filter_err = "No test was performed, all data was filtered out by criteria."
fxt = "fixtures/selective_editing"

show_sums = 1  # 0/1 Bool: Provides additional data on score calculation for checking


def load_csv(filepath):
    # read in base info
    df = pd.read_csv(filepath)
    # Check df dtypes and change where necessary
    # df = _set_dtypes(df, dtype_dict, target_columns)
    return df


# ====================================================================================
# --------------- TESTING TEMPLATE ---------------------------
# ====================================================================================
# --- Test fails with type error if no input ---
# --- Test the input dataframe validation ---
# --- Test the question list validation ---
# --- Test the combination type validation ---
# --- Test  column name params validation ---
# --- Test if cols missing from input dataframe ---
# --- Test if output is a dataframe ---
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

# noinspection PyTypeChecker
class TestSelectiveEditing(TestCase):

    # --- Test fails with type error if no input ---

    def test_input_provided(self):
        self.assertRaises(TypeError)

    # --- Test the input dataframe validation ---

    def test_validate_input_dataframe_type(self):
        with self.assertRaises(TypeError):
            selective_editing(
                ["Not_A_Dataframe"], reference_col, design_weight_col,
                threshold_col, question_list, combination_method)

    def test_validate_reserved_column_names_in_input_dataframe(self):
        df_loc = f"{fxt}/se_selective_editing_method_input.csv"
        bad_dataframe = load_csv(df_loc)
        bad_dataframe['final_score'] = 0
        with self.assertRaises(ValueError):
            selective_editing(
                bad_dataframe, reference_col, design_weight_col,
                threshold_col, question_list, combination_method)

    def test_validate_nan_for_actual_return_in_input_dataframe(self):
        df_loc = f"{fxt}/se_selective_editing_method_input.csv"
        bad_dataframe = load_csv(df_loc)
        bad_dataframe.loc[0, 'question_2_ar'] = np.nan
        with self.assertRaises(ValueError):
            selective_editing(
                bad_dataframe, reference_col, design_weight_col,
                threshold_col, question_list, combination_method)

    def test_validate_nan_for_standardising_factor_in_input_dataframe(self):
        df_loc = f"{fxt}/se_selective_editing_method_input.csv"
        bad_dataframe = load_csv(df_loc)
        bad_dataframe.loc[0, 'question_2_sf'] = np.nan
        with self.assertRaises(ValueError):
            selective_editing(
                bad_dataframe, reference_col, design_weight_col,
                threshold_col, question_list, combination_method)

    def test_validate_nan_for_question_weight_in_input_dataframe(self):
        df_loc = f"{fxt}/se_selective_editing_method_input.csv"
        bad_dataframe = load_csv(df_loc)
        bad_dataframe.loc[0, 'question_2_wt'] = np.nan
        with self.assertRaises(ValueError):
            selective_editing(
                bad_dataframe, reference_col, design_weight_col,
                threshold_col, question_list, 'weighted')

    def test_validate_nan_for_both_predicted_in_input_dataframe(self):
        df_loc = f"{fxt}/se_selective_editing_method_input.csv"
        bad_dataframe = load_csv(df_loc)
        bad_dataframe.loc[0, 'question_2_pv'] = np.nan
        bad_dataframe.loc[0, 'question_2_apv'] = np.nan
        with self.assertRaises(ValueError):
            selective_editing(
                bad_dataframe, reference_col, design_weight_col,
                threshold_col, question_list, combination_method)

    def test_validate_nan_for_basic_reference_data_in_input_dataframe(self):
        df_loc = f"{fxt}/se_selective_editing_method_input.csv"
        for bad_col in [reference_col, design_weight_col, threshold_col]:
            bad_dataframe = load_csv(df_loc)
            bad_dataframe.loc[0, bad_col] = np.nan
            with self.assertRaises(ValueError):
                selective_editing(
                    bad_dataframe, reference_col, design_weight_col,
                    threshold_col, question_list, combination_method)

    # --- Test the question list validation ---

    def test_validate_question_list_type(self):
        with self.assertRaises(TypeError):
            df_loc = f"{fxt}/se_selective_editing_method_input.csv"
            test_dataframe = load_csv(df_loc)
            selective_editing(
                test_dataframe, reference_col, design_weight_col,
                threshold_col, 'Not a list', combination_method)

    def test_validate_question_list_value(self):
        with self.assertRaises(ValueError):
            df_loc = f"{fxt}/se_selective_editing_method_input.csv"
            test_dataframe = load_csv(df_loc)
            selective_editing(
                test_dataframe, reference_col, design_weight_col,
                threshold_col, [], combination_method)

    def test_validate_question_list_contents_type(self):
        with self.assertRaises(TypeError):
            df_loc = f"{fxt}/se_selective_editing_method_input.csv"
            test_dataframe = load_csv(df_loc)
            selective_editing(
                test_dataframe, reference_col, design_weight_col,
                threshold_col, [1, 2, 3], combination_method)

    # --- Test the combination type validation ---

    def test_validate_combination_method_type(self):
        with self.assertRaises(TypeError):
            df_loc = f"{fxt}/se_selective_editing_method_input.csv"
            test_dataframe = load_csv(df_loc)
            selective_editing(
                test_dataframe, reference_col, design_weight_col,
                threshold_col, question_list, ['not a string'])

    def test_validate_combination_method_value(self):
        with self.assertRaises(ValueError):
            df_loc = f"{fxt}/se_selective_editing_method_input.csv"
            test_dataframe = load_csv(df_loc)
            selective_editing(
                test_dataframe, reference_col, design_weight_col,
                threshold_col, question_list, 'incorrect')

    # --- Test the minkowski distance type validation ---

    def test_validate_minkowski_distance_param_type(self):
        with self.assertRaises(TypeError):
            df_loc = f"{fxt}/se_selective_editing_method_input.csv"
            test_dataframe = load_csv(df_loc)
            selective_editing(
                test_dataframe, reference_col, design_weight_col,
                threshold_col, question_list, 'minkowski', '2')

    def test_validate_minkowski_distance_param_value(self):
        with self.assertRaises(ValueError):
            df_loc = f"{fxt}/se_selective_editing_method_input.csv"
            test_dataframe = load_csv(df_loc)
            selective_editing(
                test_dataframe, reference_col, design_weight_col,
                threshold_col, question_list, 'minkowski', 0)

    # --- Test column name params validation ---

    def test_validate_column_name_param_type(self):
        df_loc = f"{fxt}/se_selective_editing_method_input.csv"
        test_dataframe = load_csv(df_loc)
        for i in range(3):
            bad_list = [reference_col, design_weight_col, threshold_col]
            bad_list[i] = [bad_list[i]]
            with self.assertRaises(TypeError):
                selective_editing(
                    test_dataframe, bad_list[0], bad_list[1], bad_list[2],
                    question_list, combination_method)

    # --- Test if cols missing from input dataframe ---

    def test_validate_basic_reference_columns_present(self):
        df_loc = f"{fxt}/se_selective_editing_method_input.csv"
        test_dataframe = load_csv(df_loc)
        for i in range(3):
            bad_list = [reference_col, design_weight_col, threshold_col]
            bad_list[i] = 'bad-column-name'
            with self.assertRaises(KeyError):
                selective_editing(
                    test_dataframe, bad_list[0], bad_list[1], bad_list[2],
                    question_list, combination_method)

    def test_validate_question_data_columns_present(self):
        df_loc = f"{fxt}/se_selective_editing_method_input.csv"
        test_dataframe = load_csv(df_loc)
        for qst in question_list:
            for sfx in ['_ar', '_pv', '_apv', '_sf']:
                drop_col = f"{qst}{sfx}"
                bad_dataframe = test_dataframe.drop(drop_col, axis=1)
                with self.assertRaises(KeyError):
                    selective_editing(
                        bad_dataframe, reference_col, design_weight_col,
                        threshold_col, question_list, combination_method)

    def test_validate_question_weight_columns_present_for_weighted_combination(self):
        df_loc = f"{fxt}/se_selective_editing_method_input.csv"
        test_dataframe = load_csv(df_loc)
        for x in range(1, 4):
            drop_col = f"question_{x}_wt"
            test_dataframe.drop(columns=[drop_col], inplace=True)
        with self.assertRaises(KeyError):
            selective_editing(
                test_dataframe, reference_col, design_weight_col,
                threshold_col, question_list, 'weighted')

    # --- Test if output is a dataframe ---

    def test_return_is_dataframe(self):
        df_loc = f"{fxt}/se_selective_editing_method_input.csv"
        test_dataframe = load_csv(df_loc)
        ret_val = selective_editing(
                test_dataframe, reference_col, design_weight_col,
                threshold_col, question_list, combination_method, show_sums)
        assert isinstance(ret_val, type(pd.DataFrame()))
        # Not part of the actual test, but a good place to record the output as a CSV.
        ret_val.to_csv('testing_output.csv', index=False)

    # --- Test if output contents is as expected, both new columns and data content ---

    def test_scores_are_present_for_each_question(self):
        df_loc = f"{fxt}/se_selective_editing_method_input.csv"
        test_dataframe = load_csv(df_loc)
        ret_val = selective_editing(
                test_dataframe, reference_col, design_weight_col,
                threshold_col, question_list, combination_method)
        cols = list(ret_val.columns)
        assert 'question_1_s' in cols
        assert 'question_2_s' in cols
        assert 'question_3_s' in cols

    def test_predicted_markers_are_present_for_each_question(self):
        df_loc = f"{fxt}/se_selective_editing_method_input.csv"
        test_dataframe = load_csv(df_loc)
        ret_val = selective_editing(
                test_dataframe, reference_col, design_weight_col,
                threshold_col, question_list, combination_method)
        cols = list(ret_val.columns)
        assert 'question_1_pm' in cols
        assert 'question_2_pm' in cols
        assert 'question_3_pm' in cols

    def test_fixed_output_columns_are_present(self):
        df_loc = f"{fxt}/se_selective_editing_method_input.csv"
        test_dataframe = load_csv(df_loc)
        ret_val = selective_editing(
                test_dataframe, reference_col, design_weight_col,
                threshold_col, question_list, combination_method)
        cols = list(ret_val.columns)
        assert 'reference' in cols
        assert 'design_weight' in cols
        assert 'threshold' in cols
        assert 'final_score' in cols
        assert 'selective_editing_marker' in cols

    def test_weighted_scores_are_present_when_weighted_combination_used(self):
        df_loc = f"{fxt}/se_selective_editing_method_input.csv"
        test_dataframe = load_csv(df_loc)
        test_dataframe['question_1_wt'] = 0.34
        test_dataframe['question_2_wt'] = 0.33
        test_dataframe['question_3_wt'] = 0.33
        ret_val = selective_editing(
                test_dataframe, reference_col, design_weight_col,
                threshold_col, question_list, 'weighted')
        cols = list(ret_val.columns)
        assert 'question_1_wts' in cols
        assert 'question_2_wts' in cols
        assert 'question_3_wts' in cols

    def test_minkowski_scores_are_present_when_minkowski_combination_used(self):
        df_loc = f"{fxt}/se_selective_editing_method_input.csv"
        test_dataframe = load_csv(df_loc)
        ret_val = selective_editing(
            test_dataframe, reference_col, design_weight_col,
            threshold_col, question_list, 'minkowski', 2)
        cols = list(ret_val.columns)
        assert 'question_1_mks' in cols
        assert 'question_2_mks' in cols
        assert 'question_3_mks' in cols

    def test_predictive_marker_being_set_to_false_when_apv_used(self):
        actually_tested = 0
        df_loc = f"{fxt}/se_selective_editing_method_input.csv"
        test_dataframe = load_csv(df_loc)
        ret_val = selective_editing(
            test_dataframe, reference_col, design_weight_col,
            threshold_col, question_list, combination_method)
        for question_name in question_list:
            pv_col = f"{question_name}_pv"
            p_marker_col = f"{question_name}_pm"
            check_df = ret_val[(ret_val[pv_col].isna())]
            if not check_df.empty:
                actually_tested = 1
                assert not check_df[p_marker_col].any()
        if not actually_tested:
            raise AssertionError(filter_err)

    def test_scores_as_expected_for_maximum_combination_mode(self):
        df_loc = f"{fxt}/se_selective_editing_method_input.csv"
        test_dataframe = load_csv(df_loc)
        df_loc = f"{fxt}/se_methodology_calculated_outputs.csv"
        results_df = load_csv(df_loc)
        ret_val = selective_editing(
            test_dataframe, reference_col, design_weight_col,
            threshold_col, question_list, 'maximum')
        for idx, row in ret_val.iterrows():
            ru_ref = row['reference']
            check_df = results_df.loc[results_df.reference == ru_ref]

            for score_col in ['question_1_s', 'question_2_s', 'question_3_s']:
                actual = float(f"{row[score_col]:.6f}")
                expected = float(f"{check_df[score_col].item():.6f}")
                assert actual == expected,\
                    f"Question {idx + 1} score of {actual} for ref {ru_ref} " \
                    f"not {expected} as expected."

            actual = float(f"{row['final_score']:.6f}")
            expected = float(f"{check_df['max_score'].item():.6f}")
            assert actual == expected, \
                f"Final score of {actual} for ref {ru_ref} " \
                f"not {expected} as expected."

            actual = bool(row['selective_editing_marker'])
            expected = bool(check_df['se_marker_max'].item())
            assert actual == expected, \
                f"SE Marker of {actual} for ref {ru_ref} " \
                f"not {expected} as expected."

    def test_scores_as_expected_for_mean_combination_mode(self):
        df_loc = f"{fxt}/se_selective_editing_method_input.csv"
        test_dataframe = load_csv(df_loc)
        df_loc = f"{fxt}/se_methodology_calculated_outputs.csv"
        results_df = load_csv(df_loc)
        ret_val = selective_editing(
            test_dataframe, reference_col, design_weight_col,
            threshold_col, question_list, 'mean')
        for idx, row in ret_val.iterrows():
            ru_ref = row['reference']
            check_df = results_df.loc[results_df.reference == ru_ref]

            for score_col in ['question_1_s', 'question_2_s', 'question_3_s']:
                actual = float(f"{row[score_col]:.6f}")
                expected = float(f"{check_df[score_col].item():.6f}")
                assert actual == expected,\
                    f"Question {idx + 1} score of {actual} for ref {ru_ref} " \
                    f"not {expected} as expected."

            actual = float(f"{row['final_score']:.6f}")
            expected = float(f"{check_df['mean_score'].item():.6f}")
            assert actual == expected, \
                f"Final score of {actual} for ref {ru_ref} " \
                f"not {expected} as expected."

            actual = bool(row['selective_editing_marker'])
            expected = bool(check_df['se_marker_mean'].item())
            assert actual == expected, \
                f"SE Marker of {actual} for ref {ru_ref} " \
                f"not {expected} as expected."

    def test_scores_as_expected_for_weighted_combination_mode(self):
        df_loc = f"{fxt}/se_selective_editing_method_input.csv"
        test_dataframe = load_csv(df_loc)
        df_loc = f"{fxt}/se_methodology_calculated_outputs.csv"
        results_df = load_csv(df_loc)
        ret_val = selective_editing(
            test_dataframe, reference_col, design_weight_col,
            threshold_col, question_list, 'weighted')
        for idx, row in ret_val.iterrows():
            ru_ref = row['reference']
            check_df = results_df.loc[results_df.reference == ru_ref]

            for score_col in ['question_1_wts', 'question_2_wts', 'question_3_wts']:
                actual = float(f"{row[score_col]:.6f}")
                expected = float(f"{check_df[score_col].item():.6f}")
                assert actual == expected,\
                    f"Question {idx + 1} weighted score of {actual} for ref {ru_ref} " \
                    f"not {expected} as expected."

            actual = float(f"{row['final_score']:.6f}")
            expected = float(f"{check_df['weighted_score'].item():.6f}")
            assert actual == expected, \
                f"Final score of {actual} for ref {ru_ref} " \
                f"not {expected} as expected."

            actual = bool(row['selective_editing_marker'])
            expected = bool(check_df['se_marker_weighted'].item())
            assert actual == expected, \
                f"SE Marker of {actual} for ref {ru_ref} " \
                f"not {expected} as expected."

    def test_scores_as_expected_for_minkowski_combination_mode(self):
        df_loc = f"{fxt}/se_selective_editing_method_input.csv"
        test_dataframe = load_csv(df_loc)
        df_loc = f"{fxt}/se_methodology_calculated_outputs.csv"
        results_df = load_csv(df_loc)
        ret_val = selective_editing(
            test_dataframe, reference_col, design_weight_col,
            threshold_col, question_list, 'minkowski', 4)
        for idx, row in ret_val.iterrows():
            ru_ref = row['reference']
            check_df = results_df.loc[results_df.reference == ru_ref]

            for score_col in ['question_1_mks', 'question_2_mks', 'question_3_mks']:
                actual = float(f"{row[score_col]:.6f}")
                expected = float(f"{check_df[score_col].item():.6f}")
                assert actual == expected,\
                    f"Question {idx + 1} score of {actual} for ref {ru_ref} " \
                    f"not {expected} as expected."

            actual = float(f"{row['final_score']:.6f}")
            expected = float(f"{check_df['minkowski_score'].item():.6f}")
            assert actual == expected, \
                f"Final score of {actual} for ref {ru_ref} " \
                f"not {expected} as expected."

            actual = bool(row['selective_editing_marker'])
            expected = bool(check_df['se_marker_minkowski'].item())
            assert actual == expected, \
                f"SE Marker of {actual} for ref {ru_ref} " \
                f"not {expected} as expected."
