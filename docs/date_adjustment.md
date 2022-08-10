Overall method
=============

The controlling function validates the input DataFrames and Parameters before stepping 
the data through the sub-functions in the following order:

1. generate_average_weekly_questions
2. missing_value_subfunction
3. primary_wrangler_subfunction
4. midpoint_subfunction
5. secondary_wrangler_subfunction
6. date_adjustment_subfunction
7. average_weekly_subfunction
    
All calculations are done on a row by row basis.

>##### NOTE:
>The seven sub-functions are private to the main method and must not be called independently.

Required Inputs
---------------

* **input_dataframe**: (DataFrame): The dataframe containing the data to be processed plus processing options.
* **trading_weights**: (DataFrame): The trading day weight reference data required for processing.
* **target_columns**: (List of Strings): The trading day weight reference data required for processing.
* **contributor_returned_start_date_col**: (String): Name of the column holding the contributors returned period 
start date in the input DataFrame.
* **contributor_returned_end_date_col**: (String): Name of the column holding the contributors returned period 
end date in the input DataFrame.
* **expected_start_date_col**: (String): Name of the column holding the expected period start date in the input 
DataFrame.
* **expected_end_date_col**: (String): Name of the column holding the expected period end date in the input DataFrame.
* **domain_col**: (String): Name of the column holding the Domain (SIC) in the input DataFrame.
* **short_period_parameter_col**: (String): Name of the column holding the "short period parameter" in the input 
DataFrame.
* **long_period_parameter_col**: (String): Name of the column holding the "long period parameter" in the input 
DataFrame.
* **equal_weighted_col**: (String): Name of the column holding the "Use equal weighted" option in the input DataFrame.
* **set_to_mid_point_col**: (String): Name of the column holding the "Use mid-point method" option in the input 
DataFrame.
* **use_calendar_days_col**: (String): Name of the column holding the "use calendar days" option in the input 
DataFrame.
* **average_weekly_col**: (String): Name of the column holding the "average_weekly" in the input DataFrame.
* **da_error_flag_col**: (String): Name of the column that the user wishes the error flag column to be called in the 
output DataFrame.
* **trading_date_col**: (String): Name of the column holding the dates in the trading weights DataFrame.
* **trading_weights_col**: (String): Name of the column holding the weights in the trading weights DataFrame.
* **trading_domain_col**: (String): Name of the column holding the domain (SIC) in the trading weights DataFrame.
* **trading_period_start_col**: (String): Name of the column holding the trading period start date in the trading 
weights DataFrame.
* **trading_period_end_col**: (String): Name of the column holding the trading period end date in the trading 
weights DataFrame.


Parameter Options and restrictions
----------------------------------

Although some parameters, such as contributor date column names, are obvious and
open-ended, some are restricted in their values. Normally such run-time parameters
would be set by options in the front end client, but in case this is module is being
used in a more free-form manner, the following may be useful:

* **Target columns**: The columns in the input dataframe that  will be date adjusted.
<br/><br/>
* **Set to equal weighted**: 
  * "**Y**": Set all rows to equal weighting
  * "**N**": Utilise trading weights dataframe for all rows.
<br/><br/>
* **Average weekly**: Define which questions will undergo average weekly adjustment: 
  * "**A**": All
  * "**N**": None
  * "**\<List>**": A subset of the target columns.
<br/><br/>
* **Set to midpoint**: Define which midpoint method to use:
  * "**N**": No midpoint method
  * "**Y**": Standard midpoint method.
  * "**YT**": Trimmed midpoint method.
<br/><br/>
* **Use calendar days**: Define which dates to use if midpoint changes return dates:
  * "**Y**": Use the start and end dates of the midpoints calendar month.
  * "**N**" - Use the start and end dates of the midpoints trading period.


      WARNING: The value for each of these options must be the same for every row of
               the input dataframe.

Error Flags
-----------

If a row of data is not able to be processed, an error flag will be raised to indicate the issue with the data.
The error flags are as follows:

* **E00**: Average Weekly parameter is invalid.
* **E01**: The value to be date adjusted is missing from one of the target columns.
* **E02**: The contributor returned end date is earlier than the contributor returned start date.
* **E03**: A required record for calculating weight m is missing from the trading weights table.
* **E04**: A required trading weight for calculating weight m is null or blank.
* **E05**: A required trading weight for calculating weight m has a negative value.
* **E06**: A required record for calculating weight n is missing from or duplicated in the trading  weights table.
* **E07**: A required trading weight for calculating weight n is null or blank.
* **E08**: A required trading weight for calculating weight n has a negative value.
* **E09**: The contributors return does not cover any of expected period.
* **E10**: The sum of trading day weights over contributors returned period is zero.
* **E11**: The sum of trading day weights over contributors returned period is zero.
* **E12**: A required record for calculating midpoint date is missing from the trading weights table.
* **E13**: A required record for setting APS and APE by midpoint is missing from or duplicated in the trading  weights table.
* **E14**: Expected period start date is missing or an invalid date.
* **E15**: Expected period end date is missing or an invalid date.


>##### NOTE:
>These are NOT exceptions and do not cause the method to fail. Once an error flag
has been placed on a row of data, no further processing is done to that row,
preserving the data in the state it was when the flag was raised.
<br><br>
If at any point in processing an error flag is set on all rows, processing will
stop after that sub-function and the dataframe will be returned as it is at that
point to allow the user to 'debug' their data.

Warning Flags
-------------

If a row of data is able to be processed, but requires the user to be notified of a
potential issue, a warning flag is raised for that row. The following warning flags
are applied in the given circumstances:
* "**S**": The contributors returned period is less than the threshold supplied
      in the short period parameter.
* "**L**": The contributors returned period is greater than the threshold supplied
      in the long period parameter.
* "**SL**": The supplied short period parameter is greater than or equal to the
        supplied long period parameter.


>##### NOTE:
>A warning flag does not stop the method running, and the row will continue to be
processed as normal.


Overview of Sub-functions
-------------------------

### 1. generate_average_weekly_questions

This sub-function generates the average_weekly_questions_list, an internal variable used later in the average
weekly method. The two fixed parameter values of average_weekly and their respective outputs are:
* "**A**" : **A**ll of the target columns will be passed through the average weekly method.
* "**N**"  : **N**one of the target columns will be passed through the average weekly method.

However, it is also possible to run the average_weekly method in "Selective Mode". To run the average weekly
method in this way, the average_weekly parameter must be a list that is subset of target_columns.

For example, f you provided a target_columns parameter of:

    ['question_a', 'question_b', 'question_c', 'question_d']

and wanted to run the average weekly method on questions b and c, you should use an average_weekly
parameter of:

    ['question_b', 'question_c']

or:

    "question_b, question_c"

When using selective mode, if any element in average_weekly does not exactly match an element in
    target_columns, output will be returned at this point showing an "E00" error flag.
>##### NOTE:
>The value for the average_weekly parameter must be the same for every row of the input DataFrame.

<br>

### 2. missing_value_subfunction

If any data in the target columns is null or missing, that row is assigned an "E01" error flag. The error does not
stop the process running, but no further processing will be done on that row.

>##### NOTE:
>For legacy compatibility, a value of "." also counts as null and will be treated as such.

An error flag column with the user specified name is added to the dataframe to hold error flags generated in this
and further processing.

<br>

### 3. primary_wrangler_subfunction

**For each row not already holding an error flag, do the following:**
*  If it has a null or missing contributor returned start date value,
    use the expected start date instead.
*  If it has a null or missing contributor returned end date value,
    use the expected end date instead.

**Then for each row not already holding an error flag do the following:**
* Set weight m to zero as a default
* Set the number of days in contributors_returned_period to zero as a default
* If the contributor returned end date is earlier than the contributor returned start date,
   apply error flag E02 and do not process row further.
* Calculate the number of days in contributors returned period.
* If a required record for calculating weight m is missing from the trading weights table,
   apply error flag E03 and do not process row further.
* If a required trading weight for calculating weight m is null or blank,
   apply error flag E04 and do not process row further.
* If a required trading weight for calculating weight m has a negative value,
   apply error flag E05 and do not process row further.
* Calculate the weight m from the trading weight data and contributor returned dates.

>##### NOTE:
>The number of days in contributor period and sum of trading day weights in contributor period are not parameters 
because they are created in this sub-function.

<br>

### 4. midpoint_subfunction

**CRPS**: **C**ontributor **R**eturned **P**eriod **S**tart <br>
**CRPE**: **C**ontributor **R**eturned **P**eriod **E**nd <br>
**APS**: **A**ctual **P**eriod **S**tart date <br>
**APE**: **A**ctual **P**eriod **E**nd Date <br>
**EPS**: **E**xpected **P**eriod **S**tart date <br>
**EPE**: **E**xpected **P**eriod **E**nd date <br>
**MPD**: **M**id-**P**oint **D**ate

**For each row not already holding an error flag, do the following in order:**
<br>

* If the set to mid-point parameter is set to 'N':
  * Set the APS to the EPS
  * Set the APE to the EPE
  * Stop processing.
<br></br>
* If equal weighted columns parameter is set to 'Y': 
  * set set to mid-point parameter to 'Y'.
<br></br>
* If the equal weighted columns parameter is set to 'N': 
    * Set CRPS to earliest date >= CRPS with a non-zero trading weight in same domain.
    * If lack of trading weight data makes this impossible, apply error flag E12 and do not process further.
    * Set CRPE to latest date <= CRPE with a non-zero trading weight in same domain.
    * As before, if lack of trading weight data makes this impossible, apply error flag E12 and do not process further.
<br></br>
* Calculate the number of days between CRPS and CRPS and add 1 one.
* If the calculated difference is an odd number, add a further day.
* Add the the difference / 2 to the CRPS to get the MPD.
<br></br>
* If EPS  <= MPD *and* MPD <= EPE:
    * Set the APS to the EPS.
    * Set the APE to the EPE.
* Otherwise: 
  * Set Date Change Flag to 'C'.
  * If use calender days is set to 'Y':
    * set APS to the first date of the calendar month containing the MPD.
    * set APE to the last date of the calendar month containing the MPD.
  * If use calender days  is set to 'N':
    * set APS to the first date of the trading period containing the MPD.
    * set APE to the last date of the trading period containing the MPD.
    * If lack of trading weight data makes this impossible, apply error flag E13 and stop processing.
    
<br>

### 5. secondary_wrangler_subfunction

**For each row not already holding an error flag, do the following:**
* If the set to mid-point parameter is not set to 'YT', calculate the number of days in actual returned period.

**Then, for each row not already holding an error flag, do the following:**
* If the contributors returned period is less than the threshold supplied in the short period parameter,
    apply warning flag 'S'.
* If the contributors returned period is greater than the threshold supplied in the long period parameter,
    apply warning flag 'L'.
* If the supplied short period parameter is greater than or equal to the supplied long period parameter,
    apply warning flag 'SL'.

**Next, for each row not already holding an error flag, do the following:**
* If the midpoint parameter is set to 'Y':
  * set weight n equal to the number of days in actual returned period
* Else:
  * If a required record for calculating weight n is missing from the trading weights table,
    apply error flag E06 and do not process row further.
  * If a required trading weight for calculating weight n is null or blank,
    apply error flag E07 and do not process row further.
  * If a required trading weight for calculating weight n has a negative value,
    apply error flag E08 and do not process row further.
  * Calculate the weight n from the trading weight data and actual returned dates.

**Finally, for each row not already holding an error flag, do the following:**
* If the contributor returned period does not overlap the actual return period by at least 1 day,
  apply error flag E09 and do not process row further.

<br>

### 6. date_adjustment_subfunction

**For each row not already holding an error flag, do the following:**
* If weight m is zero, apply error flag E10 and do not process row further.
* If weight n is zero, apply error flag E10 and do not process row further.
* Calculate the date adjusted value for each column listed in the target columns parameter.

>##### NOTE:
>AW = The sum of trading day weights over actual returned period. <br>
CW = The sum of trading day weights over contributor returned period.<br></br>
Adjusted Value = Value * (AW / CW)

<br>

### 7. weekly_average_subfunction

**For each row not already holding an error flag, do the following:**
* Calculate the average weekly value for each column listed in the average weekly questions list parameter.

>##### NOTE:
>AD = The number of days in the actual returned period. <br></br>
Average Weekly Value =  (7 * Date Adjusted Value) / AD
