# Thousand-Pounds

## Source data

An example of running the method directly and using csv data (in-memory and from files) is provided in [example.py](example.py)

Example input data: (2 csv files)

```bash
unique_identifier,principal_variable,predictive,auxiliary,upper_limit,lower_limit,precision
12340000001-201409-q100,50000000,60000,30000,1350,350,2

identifier,value
q101,500
q102,1000
q103,1500
q104,
```

i.e.

|unique_identifier|principal_variable|predictive|auxiliary|upper_limit|lower_limit|precision
|---|---|---|---|---|---|---|
12340000001-201409-q100|50000000|60000|30000|1350|350|2

|identifier| value
|---|----|
q101| 500
q102| 1000
q103| 1500
q104|

## Calling the method

The method has the following interface:

```python
def thousand_pounds(
    unique_identifier: Optional[str],  # Unique identifier e.g. a question
    # code/ruref/period/id/combination of all of these
    principal_variable: float,  # Original response value provided for
    # the 'current' period
    predictive: Optional[float],  # Value used for 'previous'
    # response (Returned/Imputed/Constructed)
    auxiliary: Optional[float],  # Calculated response for the
    # 'previous' period
    upper_limit: float,  # Upper bound of 'error value' threshold
    lower_limit: float,  # Lower bound of 'error value' threshold
    target_variables: List[TargetVariable], # identifier/value pairs
    precision: Optional[int],  #Precision is used by the decimal package to ensure a specified accuracy
    # used throughout method processing
)
```

e.g.

```python
from thousand_pounds import thousand_pounds

output = thousand_pounds(
    unique_identifier = "12340000001-201409-q100",
    principal_variable = "50000000",
    predictive = "60000",
    auxiliary = "30000",
    upper_limit = "1350",
    lower_limit = "350",
    target_variables = {"q101": 500,
                        "q102": 1000,
                        "q103": 1500,
                        "q104": None},
    precision = 1
)
```

## Output

```python
ThousandPoundsOutput(
    principal_identifier='12340000001-201409-q100',
    principal_adjusted_value="50000.0",
    target_variables=[
        TargetVariable(identifier='101', original_value="500", adjusted_value="0.5"),
        TargetVariable(identifier='102', original_value="1000", adjusted_value="1.0"),
        TargetVariable(identifier='103', original_value="1500", adjusted_value="1.5"),
        TargetVariable(identifier='104', original_value=None, adjusted_value=None)],
    tpc_ratio="833.3",
    tpc_marker='C',
    error_description=''
)
```

Alternatively presented: (mixing input and output data for comparisons)

| unique_identifier       |principal_variable|predictive|aux|threshold_upper|threshold_lower| tpc_marker | tpc_ratio |principal_adjusted_value|target_variable|target_adjusted_value
|-------------------------|---|---|---|---|---|------------|-----------|---|---|---|
 12340000001-201409-q100 |50000000|60000|15000|1350|350| C          | 1000.0    |50000.0|q101|0.5
 12340000001-201409-q100 |-|-|-|-|-| -          | -         |-|q102|1
 12340000001-201409-q100 |-|-|-|-|-| -          | -         |-|q103|1.5
 12340000001-201409-q100 |-|-|-|-|-| -          | -         |-|q104||

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
