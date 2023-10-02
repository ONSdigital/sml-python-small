"""
Example code that uses the pandas wrapper showing examples of using it with each valid method,
currently this includes Totals and Components, and Thousand Pounds Correction

For Copyright information, please see LICENCE.
"""
import pandas as pd

# We import the wrapper function from the pandas_wrapper
from sml_small.utils.pandas_wrapper import wrapper


# Function below is used to read a CSV file from the given
# filepath and return as a DataFrame
def load_csv(filepath):
    df = pd.read_csv(filepath)
    return df


# ---------------------------------------
# Totals and Components usage
# ---------------------------------------
# The code below calls the load_csv function
# with the filename as an argument
input_dataframe_totals_and_components = load_csv(
    "../../tests/editing/totals_and_components/example_data/example_test_data.csv"
)
components = ["comp_1", "comp_2", "comp_3", "comp_4"]

# We call the wrapper function from pandas_wrapper python file
# passing in the required arguments, which in this case are
# column names
totals_and_components_output_columns = [
    "Absolute Difference",
    "Low Percent Threshold",
    "High Percent Threshold",
    "TCC Marker",
    "Final Total",
    "Final Components",
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

# The resulting DataFrame that is stored in the variable test_totals_and_components
# is then saved to a new CSV file
# The index=False argument ensures that the row indices are not written
# to the CSV file
test_totals_and_components.to_csv(
    "../../tests/editing/totals_and_components/example_data/example_test_data_pandas_output.csv",
    index=False,
)
# ---------------------------------------
# Thousand Pounds usage
# ---------------------------------------
input_dataframe_thousand_pounds = load_csv(
    "../../tests/editing/thousand_pounds/example_data/example_test_data.csv"
)
target_variables = ["q42", "q43"]
thousand_pounds_output_columns = [
    "Principal Original Value",
    "Principal Final Value",
    "Target Variables",
    "TPC Ratio",
    "TPC Marker",
]
test_thousand_pounds = wrapper(
    input_dataframe_thousand_pounds,
    "thousand_pounds",
    output_columns=thousand_pounds_output_columns,
    principal_identifier_column="RU",
    principal_variable_column="principal_val",
    target_variables_columns=target_variables,
    upper_limit_column="threshold_upper",
    lower_limit_column="threshold_lower",
    predictive_column="predictive_val",
    auxiliary_column="aux_val",
)
test_thousand_pounds.to_csv(
    "../../tests/editing/thousand_pounds/example_data/example_test_data_pandas_output.csv",
    index=False,
)
