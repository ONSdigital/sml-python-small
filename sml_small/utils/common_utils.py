"""
Common functionality that can be used by any SML method

For Copyright information, please see LICENCE.
"""
import logging.config
from os import path

from sml_small.utils.error_utils import get_params_is_not_a_number_error

log_file_path = path.join(path.dirname(path.abspath(__file__)), "../logging.conf")
logging.config.fileConfig(log_file_path)
# create logger
logger = logging.getLogger("commonUtils")

# This is a function to print a table.
# An example input would look like the following:
# print_table(
#         "Name of your table",
#         variable_name_1=variable_value_1,
#         variable_name_2=variable_value_2,
#         ...
#         variable_name_n=variable_value_n,
#     )
def log_table(table_name: str, **kwargs):
    """
    Prints the parsed attributes.

    :param kwargs:
    :type kwargs: kwargs
    :return: N/A (this is a console output)
    """

    # This constant is used to space out the columns
    # if your variable name is longer than this value
    # then the table would misshapen. If this occurs
    # increase the value.
    table_padding = 32

    # Print table of variable names and values
    logger.info("\n")
    logger.info(table_name)
    logger.info("Variable Name                   |   Value")
    logger.info("--------------------------------|---------")
    for var_name, var_value in kwargs.items():
        logger.info(f"{var_name:<{table_padding}}|   {var_value}")


# This is a function to validate an input is a number.
# Example of usage is as follows:
# if validate_number("variable_name", variable_value) is True:
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
