Method specification
====================

* [SML](https://github.com/ONSdigital/Statistical-Method-Specifications/blob/thousand_pound/thousand_pounds_correction.md)

Overall method
=============

This process determines whether a given value is too large by a factor of ~1000. If so, the value is corrected to be smaller, and any accompanying values are also adjusted accordingly.

The method is to be run for a single instance of a principal question (with 0..n linked questions) at a time. If there are multiple principal questions or multiple references to be processed then the method should be called multiple times, once for each principal question (+ linked) dataset.

* Dataclasses are used to provide structure where required
* All dataclass datasets are immutable upon creation
* Missing/null values are not adjusted (they are placed in the output dataset 'as-is' regardless of calculations)
* Uses built-in python libraries only
* Assumes that all processing can be dealt with 'in-memory' and output is provided as single dataset
* Errors are caught internally within the method and are converted into managed output errors (TPC Marker of "E")

Inputs
------

The method requires at least one of the following as the previous period predictor variable, in the given priority order:

1. Returned, cleaned response,
2. Imputed or constructed value

The calling process is responsible for determining whether a returned, clean response is suitable for use in the method and to set the 'predictive' variable accordingly, giving the following effective priority order:

1. Returned, cleaned response
2. Imputed or constructed value
3. Auxiliary variable, e.g. registered annual turnover

The calling/wrangling process is also responsible for auditing the metadata about the values used in this method (e.g. the source of the predictive value, tpc_ratio, etc).

Note: ensure that predictor and auxiliary variables are of the same denomination as the current period variables.

* **principal_identifier**: *(String)* - Unique identifier e.g. "q500" (question identifier), or "12345678901-202209" (conrtibutor reference & period)
* **principal_variable**: *(Float)* - Numeric value that the method is working on
* **predictive**: *(Float)* - *Optional* - Numeric value used for comparison. A previous 'valid' value (i.e. Returned/Imputed/Constructed)
* **auxiliary**: *(Float)* - *Optional* - Alternative numeric` value used when a predictive value is not available and required by the user
* **upper_limit**: *(Float)* - Upper bound of 'error value' threshold
* **lower_limit**: *(Float)* - Lower bound of 'error value' threshold
* **target_variables**: *(List of Variables)* - *Optional* - List of linked question and values to potentially be adjusted

*target_variables* consists of the following structure:

* **identifier**: *(String)* - Unique identifer e.g. a question code - q050
* **value**: *(Float)* - *Optional* - Numeric value that may be adjusted.

Note:

* Although *predictive* and *auxiliary* are both optional, at least one has to be provided for the calculation, else a method error is produced
* The principal_identifier is unused directly by the method and is passed-through as-is into the output dataset. This attribute is provided to allow a user context to be provided as required. For example, it could contain a contributor reference, an IDBR period and a question code ('19900001234-202207-q500'), a unique system generated ID ('cfacf706-36a5-4acb-935f-67e7b07c0470'), just the principal question code ('q150'), etc. It is a text/string field and no parsing or validation is undertaken by the method.
* If no target_variables are provided only the principal_variable may be adjusted

Calculation
-----------

A ratio is determined by the ratio of the latest returned principal value and the corresponding previous period value. The $comparisonValue$ is determined by either the predictive variable (if provided) or the the auxiliary (if the predictive is not available and an appropriate auxiliary variable exists).

The resulting ratio is compared against an upper and lower limit.

Where $comparisonValue \ne 0$ we use:

<p align="center">
<img src="https://latex.codecogs.com/svg.image?{\color{Orange}lowerLimit&space;<&space;\frac{principalValue}{comparisonValue}&space;<&space;upperLimit}" />
</p>

If the ratio is within the limits we determine that a pounds thousands error has been detected.

When a pounds thousands error has been detected we apply the following correction to the principalValue and all linked values:

<p align="center">
<img src="https://latex.codecogs.com/svg.image?{\color{Orange}adjustedValue&space;=&space;\frac{value}{1000}" />
</p>

If the previous period's value is zero, then the method does not continue. A thousand pounds error is neither detected nor corrected.
If any linked variable values are 'missing' then they will not be adjusted and will be placed in the output dataset 'as-is'
If a pounds thousands error has *not* been detected then the principal variable and any linked variables will not be adjusted and placed in the output dataset 'as-is'

Error Detection
---------------

The method explicitly checks for the following error states:

* Predictive and auxiliary are both missing or are both 0
* Principal variable is missing (note, a principal variable of 0 is not an error)
* At least one of the upper or lower limits are missing or 0

The method will catch unexpected errors and will set the TPC marker = 'E' and will populate the accompanying error attribute. For example, if non-numeric values are provided as inputs to numeric atttributes (such as principal value).

Outputs
-------

* **principal_identifier**: *(String)* - Unique identifer. Will contain same as was input to method.
* **principal_original_value**: *(Float)* - Original provided value
* **principal_adjusted_value**: *(Float)* - Output value that may or may not have been adjusted
* **target_variables**: *(List of Variables)* - List of linked questions, original values and adjusted values (if appropriate)
* **tpc_ratio**: *(Float)* - Calculated ratio of the principal value. Used for testing against the given limits.
* **tpc_marker**: *(String)* - C = Correction applied | N = No correction applied | E = Process failure
* **error_description**: *(String)* - Error information populated when the TPC marker = E. Will be empty/blank on succesful runs

Data example
-------------

|principal_identifier|principal_variable|predictive|aux|threshold_upper|threshold_lower|tpc_marker|tpc_ratio|principal_adjusted_value|target_variable|target_original_value|target_adjusted_value
|---|---|---|---|---|---|---|---|---|---|---|---|
[A] Valid config with linked questions|50000000|60000|15000|1350|350|C|1000.0|50000.0|q101|500|0.5
[A] Valid config with linked questions|-|-|-|-|-|-|-|-|q102|1000|1
[A] Valid config with linked questions|-|-|-|-|-|-|-|-|q103|1500|1.5
[A] Valid config with linked questions|-|-|-|-|-|-|-|-|q104||
[B] Missing auxiliary|60000000|60000||1350|350|C|400.0|60000.0|||
[C] Missing predictive|269980||200|1350|350|C|1349.9|269.98|||
[D] Missing predictive and auxiliary|7000|||1350|350|E||7000|||
[E] Predictive and auxiliary are 0|8000|0|0|1350|350|E||8000|q451|500|500
[E] Predictive and auxiliary are 0|-|-|-|-|-|-|-|-|q452|1000|1000
[F] Missing principle variable||10|20|1350|350|E|||q501|1234|1234
[F] Missing principle variable|-|-|-|-|-|-|-|-|q502|2345|2345
[G] Principle variable is 0|0|10|20|1350|350|N|0|0|q601|500|500
[G] Principle variable is 0|-|-|-|-|-|-|-|-|q602|1000|1000
[H] Ratio is exactly lower limit|3500|10|20|1350|350|N|350|3500|q701|1000|1000
[I] Ratio is exactly upper limit|13500|10|20|1350|1350|N|350|13500|q801|1000|1000
[J] Upper and Lower limits are 0|0|-1|-1|0|0|E||0|||
[K] Text is passed into numeric fields|"Cheese"|"Toast"|"Jam"|"Rhubarb"|"Custard"|E||"Cheese"|||

NB. This is a mixture of input and output data and is illustrative of behaviour only, and is not indicative of the input/ouput dataset structure used by the method

Examples of usage
-----------------

* [Description/Readme](../sml_small/pounds_thousands/readme.md)
* [Code Example](../sml_small/pounds_thousands/example.py)

Implementation
--------------

* [Method implementation](../sml_small/pounds_thousands/pounds_thousands.py)
* [Method Unit Tests](../sml_small/pounds_thousands/test_pounds_thousands.py)
