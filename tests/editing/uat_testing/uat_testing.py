"""
Example code that uses the pandas wrapper showing examples of using it with each valid method,
currently this includes Totals and Components, and Thousand Pounds Correction

For Copyright information, please see LICENCE.
"""

import itertools
import os
import re

import datatest as dt
import numpy as np
import pandas as pd
import pytest

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

            elif function == "thousand_pounds":
                run_thousand_pounds_with_pandas(
                    directory, input_filename, output_filename
                )


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

    for _, row in df.iterrows():
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

    # Move the tcc_marker to be the last column
    column_to_move = "tcc_marker"

    # Define the desired column order with the specified column at the end
    column_order = [col for col in final_df.columns if col != column_to_move] + [
        column_to_move
    ]

    # Create a new DataFrame with the columns in the desired order
    final_df = final_df[column_order]

    # Create the tcc_test_data_processed folder if it doesn't exist
    os.makedirs("tcc_test_data_processed", exist_ok=True)

    # Write the DataFrame to a CSV, excluding the index column
    csv_filename = "tcc_test_data_processed/" + output_csv
    final_df.to_csv(csv_filename, index=False)


# ---------------------------------------
# Thousand Pounds usage with Pandas
# ---------------------------------------
def run_thousand_pounds_with_pandas(path, input_csv, output_csv):
    input_dataframe_thousand_pounds = load_csv(path + input_csv)

    # match target variable columns q<number>
    list_column_pattern = r"q\d+"
    target_variables = filter_columns_by_pattern(
        input_dataframe_thousand_pounds, list_column_pattern
    )

    thousand_pounds_output_columns = [
        "principal_final_value",
        "target_variables",
        "tpc_ratio",
        "tpc_marker",
    ]
    test_thousand_pounds = wrapper(
        input_dataframe_thousand_pounds,
        "thousand_pounds",
        output_columns=thousand_pounds_output_columns,
        unique_identifier_column="RU",
        principal_variable_column="principal_val",
        target_variables_columns=target_variables,
        upper_limit_column="threshold_upper",
        lower_limit_column="threshold_lower",
        predictive_column="predictive_val",
        auxiliary_column="aux_val",
    )

    # Expand columns that contain a list of objects (e.g target_variable [TargetVariable(identifier='q42', original_value='32', final_value='0.032'),...])
    # and create separate columns e.g: q42_final_value
    final_data = expand_list_column(
        df=test_thousand_pounds,
        list_column_name="target_variables",
        prefix_attribute="identifier",
    )

    # Create a new DataFrame from the final_data list
    final_df = pd.DataFrame(final_data)

    # Drop the "target_variables" column
    final_df.drop(columns=["target_variables"], inplace=True)

    # Move the tpc_marker to be the last column
    column_to_move = "tpc_marker"

    # Define the desired column order with the specified column at the end
    column_order = [col for col in final_df.columns if col != column_to_move] + [
        column_to_move
    ]

    # Update the DataFrame with the columns in the desired order
    final_df = final_df[column_order]

    # Create the tpc_test_data_processed folder if it doesn't exist
    os.makedirs("tpc_test_data_processed", exist_ok=True)

    # Write the DataFrame to a CSV, excluding the index column
    csv_filename = "tpc_test_data_processed/" + output_csv
    final_df.to_csv(csv_filename, index=False)


# This fixture is used to set up the environment before running the tests
# It is automatically used by all test functions in the session scope
@pytest.fixture(scope="session", autouse=True)
def setup_before_tests():
    # Code to run before tests
    print("Running the TCC & TPC input CSV files through the pandas wrapper...")
    # Run Totals and Components UAT
    run_all_csvs("tcc_test_data_original/", "totals_and_components")
    # Run Thousand Pounds UAT
    run_all_csvs("tpc_test_data_original/", "thousand_pounds")
    yield
    # Code to run after tests
    print("Testing has finished")


# Set of column names for the original input CSV files that we will use to test against
# the original input CSV files that is in the tcc_test_data_original directory
tcc_original_input_column_names = [
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
    "perc_threshold",
]

# Set of column names for the processed output CSV files that we will use to test against
# the processed output CSV files that is in the tcc_test_data_processed directory
tcc_processed_output_column_names = [
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
    "final_total",
    "final_component_1",
    "final_component_2",
    "final_component_3",
    "final_component_4",
    "tcc_marker",
]

# Set of column names for the original input CSV files that we will use to test against
# the original input CSV files that is in the tpc_test_data_original directory
# Target variable column names such as q42 will not be tested as target variables can be named anything,
# and there can be many different target variables
tpc_original_input_column_names = [
    "RU",
    "period",
    "principal_val",
    "predictive_val",
    "aux_val",
    "threshold_upper",
    "threshold_lower",
]

# Set of column names for the processed output CSV files that we will use to test against
# the processed output CSV files that is in the tpc_test_data_processed directory
# Target variable column names such as q42, q42_final_value will not be tested as target variables can be named anything,
# and there can be many different target variables
tpc_processed_output_column_names = [
    "RU",
    "principal_val",
    "threshold_upper",
    "threshold_lower",
    "predictive_val",
    "aux_val",
    "principal_final_value",
    "tpc_ratio",
    "tpc_marker",
]


# Use the parametrize decorator to run the test with different arguments
@pytest.mark.parametrize(
    "directory,type_to_test,column_names,ignored_column_names",
    [
        ("tcc_test_data_original/", "input", tcc_original_input_column_names, []),
        ("tcc_test_data_processed/", "output", tcc_processed_output_column_names, []),
        (
            "tpc_test_data_original/",
            "input",
            tpc_original_input_column_names,
            ["q42", "q43"],
        ),
        (
            "tpc_test_data_processed/",
            "output",
            tpc_processed_output_column_names,
            ["q42", "q43", "q42_final_value", "q43_final_value"],
        ),
    ],
)
# This function is used to test the column names in a CSV file
# It takes directory, type_to_test, column_names and ignored_column_names as parameters
# directory is the location of the CSV files we want to test
# type_of_test specifies if it's the input files or output files we want to test
# column_names takes in the column_names we want to test against the CSV files
# ignored_column_names takes in the column names we want to ignore when testing the CSV files
@pytest.mark.mandatory
def test_column_names(directory, type_to_test, column_names, ignored_column_names):
    print("\n")
    for filename in os.listdir(directory):
        if (
            type_to_test == "input"
            and filename.endswith(".csv")
            and "output" not in filename
        ):
            df_input = pd.read_csv(directory + filename)
            print(f"Testing {directory}: {filename} input column names")
            dt.validate(
                [col for col in df_input.columns if col not in ignored_column_names],
                column_names,
            )

        elif type_to_test == "output":
            df_processed_output = pd.read_csv(directory + filename)
            print(f"Testing {directory}: {filename} output column names")
            dt.validate(
                [
                    col
                    for col in df_processed_output.columns
                    if col not in ignored_column_names
                ],
                column_names,
            )


# This function is used to round the decimal places of any decimal value found in the
# processed output CSV file that is in the tcc_test_data_processed directory
# It takes in the processed output CSV file and the expected output CSV file as parameters
# It checks if the processed output value is a float and if it is, it checks if it has a decimal place
# If it does, it will round the value to the same number of decimal places as the expected value
# This is to ensure that the values match when comparing the processed output CSV file
# against the expected output CSV file
def check_decimal_values(df_processed_output, df_expected_output):
    # This code iterates over each row and column in the processed output DataFrame.
    for index, row in df_processed_output.iterrows():
        for column in df_processed_output.columns:
            value = row[column]
            # It checks if the value in a cell is a float and has decimal places.
            if isinstance(value, float) and value % 1 != 0:
                # If the value has decimal places, it retrieves the corresponding expected value from the expected output DataFrame.
                expected_value = df_expected_output.loc[index, column]
                # If the expected value is also a float and has decimal places, it determines the number of decimal places.
                if isinstance(expected_value, float) and expected_value % 1 != 0:
                    expected_decimal_places = len(str(expected_value).split(".")[1])
                    # The value in the processed output DataFrame is then rounded to the same number of decimal places as the expected value.
                    # This ensures that the values match when comparing the processed output against the expected output.
                    df_processed_output.loc[index, column] = round(
                        value, expected_decimal_places
                    )

    return df_processed_output


# The output_failures function is responsible for printing the details of failures that
# occurred during the comparison of expected output and processed output. It takes a list of failures
# as input and iterates over each failure. For each failure, it prints the filename with the error,
# the reference (if available), the row and column where the value mismatch occurred, the expected output value,
# and the processed output value.
def output_failures(failures):
    # Print all the failures
    for failure in failures:
        print("\n")
        print(
            "===================================================================================================================="
        )
        print(f"Filename with the error '{failure['file_name']}'.")
        for failure_details in failure["failures"]:
            if "reference" in failure_details:
                print(
                    f"Value mismatch at reference {failure_details['reference']}, row {failure_details['row']} and column {failure_details['col']}."
                )
            elif "RU" in failure_details:
                print(
                    f"Value mismatch at RU {failure_details['RU']}, row {failure_details['row']} and column {failure_details['col']}."
                )
            print(f"Expected output: {failure_details['expected_output']}")
            print(f"Processed output: {failure_details['processed_output']}")
            print("\n")


def compare_dataframes(df_processed_output, df_expected_output, method, file1):
    # Comparing nan values is problematic when using the datatest library
    # so we make all the nan values in the processed and expected output -1
    # so we can easily compare it without being thrown an error when comparing nan values

    # We use -1 to replace nan values because if the expected value is 0 and the processed value is NaN,
    # using fillna(0) would mask this discrepancy, as both values would become 0 after the operation
    # Setting NaN values to -1 (or any other value that you're sure won't appear in your data) is one way to
    # to handle this, as it would allow us to distinguish between actual 0 values and values that were originally NaN
    df_processed_output = df_processed_output.fillna(-1)
    df_expected_output = df_expected_output.fillna(-1)

    # Round the decimal values in the df_processed_output dataframe to the same number of decimal
    # places as the df_expected_output dataframe
    df_processed_output = check_decimal_values(df_processed_output, df_expected_output)

    # Compare the dataframes
    comparison = df_processed_output == df_expected_output

    # This section of code is responsible for comparing the processed output dataframe with the expected output dataframe.
    # It uses the datatest library to perform the comparison.
    # If there are any mismatches between the two dataframes, a ValidationError is raised.
    # The code catches the ValidationError and identifies the locations of the mismatches.
    # It then stores the details of each failure in a list called file_failures.
    # The failure details include the reference, row number, column number, expected output, and processed output.
    # The failures list will be printed later to display all the failures encountered during the comparison.
    file_failure = {}

    try:
        dt.validate(df_processed_output, df_expected_output)
    except dt.ValidationError:
        # Using the NumPy library to find the locations where the comparison variable is false.
        # The resulting indices are stored in the mismatch_locations variable.
        # The tilde (~) is a unary operator in Python that performs a bitwise negation.
        # In this case, it is used to negate the comparison variable.
        # This means that the condition inside np.where() will be true for elements where comparison is false.
        mismatch_locations = np.where(~comparison)
        file_failures = []  # Store the failures for each file

        # This for loop iterates over each pair of row and column indices in the mismatch_locations variable.
        # The mismatch_locations variable contains the indices where the comparison between the processed output
        # and expected output dataframes is false.
        # These indices represent the locations where the values in the two dataframes do not match.
        for row, col in zip(*mismatch_locations):
            # Check the method type to determine the failure details format
            if method == "TCC":
                # Create a failure dictionary with the reference, row number, column number, expected output, and processed output
                failure = {
                    "reference": df_processed_output.loc[row, "reference"],
                    "row": row + 1,
                    "col": col + 1,
                    "expected_output": df_expected_output.iloc[row, col],
                    "processed_output": df_processed_output.iloc[row, col],
                }
            elif method == "TPC":
                # Create a failure dictionary with the RU, row number, column number, expected output, and processed output
                failure = {
                    "RU": df_processed_output.loc[row, "RU"],
                    "row": row + 1,
                    "col": col + 1,
                    "expected_output": df_expected_output.iloc[row, col],
                    "processed_output": df_processed_output.iloc[row, col],
                }
            # Append the failure dictionary to the file_failures list
            file_failures.append(failure)

        # If there are any failures in the file, create a dictionary with the file name and the list of failures
        if len(file_failures) > 0:
            file_failure = {"file_name": file1, "failures": file_failures}
            return file_failure


# This test_values function is used to test the values in the processed output CSV files against the expected output CSV files.
# It uses the parametrize decorator to run the test with different arguments.
# The test_data parameter is a tuple containing the method ("TCC" or "TPC"), the path to the original test data directory,
# and the path to the processed test data directory.
@pytest.mark.parametrize(
    "test_data",
    [
        ("TCC", "tcc_test_data_original/", "tcc_test_data_processed/"),
        ("TPC", "tpc_test_data_original/", "tpc_test_data_processed/"),
    ],
)
def test_values(test_data):
    method, test_data_original_path, test_data_processed_path = test_data

    # Get the list of files in the original test data directory and the processed test data directory
    test_data_original = os.listdir(test_data_original_path)
    test_data_processed = os.listdir(test_data_processed_path)

    failures = []

    # Iterate through each combination of file1 and file2 from test_data_processed and test_data_original
    for file1, file2 in itertools.product(test_data_processed, test_data_original):
        # Check if file2 is an output file and if file1 and file2 have the same name
        if file2.endswith("output.csv") and file1 == file2:
            # Read the processed output CSV file and the expected output CSV file
            df_processed_output = pd.read_csv(test_data_processed_path + file1)
            df_expected_output = pd.read_csv(test_data_original_path + file2)

            # Compare the dataframes and get the failure (if any)
            failure = compare_dataframes(
                df_processed_output, df_expected_output, method, file1
            )
            if failure is not None:
                failures.append(failure)

    # Print the details of the failures
    output_failures(failures)

    # Assert that there are no failures
    assert len(failures) == 0, f"{len(failures)} test(s) failed"
