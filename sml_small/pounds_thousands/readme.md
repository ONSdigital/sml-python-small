# Pounds-Thousands

## Source data

An example of running the method directly and using csv data (in-memory and from files) is provided in [example.py](example.py)

Example input data: (2 csv files)

```
principle_identifier,principle_variable,predicted,auxiliary,upper_limit,lower_limit
q100,50000000,60000,30000,1350,350

identifier,value
q101,500
q102,1000
q103,1500
q104,
```

i.e.
|principle_identifier|principle_variable|predicted|auxiliary|upper_limit|lower_limit|
|---|---|---|---|---|---|
q100|50000000|60000|30000|1350|350

|identifier|value|
|-|-|
q101|500
q102|1000
q103|1500
q104|

## Calling the method

The method has the following interface:

```python
def run(
    principle_identifier: Optional[str],  # Unique identifer e.g. a question code - q500
    principle_variable: float,  # Original response value provided for the 'current' period
    predicted: Optional[float],  # Value used for 'previous' response (Returned/Imputed/Constructed)
    auxiliary: Optional[float],  # Calculated response for the 'previous' period
    upper_limit: float,  # Upper bound of 'error value' threshold
    lower_limit: float,  # Lower bound of 'error value' threshold
    target_variables: List[Target_variable] # identifier/value pairs
)
```

e.g.

```python
output = run(
    principle_identifier = "q234a",
    principle_variable = 50000000,
    predicted = 60000,
    auxiliary = 30000,
    upper_limit = 1350,
    lower_limit = 350,
    target_variables = [
            Target_variable(identifier="q101", value=500),
            Target_variable(identifier="q102", value=1000),
            Target_variable(identifier="q103", value=1500),
            Target_variable(identifier="q104", value=None)]
)
```

## Output

```python
Thousands_output(
    principle_identifier='100',
    principle_final_value=50000.0,
    target_variables=[
        Target_variable(identifier='101', value=0.5),
        Target_variable(identifier='102', value=1.0),
        Target_variable(identifier='103', value=1.5),
        Target_variable(identifier='104', value=None)],
    ratio=833.3333333333334,
    tpc_marker='C',
    error=''
)
```

Alternatively presented: (mixing input and output data for comparisons)

|principle_identifier|principle_variable|predicted|aux|threshold_upper|threshold_lower|TPC_marker|ratio|principle_final_value|linked_question|linked_value|linked_final_value
|---|---|---|---|---|---|---|---|---|---|---|---|
q100|50000000|60000|15000|1350|350|C|1000.0|50000.0|q101|500|0.5
-|-|-|-|-|-|-|-|-|q102|1000|1
-|-|-|-|-|-|-|-|-|q103|1500|1.5
-|-|-|-|-|-|-|-|-|q104||
