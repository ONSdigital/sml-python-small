Method specification
====================

* [SML](https://github.com/ONSdigital/Statistical-Method-Specifications/blob/thousand_pound/thousand_pounds_correction.md)

Overall method
=============

This process determines whether a given value is too large by a factor of ~1000. If so, the value is correct to be smaller, and any accompanying values are also adjusted accordingly.

* Dataclasses are used to provide structure where required
* All dataclass datasets are immutable upon creation
* Missing/null values are not adjusted (they are placed in the output dataset 'as-is' regardless of calculations)
* Uses built-in python libraries only
* Assumes that all processing can be dealt with 'in-memory' and output is provided as single dataset
* Errors are caught internally within the method and are converted into managed output errors (TPC Marker of "E")

Inputs
------

The method is to be provided at least one of the two values: predicted (response/imputed/constructed)

* **principle_identifier**: *(String)* - *Optional* - Unique identifer e.g. a question code - q500
* **principle_variable**: *(Float)* - Numeric value we are verifying
* **predicted**: *(Float)* - *Optional* - Numeric value used for comparison. A previous 'valid' value (i.e. Returned/Imputed/Constructed)
* **auxiliary**: *(Float)* - *Optional* - Alternative numeric` value used when a predicted value is not available
* **upper_limit**: *(Float)* - Upper bound of 'error value' threshold
* **lower_limit**: *(Float)* - Lower bound of 'error value' threshold
* **target_variables**: *(List of Variables)* - *Optional* - List of linked question and values to potentially be adjusted

*target_variables* consists of the following structure:

* **identifier**: *(String)* - Unique identifer e.g. a question code - q050
* **value**: *(Float)* - *Optional* - Numeric value that may be adjusted.

Note:

* Although *predicted* and *auxiliary* are both optional, at least one has to be provided for the calculation to work.
* The principle_identifier is unused by the method and is passed-through as-is into the output dataset
* If no target_variables are provided only the principle_variable may be adjusted

Calculation
-----------

A ratio is determined by the ratio of the latest given value and the last good previous value we have. The $comparisonValue$ is determined by using the either predicted (if provided) or then the auxiliary (if the predicted is not available).

The given $principleValue$ is compared against an upper and lower limit.

Where $comparisonValue \ne 0$ we use:

<p align="center">
<img src="https://latex.codecogs.com/svg.image?{\color{Orange}lowerLimit&space;<&space;\frac{principleValue}{comparisonValue}&space;<&space;upperLimit}" />
</p>

If the ratio is within the limits we determine that a pounds thousands error has been detected.

When a pounds thousands error has been detected we apply the following correction to the principleValue and all linked values:

<p align="center">
<img src="https://latex.codecogs.com/svg.image?{\color{Orange}adjustedValue&space;=&space;\frac{value}{1000}" />
</p>

If any linked variable values are 'missing' then they will not be adjusted and will be placed in the output dataset 'as-is'
If a pounds thousands error has *not* been detected then the principle variable and any linked variables will not be adjusted and placed in the output dataset 'as-is'

Error Detection
---------------

The method explicitly checks for the following error states:

* Predicted and auxiliary are both missing or are both 0
* Principle variable is missing (note, a principle variable of 0 is not an error)
* The upper and lower limits are both 0

The method will catch unexpected errors and will set the TPC marker = 'E' and will populate the accompanying error attribute.

Outputs
-------

* **principle_identifier**: *(String)* - Unique identifer. Will contain same as was input to method.
* **principle_final_value**: *(Float)* - Output value that may or may not have been adjusted
* **target_variables**: *(List of Variables)* - List of linked question and values that may have been adjusted
* **ratio**: *(Float)* - Calculated ratio of the principle value. Used for testing against the given limits.
* **tpc_marker**: *(String)* - C = Correction applied | N = No correction applied | E = Process failure
* **error**: *(String)* - Error information populated when the TPC marker = E. Will be empty/blank on succesful runs

Data example
-------------

|principle_identifier|principle_variable|predicted|aux|threshold_upper|threshold_lower|TPC_marker|ratio|principle_final_value|linked_question|linked_value|linked_final_value
|---|---|---|---|---|---|---|---|---|---|---|---|
q100|50000000|60000|15000|1350|350|C|1000.0|50000.0|q101|500|0.5
-|-|-|-|-|-|-|-|-|q102|1000|1
-|-|-|-|-|-|-|-|-|q103|1500|1.5
-|-|-|-|-|-|-|-|-|q104||
q200|60000000|60000||1350|350|C|400.0|60000.0|||
q300|269980||200|1350|350|C|1349.9|269.98|||
q400|7000|||1350|350|E||7000|||
q450|8000|0|0|1350|350|E||8000|q451|500|500
-|-|-|-|-|-|-|-|-|q452|1000|1000
q500||10|20|1350|350|E|||q501|1234|1234
-|-|-|-|-|-|-|-|-|q502|2345|2345
q600|0|10|20|1350|350|N|0|0|q601|500|500
-|-|-|-|-|-|-|-|-|q602|1000|1000
q700|3500|10|20|1350|350|N|350|3500|q701|1000|1000
q800|0|-1|-1|0|0|E||0|||

NB. This is a mixture of input and output data and is illustrative of behaviour only, and is not indicative of the input/ouput dataset structure used by the method

Examples of usage
-----------------

* [Description/Readme](../sml_small/pounds_thousands/readme.md)
* [Code Example](../sml_small/pounds_thousands/example.py)

Implementation
--------------

* [Method implementation](../sml_small/pounds_thousands/pounds_thousands.py)
* [Method Unit Tests](../sml_small/pounds_thousands/test_pounds_thousands.py)
