# Thousand-Pounds

## Source data

An example of running the method directly and using csv data (in-memory and from files) is provided in [example.py](example.py)

Example input data: (2 csv files)

```
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
    unique_identifier: Optional[str],  # Unique identifer e.g. a question code/ruref/period/id/combination of all of thse
    principal_variable: float,  # Original response value provided for the 'current' period
    predictive: Optional[float],  # Value used for 'previous' response (Returned/Imputed/Constructed)
    auxiliary: Optional[float],  # Calculated response for the 'previous' period
    upper_limit: float,  # Upper bound of 'error value' threshold
    lower_limit: float,  # Lower bound of 'error value' threshold
    target_variables: List[Target_variable], # identifier/value pairs
    precision: Optional[int],  #Precision is used by the decimal package to ensure a specified accuracy
    # used throughout method processing
)
```

e.g.

```python
output = thousand_pounds(
    unique_identifier = "12340000001-201409-q100",
    principal_variable = "50000000",
    predictive = "60000",
    auxiliary = "30000",
    upper_limit = "1350",
    lower_limit = "350",
    target_variables = [
            Target_variable(identifier="q101", original_value="500"),
            Target_variable(identifier="q102", original_value="1000"),
            Target_variable(identifier="q103", original_value="1500"),
            Target_variable(identifier="q104", original_value=None)],
    precision = 1
)
```

## Output

```python
Thousands_output(
    principal_identifier='12340000001-201409-q100',
    principal_adjusted_value="50000.0",
    target_variables=[
        Target_variable(identifier='101', original_value="500", adjusted_value="0.5"),
        Target_variable(identifier='102', original_value="1000", adjusted_value="1.0"),
        Target_variable(identifier='103', original_value="1500", adjusted_value="1.5"),
        Target_variable(identifier='104', original_value=None, adjusted_value=None)],
    tpc_ratio="833.3",
    tpc_marker='C',
    error_description=''
)
```

Alternatively presented: (mixing input and output data for comparisons)

| unique_identifier       |principal_variable|predictive|aux|threshold_upper|threshold_lower|TPC_marker|ratio|principal_adjusted_value|target_variable|target_original_value|target_adjusted_value
|-------------------------|---|---|---|---|---|---|---|---|---|---|---|
 12340000001-201409-q100 |50000000|60000|15000|1350|350|C|1000.0|50000.0|q101|500|0.5
 12340000001-201409-q100 |-|-|-|-|-|-|-|-|q102|1000|1
 12340000001-201409-q100 |-|-|-|-|-|-|-|-|q103|1500|1.5
 12340000001-201409-q100 |-|-|-|-|-|-|-|-|q104||
