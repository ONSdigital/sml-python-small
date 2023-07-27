"""
Common functionality that can be used by any SML method

For Copyright information, please see LICENCE.
"""

from sml_small.utils.error_utils import get_params_is_not_a_number_error


# This is a function to print a table.
# An example input would look like the following:
# print_table(
#         "Name of your table",
#         variable_name_1=variable_value_1,
#         variable_name_2=variable_value_2,
#         ...
#         variable_name_n=variable_value_n,
#     )
def print_table(table_name: str, **kwargs):
    """
    Prints the parsed attributes.

    :param kwargs:
    :type kwargs: kwargs
    :return: N/A (this is a console output)
    """
    # Print table of variable names and values
    print("\n")

    print(table_name)

    print("Variable Name   |   Value")

    print("----------------|---------")

    for var_name, var_value in kwargs.items():
        print(f"{var_name:<15}|   {var_value}")


# This is a function to validate an input is a number.
# Example of usage is as follows:
# if validate_number("total", total) is True:
#     then do something
def validate_number(tag: str, value: str) -> bool:
    """
    This function will take a parsed tag and a value.
    The function then checks to see if the value entered is a number.
    validate_number will raise a ValueError if expectations are not met.

    :param tag: The tag is a way of identifying the value and type entered and is used if a
                ValueError is returned.
    :type tag: str
    :param value: value is what is parsed to the function it can be many different types.
    :type value: float | optional
    :raises ValueError: ValueError is raised for missing numbers or improper data types.
    :return: Returns True when a value can be converted to float.
    :rtype: boolean
    """

    if not is_number(value):
        raise ValueError(get_params_is_not_a_number_error(tag))

    return True


# This function is part of validate_number it will check if the value can
# be converted to a float
def is_number(value) -> bool:
    """
    This function attempts to convert an entered type into a float.
    It will return a boolean dependent on whether it can or can't be converted.

    :param value: value is the parsed parameter which is to be converted to a float(if possible).
    :type value: float | optional
    :return: This return a True boolean value if the value obtained can be converted to a float.
    :rtype: boolean to indicate if value is a number or not.
    """

    try:
        float(value)

    except Exception:
        return False

    return True
