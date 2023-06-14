# In this python file, we are calling the T&C method and passing in the
# test data to be processed by the T&C method and return the result to
# be displayed in a formatted table on the command line

# Importing the totals_and_components method from the totals_and_components.py file
from totals_and_components import totals_and_components, Component_list

# Importing tabulate function from tabulate to pretty print the input and output results
# from the T&C method in a tabular format
# This import isn't necessary to work with the T&C method
from tabulate import tabulate

test_data = [
    # [
    #   "A",
    #   "202301",
    #   1625,
    #   [Component_list(632, None), Component_list(732, None), Component_list(99, None), Component_list(162, None)],
    #   True,
    #   1625,
    #   "202301",
    #   None,
    #   11,
    #   None
    # ],
    # [
    #   "B",
    #   "202301",
    #   10817,
    #   [Component_list(9201, None), Component_list(866, None), Component_list(632, None), Component_list(112, None)],
    #   True,
    #   10817,
    #   "202301",
    #   None,
    #   11,
    #   None
    # ],
    [
        "C",
        "202301",
        90,
        [
            Component_list(90, None),
            Component_list(0, None),
            Component_list(4, None),
            Component_list(6, None),
        ],
        False,
        90,
        "202301",
        None,
        None,
        0.1,
    ],
    # [
    #     "X",
    #     "202301",
    #     41,
    #     [
    #         Component_list(10, None),
    #         Component_list(10, None),
    #         Component_list(10, None),
    #         Component_list(10, None),
    #     ],
    #     False,
    #     41,
    #     "202301",
    #     None,
    #     None,
    #     None,
    # ],
    # [
    #   "D",
    #   "202301",
    #   1964,
    #   [Component_list(632, None), Component_list(732, None), Component_list(99, None), Component_list(162, None)],
    #   True,
    #   1964,
    #   "202301",
    #   None,
    #   25,
    #   0.1
    # ],
    # [
    #   "E",
    #   "202301",
    #   306,
    #   [Component_list(240, None), Component_list(0, None), Component_list(30, None), Component_list(10, None)],
    #   True,
    #   306,
    #   "202301",
    #   None,
    #   25,
    #   0.1
    # ],
    # [
    #   "F",
    #   "202301",
    #   11,
    #   [Component_list(0, None), Component_list(0, None), Component_list(0, None), Component_list(0, None)],
    #   True,
    #   11,
    #   "202301",
    #   None,
    #   11,
    #   None
    # ],
]


# In this function we pass in the in memory test data into the totals_and_components function
def invoke_process_in_memory_data_example():

    # This list is used to keep track of the original data inputted, so we can display this
    # on the command line on a table

    # The input data below once passed into the T&C method should return
    # a TCC Marker of N = No correction required, i.e., the total is equal to the components sum
    # Meaning we have no correction and the method stops with an output written.
    data = [
        "A",
        "202301",
        1625,
        [
            Component_list(632, None),
            Component_list(732, None),
            Component_list(99, None),
            Component_list(162, None),
        ],
        True,
        1625,
        "202301",
        None,
        11,
        None,
    ]

    # We pass in the input data to be processed and returned by the T&C method
    result = totals_and_components(
        "A",
        "202301",
        1625,
        [
            Component_list(632, None),
            Component_list(732, None),
            Component_list(99, None),
            Component_list(162, None),
        ],
        True,
        1625,
        "202301",
        None,
        11,
        None,
    )

    filter_data(result, data)


# In this example we can pass in the data as a list and unpack it into separate arguments
def invoke_process_in_memory_data_example_2():

    # The input data below once passed into the T&C method should return
    # a TCC Marker of Components corrected
    data = [
        "C",
        "202301",
        90,
        [
            Component_list(90, None),
            Component_list(0, None),
            Component_list(4, None),
            Component_list(6, None),
        ],
        False,
        90,
        "202301",
        None,
        None,
        0.1,
    ]

    # We use * to unpack the above list into separate arguments
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
        result.period,
        result.absolute_difference,
        result.low_percent_threshold,
        result.high_percent_threshold,
        result.final_total,
        result.tcc_marker,
    ]

    # We pop the components object from the original_data list as we wouldn't be needing it
    original_data.pop(3)

    # We extract the original_value from the components from the final_components list returned from
    # the T&C method
    original_data_comp = []
    for component in result.final_components:
        original_data_comp.append(component.original_value)

    # We extract the final_value from the components from the final_components list returned from
    # the T&C method
    new_result_comp = []
    for component in result.final_components:
        new_result_comp.append(component.final_value)

    # We get all the list data above and amend that to a 2D list to be passed on to the
    # display_results function
    results = [original_data, new_result, original_data_comp, new_result_comp]
    display_results(results)


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
            "Period",
            "Total",
            "Amend Total",
            "Predictive",
            "Predictive Period",
            "Auxiliary Variable",
            "Absolute Difference Threshold",
            "Percentage Difference Threshold",
        ],
        "Final Results": [
            "Identifier",
            "Period",
            "Absolute Difference",
            "Low Percent Threshold",
            "High Percent Threshold",
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


# You can run the functions invoke_process_in_memory_data_example or invoke_process_in_memory_data_example_2 below
invoke_process_in_memory_data_example_2()
