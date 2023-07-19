# In this python file, we are calling the T&C method and passing in the
# test data to be processed by the T&C method and return the result to
# be displayed in a formatted table on the command line

# Importing the totals_and_components method from the totals_and_components.py file
from totals_and_components import totals_and_components
import csv

# Importing tabulate function from tabulate to pretty print the input and output results
# from the T&C method in a tabular format
# This import isn't necessary to work with the T&C method
from tabulate import tabulate

test_data = [
    # The input data below once passed into the T&C method should return
    # a TCC Marker of N = No correction required, i.e., the total is equal to the components sum
    # Meaning we have no correction and the method stops with an output written
    [
      "A",
      1625,
      [632, 732, 99, 162],
      True,
      1625,
      None,
      11,
      None    
    ],
    # Should return a TCC Marker of T = Totals corrected
    [
      "B",
      10817,
      [9201, 866, 632, 112],
      True,
      10817,
      None,
      11,
      None
    ],
    # Should return a TCC Marker of C = Components corrected
    [
        "C",
        90,
        [90, 0, 4, 6],
        False,
        90,
        None,
        None,
        0.1,
        2,
    ],
    # Should return a TCC Marker of M = Manual editing required
    # This marker will identify contributors where the discrepancy 
    # between the total and component is deemed too large for automatic correction
    [
      "D",
      1964,
      [632, 732, 99, 162],
      True,
      1964,
      None,
      25,
      0.1,
      None,
    ],
    # Should return a TCC Marker of T = Totals corrected
    [
      "E",
      306,
      [240, 0, 30, 10],
      True,
      306,
      None,
      25,
      0.1,
      None
    ],
    # Should return a TCC Marker of S = Method stops. This may be due
    # to insufficient data to run the method, or one of the relevant zero cases
    [
      "F",
      11,
      [0, 0, 0, 0],
      True,
      11,
      None,
      11,
      None
    ],
]


# In this function we pass in the test data directly into the totals_and_components function
def invoke_process_in_memory_data_example():

    # This list is used to keep track of the original data inputted, so we can display this
    # on the command line on a table

    # The input data below once passed into the T&C method should return
    # a TCC Marker of N = No correction required, i.e., the total is equal to the components sum
    # Meaning we have no correction and the method stops with an output written

    # The input data is here as a list below but this isn't needed to work with the T&C method
    # The List[] data below is used to keep track of the original data to display on the command line
    # in a table format
    data = [
        "A",
        1625,
        [632, 732, 99, 162],
        True,
        1625,
        None,
        11,
        None    
    ]

    # We pass in the input data to be processed and returned by the T&C method
    result = totals_and_components(
        "A",
        1625,
        [632, 732, 99, 162],
        True,
        1625,
        None,
        11,
        None
    )

    filter_data(result, data)


# In this example we pass a dataset stored in a 2D List[] into the T&C method by unpacking it into separate arguments
def invoke_process_in_memory_data_example_2():

    # The input data below once passed into the T&C method should return
    # a TCC Marker of C = Components corrected
    # data = [
    #     "C",
    #     "202301",
    #     90,
    #     [90, 0, 4, 6],
    #     False,
    #     90,
    #     "202301",
    #     None,
    #     None,
    #     0.1
    # ]

    # We use * to unpack the above list into separate arguments to pass into the T&C method
    for data in test_data:
        result = totals_and_components(*data)
        filter_data(result, data)


# The two functions below are solely used to create a pretty table on the command line
# to display the data in a nice format/ table
# They aren't essential to work with the T&C method

# Filter the results returned from T&C method
# This function is used to wrangle the results returned so we can pass the results
# into the tabulate function to create the table on the command line
def filter_data(result, original_data):
    """
    Formats the result we get back from the T&C method into a table format
    to be viewed on the command line.

    :param result: The processed data we get back once we pass the input data to the T&C method.
    :type result: Object[Totals_and_Components_Output]
    :param original_data: In this case the original data is the input data we hold in memory.
    :type original_data: 2D List
    """

    # Once we get the result/ T&C output object, we take the values and convert
    # it to a list
    new_result = [
        result.identifier,
        result.absolute_difference,
        result.low_percent_threshold,
        result.high_percent_threshold,
        result.precision,
        result.final_total,
        result.tcc_marker,
    ]

    # We extract the components from the input data so we can use it later on to display
    # it on the command line in a table format
    original_data_comp = original_data[2]

    original_data.pop(2)

    # We extract the components from the results data returned from the so we can use it
    # the T&C method, so we can later on to display on the command line
    # it on the command line in a table format
    new_result_comp = result.final_components

    # We get all the list data above and amend that to a 2D list to be passed on to the
    # display_results function
    results = [original_data, new_result, original_data_comp, new_result_comp]
    display_results(results)


# Function below is not needed to work with the T&C method
# This is solely for displaying the input and output data from the T&C method
# in a pretty table format on the command line

# This function is used to display the input data and output data returned from the
# T&C method in a pretty table format on the command line
def display_results(results):
    """
    This function is used to display the results on the command line in a table format,
    that came back from the T&C method.

    :param results: Contains the original data inputted, results that came back from the T&C method,
    components data of original inputted data and components of the results that came back from the T&C method.
    :type results: A 2D List
    """
    # Headers to be passed into the tabulate function for the input and output tables
    headers = {
        "Original Input": [
            "Identifier",
            "Total",
            "Amend Total",
            "Predictive",
            "Auxiliary Variable",
            "Absolute Difference Threshold",
            "Percentage Difference Threshold",
            "Precision",
        ],
        "Final Results": [
            "Identifier",
            "Absolute Difference",
            "Low Percent Threshold",
            "High Percent Threshold",
            "Precision",
            "Final Total",
            "TCC Marker",
        ],
        "Original Input Components": [
            "Original Comp 1",
            "Original Comp 2",
            "Original Comp 3",
            "Original Comp 4",
        ],
        "Final Results Components": [
            "Final Comp 1",
            "Final Comp 2",
            "Final Comp 3",
            "Final Comp 4",
        ],
    }

    print("\n")

    # The for loop iterates through the headers and results simultaneously and passes in the results data
    # and table headers into the tabulate function so the tables can be created on the command line and
    # then displayed
    # zip function is used here to to iterate through the dictionary headers and the results list simultaneously
    for header, result in zip(headers, results):
        title = header
        header = headers[header]

        table = [result]
        print(title)
        print("==========================")
        print(
            tabulate(
                table,
                headers=header,
                floatfmt="",
            )
        )
        print("\n")

# In this function we read the CSV file and extract the input data and pass into the totals_and_components function.
# Write the results returned by the T&C method into the CSV file.
def invoke_process_with_local_csv():
    # Read the CSV file and extract the input data and pass into the
    # T&C method
    results = {}
    with open("TCC_test_data_demo.csv", mode="r") as csv_file:
        csv_reader = csv.DictReader(csv_file)
        for row in csv_reader:
            print("Data type:::::::", type(row["comp_1"]))
            input_data = [
                (row["reference"]),
                (row["total"]),
                [
                    (row["comp_1"]),
                    (row["comp_2"]),
                    (row["comp_3"]),
                    (row["comp_4"]),
                ],
                True if not row["amend_total"] == "FALSE" else False,
                (row["predictive"]),
                None if not row["auxiliary"] else (row["auxiliary"]),
                None if not row["abs_threshold"] else (row["abs_threshold"]),
                None if not row["perc_threshold"] else (row["perc_threshold"]),
            ]

            result = totals_and_components(*input_data)

            new_result = {
                result.identifier: {
                    "absolute_difference": result.absolute_difference,
                    "low_percent_threshold": result.low_percent_threshold,
                    "high_percent_threshold": result.high_percent_threshold,
                    "final_total": result.final_total,
                    "tcc_marker": result.tcc_marker,
                }
            }

            print(new_result)

            new_result_comp = result.final_components
            new_result[result.identifier]["comp"] = new_result_comp

            results.update(new_result)

    # Write the results returned by the T&C into the CSV file
    with open("TCC_test_data_demo_processed.csv", mode="w") as csv_file:
        field_names = [
            "reference",
            # "total",
            # "comp_1"
            # "comp_2",
            # "comp_3",
            # "comp_4",
            # "comp_sum",
            # "amend_total",
            # "predictive",
            # "auxiliary",
            # "abs_threshold",
            "abs_diff",
            "perc_low",
            "perc_high",
            "TCC_marker",
            "final_total",
            "final_comp_1",
            "final_comp_2",
            "final_comp_3",
            "final_comp_4",
        ]

        writer = csv.DictWriter(csv_file, fieldnames=field_names, extrasaction="ignore")

        writer.writeheader()
        for identifier in results:
            print(results[identifier])
            writer.writerow(
                {
                    "reference": identifier,
                    "abs_diff": results[identifier]["absolute_difference"],
                    "perc_low": results[identifier]["low_percent_threshold"],
                    "perc_high": results[identifier]["high_percent_threshold"],
                    "final_total": results[identifier]["final_total"],
                    "final_comp_1": results[identifier]["comp"][0],
                    "final_comp_2": results[identifier]["comp"][1],
                    "final_comp_3": results[identifier]["comp"][2],
                    "final_comp_4": results[identifier]["comp"][3],
                    "TCC_marker": results[identifier]["tcc_marker"],
                }
            )

# In this function we read the CSV file and extract the input data and pass into the totals_and_components function.
# Write the results returned by the T&C method into the CSV file.
def invoke_process_with_in_memory_csv():
    # Read the CSV file and extract the input data and pass into the
    # T&C method
    in_memory_csv_data = """reference,total,comp_1,comp_2,comp_3,comp_4,amend_total,predictive,auxiliary,abs_threshold,perc_threshold
A,1625,632,732,99,162,TRUE,1625,,11,,,"""  # noqa: E501

    csv_reader = csv.DictReader(in_memory_csv_data.splitlines())
    print("CSV reader", csv_reader)

    results = {}
    for row in csv_reader:
        input_data = [
            (row["reference"]),
            (row["total"]),
            [
                (row["comp_1"]),
                (row["comp_2"]),
                (row["comp_3"]),
                (row["comp_4"]),
            ],
            True if not row["amend_total"] == "FALSE" else False,
            (row["predictive"]),
            None if not row["auxiliary"] else (row["auxiliary"]),
            None if not row["abs_threshold"] else (row["abs_threshold"]),
            None if not row["perc_threshold"] else (row["perc_threshold"]),
        ]

        result = totals_and_components(*input_data)

        new_result = {
            result.identifier: {
                "absolute_difference": result.absolute_difference,
                "low_percent_threshold": result.low_percent_threshold,
                "high_percent_threshold": result.high_percent_threshold,
                "final_total": result.final_total,
                "tcc_marker": result.tcc_marker,
            }
        }

        new_result_comp = result.final_components
        new_result[result.identifier]["comp"] = new_result_comp

        results.update(new_result)
    print(results)

    # Write the results returned by the T&C into the CSV file
    with open("TCC_test_data_demo_processed_in_memory.csv", mode="w") as csv_file:
        field_names = [
            "reference",
            # "total",
            # "comp_1"
            # "comp_2",
            # "comp_3",
            # "comp_4",
            # "comp_sum",
            # "amend_total",
            # "predictive",
            # "auxiliary",
            # "abs_threshold",
            "abs_diff",
            "perc_low",
            "perc_high",
            "TCC_marker",
            "final_total",
            "final_comp_1",
            "final_comp_2",
            "final_comp_3",
            "final_comp_4",
        ]

        writer = csv.DictWriter(csv_file, fieldnames=field_names, extrasaction="ignore")

        writer.writeheader()
        for identifier in results:
            writer.writerow(
                {
                    "reference": identifier,
                    "abs_diff": results[identifier]["absolute_difference"],
                    "perc_low": results[identifier]["low_percent_threshold"],
                    "perc_high": results[identifier]["high_percent_threshold"],
                    "final_total": results[identifier]["final_total"],
                    "final_comp_1": results[identifier]["comp"][0],
                    "final_comp_2": results[identifier]["comp"][1],
                    "final_comp_3": results[identifier]["comp"][2],
                    "final_comp_4": results[identifier]["comp"][3],
                    "TCC_marker": results[identifier]["tcc_marker"],
                }
            )


# You can run the functions invoke_process_in_memory_data_example or invoke_process_in_memory_data_example_2 below
# invoke_process_with_local_csv()
invoke_process_with_in_memory_csv()
# invoke_process_in_memory_data_example()
# invoke_process_in_memory_data_example_2()
