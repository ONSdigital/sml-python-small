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

## Input data examples

### Method 1: Passing list data into the totals_and_components

The input data below once passed into the T&C method should return a TCC Marker of N = No correction required, i.e., the total is equal to the components sum.

Meaning we have no correction and the method stops with an output written.

```python
# Importing the totals_and_components method from the totals_and_components.py file
from totals_and_components import totals_and_components

# The data we are going to pass into the T&C method
data = ["F", "202301", 11, [0, 0, 0, 0], True, 11, "202301", None, 11, None]

# We can the totals_and_components function and pass in our data and save the return outputted by the T&C method in the variable result
# We use * to unpack the above list into separate arguments to pass to the T&C method
result = totals_and_components(*data)
```

The function `def invoke_process_in_memory_data_example()` in the `wrapper.py` file shows how you can pass in a whole dataset stored in a 2D list into the `totals_and_components` function,  get the returned result and display it nicely on the command line in a tabular format.

### Method 2: Passing data directly into the totals_and_components

The input data below once passed into the T&C method should return a TCC Marker of C = Components corrected
data = ["C", "202301", 90, [90, 0, 4, 6], False, 90, "202301", None, None, 0.1]

```python
# Importing the totals_and_components method from the totals_and_components.py file
from totals_and_components import totals_and_components

# We can the totals_and_components function and pass in our data and save the return outputted by the T&C method in the variable result
result = totals_and_components("C", "202301", 90, [90, 0, 4, 6], False, 90, "202301", None, None, 0.1)
```

## Output data examples

Write something here

## Functionalities the python wrapper offers

### Running T&C method directly using explicitly specified input parameters

#### Method 1

```python
def invoke_process_in_memory_data_example()
```

In this function we pass in the data directly into the `totals_and_components` function.

The returned result data is then passed into the `filter_data` function which is used to wrangle the results returned so we can pass the results into the `display_results` which is a function used to present the results on the command line in a tabular format.

#### Method 2

```python
def invoke_process_in_memory_data_example_2()
```

In this function we pass a dataset stored in a 2D List[] into the `totals_and_components` function by unpacking it into separate arguments.

The returned result data is then passed into the `filter_data` function which is used to wrangle the results returned so we can pass the results into the `display_results` which is a function used to present the results on the command line in a tabular format.

*`filter_data` and `display_results` function are not essential functions needed to work with the T&C method itself.*

### Running T&C method one row at a time using CSV input data held in a file

```python
def invoke_process_with_local_csv()
```

In this function we read the CSV file and extract the input data and pass into the `totals_and_components` function.

Write the results returned by the T&C method into the CSV file.

### Running T&C method one row at a time using CSV input data held in-memory file

```python
def invoke_process_with_in_memory_csv()
```

In this function we read the in memory CSV data and extract the input data and pass into the `totals_and_components` function.

Write the results returned by the T&C method into the CSV file.

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
