# Python Wrapper for the Total and Components Method (T&C)

To view the code of the python wrapper and run it, you can find the `wrapper.py` file within the totals_and_components directory.

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

```python
def invoke_process_in_memory_data_example()
```

The function below shows...

```python
def invoke_process_in_memory_data_example_2()
```

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

```python
def filter_data()
```

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
