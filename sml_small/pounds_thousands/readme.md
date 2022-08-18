# Pounds-Thousands

### Assumptions

* All input datasets use dataclasses to provide structure
* All input/output datasets are immutable upon creation
* Missing/null values are not adjusted (they are placed in the adjusted field 'as-is')
* Uses built-in python libraries only
* Assumes that all processing can be dealth with 'in-memory' and output is provided as a single dataset

### Input Dataset

The following data is required by the method:

* Primary Question Identifier (primary question)
* Principal Variable (current value)
* Principle valid variable (previous value)
* Principle predictive variable value (predicted value)
* Principle Auxilliary varible (aux_value):
* Upper limit (threshold_upper)
* Lower limit (threshold_lower)
* Target variables
    This is a list of questions and responses that are linked to the Primary Question Identifier

The structure is as follows:

```python
@dataclass(frozen=True)
class Thousands_config:
    primary_question: str             # Question identifer
    current_value: Optional[float]    # Original response value provided for the 'current' period
    previous_value: Optional[float]   # Original cleared/valid response from the 'previous' period
    predicted_value: Optional[float]  # Imputed/Constructed response for the 'previous' period
    aux_value: Optional[float]        # Calculated response for the 'previous' period
    threshold_upper: float            # Upper bound of 'error value' threshold
    threshold_lower: float            # Lower bound of 'error value' threshold
    linked_questions: list[Response]  # All questions and responses associated with primary question

@dataclass(frozen=True)
class Response:
    question: str              # Question identifer e.g. a question code - q500
    response: Optional[float]  # Original response value provided```
```

### Output Dataset

The following data is output by the method:

```python
@dataclass(frozen=True)
class Thousands_output:
    question: str                    # Question identifer e.g. a question code - q500
    original_value: Optional[float]  # Original response value provided
    adjusted_value: Optional[float]  # Updated/Adjusted response value
    is_adjusted: Optional[bool]      # Flag to indicate whether adjustment took place

```

### Running the method

An example of running the method using csv data is provided in `example.py`.

Example input data:

|primary_question|current_value|previous_value|predicted|aux|threshold_upper|threshold_lower|
|---|---|---|---|---|---|---|
100|50000000|60000|30000|15000|1350|350
200|60000000||60000|15000|1350|350
300|70000000|||70000|1350|350
400|80000000|||5500|1350|350
500||60000|30000|15000|1350|350
600|0|80000|50000|15100|1350|350
700|12345||||1350|250
|||||0|0

|primary_question|question|response|
|-|-|-|
100|101|500
100|102|1000
100|103|1500
100|104|
500|510|6000
500|520|1200
600|650|1234
700|7a|456
700|7b|789"""

This produces the following output:

```
Primary question: 100 -- Formula: 833.3333333333334 = 50000000.0 / 60000.0
Primary question: 200 -- Formula: 1000.0 = 60000000.0 / 60000.0
Primary question: 300 -- Formula: 1000.0 = 70000000.0 / 70000.0
Primary question: 400 -- Formula: 14545.454545454546 = 80000000.0 / 5500.0
Primary question: 600 -- Formula: 0.0 = 0.0 / 80000.0
[Thousands_output(question='100', original_value=50000000.0, adjusted_value=50000.0, is_adjusted=True),
 Thousands_output(question='101', original_value=500.0, adjusted_value=0.5, is_adjusted=True),
 Thousands_output(question='102', original_value=1000.0, adjusted_value=1.0, is_adjusted=True),
 Thousands_output(question='103', original_value=1500.0, adjusted_value=1.5, is_adjusted=True),
 Thousands_output(question='104', original_value=None, adjusted_value=None, is_adjusted=True),
 Thousands_output(question='200', original_value=60000000.0, adjusted_value=60000.0, is_adjusted=True),
 Thousands_output(question='300', original_value=70000000.0, adjusted_value=70000.0, is_adjusted=True),
 Thousands_output(question='400', original_value=80000000.0, adjusted_value=80000000.0, is_adjusted=False),
 Thousands_output(question='500', original_value=None, adjusted_value=None, is_adjusted=None),
 Thousands_output(question='510', original_value=6000.0, adjusted_value=6000.0, is_adjusted=None),
 Thousands_output(question='520', original_value=1200.0, adjusted_value=1200.0, is_adjusted=None),
 Thousands_output(question='600', original_value=0.0, adjusted_value=0.0, is_adjusted=False),
 Thousands_output(question='650', original_value=1234.0, adjusted_value=1234.0, is_adjusted=False),
 Thousands_output(question='700', original_value=12345.0, adjusted_value=12345.0, is_adjusted=None),
 Thousands_output(question='7a', original_value=456.0, adjusted_value=456.0, is_adjusted=None),
 Thousands_output(question='7b', original_value=789.0, adjusted_value=789.0, is_adjusted=None),
 Thousands_output(question='', original_value=None, adjusted_value=None, is_adjusted=None)]
```

Alternatively presented:

|question|original_value|adjusted_value|is_adjusted|
|-|-|-|-|
|100|50000000.0|50000.0|True|
|101|500.0|0.5|True|
|102|1000.0|1.0|True|
|103|1500.0|1.5|True|
|104|None|None|True|
|200|60000000.0|60000.0|True|
|300|70000000.0|70000.0|True|
|400|80000000.0|80000000.0|False|
|500|None|None|None|
|510|6000.0|6000.0|None|
|520|1200.0|1200.0|None|
|600|0.0|0.0|False|
|650|1234.0|1234.0|False|
|700|12345.0|12345.0|None|
|7a|456.0|456.0|None|
|7b|789.0|789.0|None|
||None|None|None|

For documentation, please refer to the method-specific documentation in the
docs directory.
