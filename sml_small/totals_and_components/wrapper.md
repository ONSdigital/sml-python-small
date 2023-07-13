# Python Wrapper for the Total and Components Method (T&C)

To view the code of the python wrapper and run it, you can find the `wrapper.py` file within the `totals_and_components` directory.

To run the python wrapper:

```cmd
python wrapper.py
```

or in some cases it maybe

```cmd
python3 wrapper.py
```

in the command line.

## Functionalities the python wrapper offers

### Running T&C method directly using explicitly specified input parameters

We can do this by running the function

<details>

<summary>def invoke_process_with_local_csv()</summary>

```python
# In this function we pass in the in memory test data List[] into the totals_and_components function
def invoke_process_in_memory_data_example():

    # This list is used to keep track of the original data inputted, so we can display this
    # on the command line on a table

    # The input data below once passed into the T&C method should return
    # a TCC Marker of N = No correction required, i.e., the total is equal to the components sum
    # Meaning we have no correction and the method stops with an output written.

    # The input data is here as a list below but this isn't needed to work with the T&C method
    # The List[] data below is used to keep track of the original data to display on the command line
    # in a table format
    data = ["F", "202301", 11, [0, 0, 0, 0], True, 11, "202301", None, 11, None]

    # We pass in the input data to be processed and returned by the T&C method
    result = totals_and_components(
        "F", "202301", 11, [0, 0, 0, 0], True, 11, "202301", None, 11, None
    )

    filter_data(result, data)
```

</details>

### Running T&C method one row at a time using CSV input data held in a file

We can do this by running the function

```python
def invoke_process_with_local_csv()
```

### Running T&C method one row at a time using CSV input data held in-memory file

We can do this by running the function

```python
def invoke_process_with_in_memory_csv()
```

### Additional functions

We also have 2 other functions which aren't essential for the to work with the T&C method but are there to filter the return data and display in the command line in a tabular format.

The `filter_data` function below filters the results returned from T&C method.
This function is used to wrangle the results returned so we can pass the results into the tabulate function to create the table on the command line.

```python
def filter_data()
```

The `display_results` function below is used to display the input data and output data returned from the T&C method in a pretty table format on the command line.

```python
def display_results()
```

### Running the desired function

You can run the desired function by calling the function at the end of the file or uncommenting the function you want to run at the end of the file.

```python
# invoke_process_with_local_csv()
# invoke_process_with_in_memory_csv()
# invoke_process_in_memory_data_example()
invoke_process_in_memory_data_example_2()
```
