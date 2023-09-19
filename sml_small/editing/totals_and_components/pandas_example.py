"""
Example code that uses the pandas wrapper with the Totals and Components method.

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


# The code below calls the load_csv function
# with the filename as an argument
input_dataframe = load_csv(
    "../../../tests/editing/totals_and_components/example_data/example_test_data.csv"
)
components = ["comp_1", "comp_2", "comp_3", "comp_4"]

# We call the wrapper function from pandas_wrapper python file
# passing in the required arguments, which in this case are
# column names
test = wrapper(
    input_dataframe,
    'totals_and_components',
    unique_identifier_column="reference",
    total_column="total",
    components_list_columns=components,
    amend_total_column="amend_total",
    predictive_column="predictive",
    auxiliary_column="auxiliary",
    absolute_threshold_column="abs_threshold",
    percentage_threshold_column="perc_threshold",
)

# The resulting DataFrame that is stored in the variable test
# is then saved to a new CSV file
# The index=False argument ensures that the row indices are not written
# to the CSV file
test.to_csv(
    "../../../tests/editing/totals_and_components/example_data/example_test_data_pandas_output.csv",
    index=False,
)
