"""
Common functionality that can be used by any SML method

For Copyright information, please see LICENCE.
"""
import logging.config
from os import path

from sml_small.utils.error_utils import get_params_is_not_a_number_error

log_config_path = path.join(path.dirname(path.abspath(__file__)), "../logging.conf")
logging.config.fileConfig(log_config_path)

# Create logger
logger = logging.getLogger("commonUtils")


def log_table(table_name: str, **kwargs):
    """
    Prints the passed attributes as a table to logging.

    :param kwargs:
    :type kwargs: kwargs
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


def validate_number(tag: str, value: str) -> bool:
    """
    The function checks to see if the value entered is a number.
    validate_number will raise a ValueError if expectations are not met.

    :param tag: The tag is a way of identifying the value and type entered and is used if a
                ValueError is returned.
    :type tag: str
    :param value: value is what is parsed to the function it can be many different types.
    :type value: float | optional
    ...
    :raises ValueError: ValueError is raised for missing numbers or improper data types.
    ...
    :return: Returns True when a value can be converted to float.
    :rtype: boolean
    """

    if not is_number(value):
        raise ValueError(get_params_is_not_a_number_error(tag))

    return True


def is_number(value) -> bool:
    """
    This function attempts to convert an entered type into a float.
    It will return a boolean dependent on whether it can or can't be converted.

    :param value: value is the parsed parameter which is to be converted to a float(if possible).
    :type value: float | optional
    ...
    :return: This return a True boolean value if the value obtained can be converted to a float.
    :rtype: boolean to indicate if value is a number or not.
    """

    try:
        float(value)

    except Exception:
        return False

    return True
