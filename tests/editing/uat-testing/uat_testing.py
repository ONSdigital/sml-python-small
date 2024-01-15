"""
Example code that uses the pandas wrapper showing examples of using it with each valid method,
currently this includes Totals and Components, and Thousand Pounds Correction

For Copyright information, please see LICENCE.
"""
import pytest
import pandas as pd
import datatest as dt
import os
import re

# We import the wrapper function from the pandas_wrapper
from sml_small.utils.pandas_wrapper import wrapper


# Function to take a directory and run the provided method against
# all CSVs that do not contain output in the filename
def run_all_csvs(directory, function):
    for filename in os.listdir(directory):
        if filename.endswith(".csv") and "output" not in filename:
            input_filename = filename
            filename_without_extension, file_extension = os.path.splitext(filename)
            output_filename = f"{filename_without_extension}_output.csv"

            # Call your function for each CSV file
            if function == "totals_and_components":
                run_totals_components_with_pandas(
                    directory, input_filename, output_filename
                )

            # elif function == "thousand_pounds":
            #     run_thousand_pounds_with_pandas(
            #         directory, input_filename, output_filename
            #     )


# Function below is used to read a CSV file from the given
# filepath and return as a DataFrame
def load_csv(filepath):
    df = pd.read_csv(filepath)
    return df


# Function used to extract columns from a dataframe that are treated as a list, e.g comp_1, comp_2, comp_3
def filter_columns_by_pattern(df, pattern):
    return [col for col in df.columns if re.match(pattern, col)]


# This function takes a given dataframe and will expand a provided column that contains a list
# into separate columns based on the provided prefix (for plain lists) or attribute (for custom objects)
def expand_list_column(
    df,
    list_column_name,
    prefix_attribute=None,
    custom_prefix=None,
    custom_suffix="final_value",
):
    final_data = []

    for index, row in df.iterrows():
        data = row.to_dict()
        list_data = row[list_column_name]

        for i, item in enumerate(list_data, start=1):
            if prefix_attribute:
                # If the attribute doesn't exist N/A is added
                column_prefix = getattr(item, prefix_attribute, "N/A")
                column_name = f"{column_prefix}_{custom_suffix}"
                data[column_name] = item.final_value

            else:
                column_name = f"{custom_prefix}_{i}"
                data[column_name] = item

        final_data.append(data)

    return pd.DataFrame(final_data)


# ---------------------------------------
# Totals and Components usage with Pandas
# ---------------------------------------
def run_totals_components_with_pandas(path, input_csv, output_csv):
    # The code below calls the load_csv function
    # with the filename as an argument
    input_dataframe_totals_and_components = load_csv(path + input_csv)

    list_column_pattern = r"comp_\d+"
    # Use a regular expression to select columns that match the pattern 'comp_' followed by one or more digits.
    components = filter_columns_by_pattern(
        input_dataframe_totals_and_components, list_column_pattern
    )

    # We call the wrapper function from pandas_wrapper python file
    # passing in the required arguments, which in this case are
    # column names
    totals_and_components_output_columns = [
        "abs_diff",
        "perc_low",
        "perc_high",
        "tcc_marker",
        "final_total",
        "final_components",
    ]
    test_totals_and_components = wrapper(
        input_dataframe_totals_and_components,
        "totals_and_components",
        output_columns=totals_and_components_output_columns,
        unique_identifier_column="reference",
        total_column="total",
        components_list_columns=components,
        amend_total_column="amend_total",
        predictive_column="predictive",
        auxiliary_column="auxiliary",
        absolute_threshold_column="abs_threshold",
        percentage_threshold_column="perc_threshold",
    )

    # Loop through columns that have list and extract as separate columns
    final_data = expand_list_column(
        df=test_totals_and_components,
        list_column_name="final_components",
        custom_prefix="final_component",
    )

    # Create a new DataFrame from the final_data list
    final_df = pd.DataFrame(final_data)

    # Drop the "final_components" column
    final_df.drop(columns=["final_components"], inplace=True)

    # Move the tpc_marker to be the last column
    column_to_move = "tcc_marker"

    # Define the desired column order with the specified column at the end
    column_order = [col for col in final_df.columns if col != column_to_move] + [
        column_to_move
    ]

    # Create a new DataFrame with the columns in the desired order
    final_df = final_df[column_order]

    # Write the DataFrame to a CSV, excluding the index column
    csv_filename = "tcc_test_data_processed/" + output_csv
    final_df.to_csv(csv_filename, index=False)


# Run example data for Totals and Components
# run_totals_components_with_pandas(
#     "../../tests/editing/totals_and_components/example_data/",
#     "example_test_data.csv",
#     "example_test_data_pandas_output.csv",
# )

# Run Totals and Components UAT
run_all_csvs("tcc_test_data_original/", "totals_and_components")

# # Run example data for Thousands Pounds
# run_thousand_pounds_with_pandas(
#     "../../tests/editing/thousand_pounds/example_data/",
#     "example_test_data.csv",
#     "example_test_data_pandas_output.csv",
# )

# # Run Thousand Pounds UAT
# run_all_csvs("../../tests/editing/thousand_pounds/example_data/uat/", "thousand_pounds")




# UAT Testing
fill_value = 'default_value'

# @pytest.fixture(scope="module")
# @dt.working_directory(__file__)
# def df_input():
#     return pd.read_csv("TCC_test_data/TCC_test_data_case_a1.csv")


# @pytest.fixture(scope="module")
# @dt.working_directory(__file__)
# def df_temp_output():
#     df = pd.read_csv("TCC_test_output_data/TCC_test_data_case_a1_temp_output.csv")
#     df = df.fillna(fill_value)

#     return df

# @pytest.fixture(scope="module")
# @dt.working_directory(__file__)
# def df_correct_output():
#     df = pd.read_csv("TCC_test_data/TCC_test_data_case_a1_output.csv")
#     df = df.drop(columns=['period'])
#     df = df.fillna(fill_value)
#     df.loc[df["TCC_marker"] == "N", "TCC_marker"] = fill_value
#     column_to_move = df.pop("TCC_marker")
#     df.insert(19, "TCC_marker", column_to_move)

#     return df


@pytest.mark.mandatory
def test_input_columns():
    for filename in os.listdir("tcc_test_data_original/"):
        if filename.endswith(".csv") and "output" not in filename:
            print(filename)
            df_input = pd.read_csv("tcc_test_data_original/" + filename)
            dt.validate(
                df_input.columns,
                {
                    "reference",
                    "period",
                    "total",
                    "comp_1",
                    "comp_2",
                    "comp_3",
                    "comp_4",
                    "amend_total",
                    "predictive",
                    "auxiliary",
                    "abs_threshold",
                    "perc_threshold"
                }
            )


@pytest.mark.mandatory
def test_output_columns():
    for filename in os.listdir("tcc_test_data_processed/"):
        df_processed_output = pd.read_csv("tcc_test_data_processed/" + filename)
        dt.validate(
            df_processed_output.columns,
            {
                "reference",
                "total",
                "comp_1",
                "comp_2",
                "comp_3",
                "comp_4",
                "amend_total",
                "predictive",
                "auxiliary",
                "abs_threshold",
                "perc_threshold",
                "abs_diff",
                "perc_low",
                "perc_high",
                "tcc_marker",
                "final_total",
                "final_component_1",
                "final_component_2",
                "final_component_3",
                "final_component_4"
            }
        )

def test_values():
    tcc_test_data_original = os.listdir("tcc_test_data_original/")
    tcc_test_data_processed = os.listdir("tcc_test_data_processed/")

    for file1 in tcc_test_data_processed:
        for file2 in tcc_test_data_original:
            if file1 == file2:
                print(f"Filename '{file1}' and '{file2}' is present in both directories.")
                df_processed_output = pd.read_csv("tcc_test_data_processed/" + file1)

                df_correct_output = pd.read_csv("tcc_test_data_original/" + file2)

                df_processed_output = df_processed_output.fillna(0)
                df_correct_output = df_correct_output.fillna(0)

                with pd.option_context('display.max_rows', None, 'display.max_columns', None):  # more options can be specified also
                    print("Correct output")
                    print(df_correct_output)
                    print("\n")
                    print("Processed output")
                    print(df_processed_output)

                dt.validate.superset(df_processed_output, df_correct_output)
