# Calling Total and Components Method (T&C) Example and Pandas Wrapper Usage

To view the code of the python `example.py` and run it, you can find the `example.py` file within the `totals_and_components` directory.

## Prerequisites: Python example

In order to run some of the functions in the python `example.py`, you will need to have `tabulate` installed.

Tabulate is used to pretty-print tabular data in python on the command line.

To install `tabulate`:

```python
pip install tabulate
```

To run the python `example.py`:

```cmd
python example.py
```

## Input data examples

### Method 1: Passing list data into the T&C method

The input data below once passed into the T&C method should return a TCC Marker of N = No correction required, i.e., the total is equal to the components sum.

Meaning we have no correction and the method stops with an output written.

```python
# Importing the totals_and_components method from the
# totals_and_components.py file
from totals_and_components import totals_and_components

# The data we are going to pass into the T&C method
# Should return a TCC Marker of S = Method stops. This may be due
# to insufficient data to run the method, or one of the relevant
# zero cases
data = ["F", 11, [0, 0, 0, 0], True, 11, None, 11, None]

# We can the totals_and_components function and pass in our data and
# save the return outputted by the T&C method in the variable result
# We use * to unpack the above list into separate arguments to pass
# into the T&C method
result = totals_and_components(*data)

# The output will be returned as an object.
# You will need to destructure the object to extract the values and
# one way of doing this is using the built-in function vars().
# vars() is used to return the __dict__attribute for the specified
# module, class, instance or any other object with a
# __dict__attribute
print(vars(result))
```

The function *`def invoke_process_in_memory_data_example()`* in the `example.py` file shows how you can pass in a whole dataset stored in a 2D list into the *`totals_and_components`* function,  get the returned result and display it nicely on the command line in a tabular format.

### Method 2: Passing data directly into the T&C method

The input data below once passed into the T&C method should return a TCC Marker of C = Components corrected
data = ["C", 90, [90, 0, 4, 6], False, 90, None, None, 0.1, None]

```python
# Importing the totals_and_components method from the
# totals_and_components.py file
from totals_and_components import totals_and_components

# We can the totals_and_components function and pass in our data and
# save the return outputted by the T&C method in the variable result
# Should return a TCC Marker of C = Components corrected
result = totals_and_components("C", 90, [90, 0, 4, 6], False, 90, None, None, 0.1, None)

# The output will be returned as an object.
# You will need to destructure the object to extract the values and
# one way of doing this is using the built-in function vars().
# vars() is used to return the __dict__attribute for the specified
# module, class, instance or any other object with a
# __dict__attribute
print(vars(result))
```

## Output data examples

Input data example 1: `["F", 11, [0, 0, 0, 0], True, 11, None, 11, None]`

Output data example 1:

```bash
{
    'identifier': 'F',
    'absolute_difference': None,
    'low_percent_threshold': None,
    'high_percent_threshold': None,
    'final_total': '11',
    'final_components': ['0', '0', '0', '0'],
    'tcc_marker': 'S'
}
```

Input data example 2: `["C", 90, [90, 0, 4, 6], False, 90, None, None, 0.1, None]`

Output data example 2:

```bash
{
    'identifier': 'C',
    'absolute_difference': None,
    'low_percent_threshold': '90.0',
    'high_percent_threshold': '110.0',
    'final_total': '90',
    'final_components': ['81.0', '0', '3.60', '5.40'],
    'tcc_marker': 'C'
}
```

## Functionalities the python `example.py` offers

### Running T&C method directly using explicitly specified input parameters

#### Method 1

```python
def invoke_process_in_memory_data_example()
```

In this function we pass in the data directly into the *`totals_and_components`* function.

The returned result data is then passed into the *`filter_data`* function which is used to wrangle the results returned so we can pass the results into the *`display_results`* which is a function used to present the results on the command line in a tabular format.

#### Method 2

```python
def invoke_process_in_memory_data_example_2()
```

In this function we pass a dataset stored in a 2D List[] into the *`totals_and_components`* function by unpacking it into separate arguments.

The returned result data is then passed into the *`filter_data`* function which is used to wrangle the results returned so we can pass the results into the *`display_results`* which is a function used to present the results on the command line in a tabular format.

*`filter_data` and `display_results` function are not essential functions needed to work with the T&C method itself.*

### Running T&C method one row at a time using CSV input data held in a file

```python
def invoke_process_with_local_csv()
```

In this function we read the CSV file and extract the input data and pass into the *`totals_and_components`* function.

Write the results returned by the T&C method into the CSV file.

### Running T&C method one row at a time using CSV input data held in-memory file

```python
def invoke_process_with_in_memory_csv()
```

In this function we read the in memory CSV data and extract the input data and pass into the *`totals_and_components`* function.

Write the results returned by the T&C method into the CSV file.

### Additional functions

We also have 2 other functions which aren't essential and not needed to work with the T&C method but are there to filter the return data and display the returned results in the command line in a tabular format.

The *`filter_data`* function below filters the results returned from T&C method.
This function is used to wrangle the results returned so we can pass the results into the tabulate function to create the table on the command line.

```python
def filter_data()
```

The *`display_results`* function below is used to display the input data and output data returned from the T&C method in a pretty table/ tabular format on the command line.

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

## Pandas Wrapper

To view the code of the pandas wrapper you can find the `pandas_wrapper.py` file within the `utils` directory.

### Prerequisites: Pandas Wrapper

In order to run some of the functions in the python `pandas_wrapper.py`, you will need to have `pandas` and `numpy` installed.

To install `pandas`:

```python
pip install pandas
```

To install `numpy`:

```python
pip install numpy
```

## Pandas Wrapper Usage

- You will have to create a new python file importing in the `pandas_wrapper.py`.
- Where you will have to write functions to read a CSV file and pass in the data as a DataFrame into the *`wrapper`* function from the `pandas_wrapper.py` file.

We have an example of how to do this in the `pandas_example.py` file within the `utils` directory.
