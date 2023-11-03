"""
Common functionality that can be used by any SML method

For Copyright information, please see LICENCE.
"""
import logging.config
from cmath import nan
from decimal import Decimal, getcontext
from os import path
from typing import Dict, List

from sml_small.utils.error_utils import get_param_outside_range_error, get_params_is_not_a_number_error

log_config_path = path.join(path.dirname(path.abspath(__file__)), "../logging.conf")
logging.config.fileConfig(log_config_path)

# Create logger
logger = logging.getLogger("commonUtils")

# --- Constant Definitions ---
PRECISION_MIN = 1
PRECISION_MAX = 28

# --- Constant Definitions ---
PRECISION_MIN = 1
PRECISION_MAX = 28


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


def validate_precision(precision):
    # Default the precision value when not set
    if precision is None:
        precision = PRECISION_MAX
    else:
        if validate_number("precision", precision) is True:
            precision = int(precision)

            if precision < PRECISION_MIN or precision > PRECISION_MAX:
                raise ValueError(
                    get_param_outside_range_error(
                        "precision",
                        [
                            str(PRECISION_MIN),
                            str(PRECISION_MAX),
                        ],
                    )
                )
    return precision


def convert_input_to_decimal(
    keys: List[str],
    args: List[float],
    precision: int,
) -> Dict[str, Decimal]:
    """
    convert_input_to_decimal This function will take key value pairs within a dict
    the values will then be converted to decimal if appropriate.

    :param keys: List of string names associated with the values in the list
    :type keys: List[str]
    :param args: Values to be converted to decimal
    :type args: List[float]
    :raises ValueError: Error string raised in the event the keys do not
    have arguments or arguments do not have keys
    ...
    :return: key names and their values returned as decimals if appropriate.
    :rtype: Dict[str, Decimal]
    """
    try:
        if len(keys) != len(args):
            raise ValueError("Number of keys needs to match the number of arguments")

        getcontext().prec = precision
        decimal_values = {}

        # Using zip to iterate through the keys and arguments simultaneously
        for key, arg in zip(keys, args):
            if type(arg) == Decimal:
                decimal_values[key] = arg

            elif type(arg) == list:
                if arg == []:
                    decimal_values[key] = arg

                else:
                    for i in range(len(arg)):
                        if type(arg[i]) == Decimal:
                            decimal_values[key] = arg

                        elif arg[i] is None or arg[i] == nan:
                            decimal_values[key] = arg

                        else:
                            arg[i] = Decimal(str(arg[i]))
                            decimal_values[key] = arg
            elif type(arg) == dict:
                if arg == {}:
                    decimal_values[key] = arg
                else:
                    for dict_keys, dict_values in arg.items():
                        if type(dict_values) == Decimal:
                            decimal_values[key] = arg
                        elif dict_values is None or dict_values == nan:
                            decimal_values[key] = arg
                        else:
                            arg[dict_keys] = Decimal(str(dict_values))
                            decimal_values[key] = arg

            elif arg is None or arg is nan:
                decimal_values[key] = arg

            else:
                decimal_values[key] = Decimal(str(arg))

        return decimal_values
    except Exception as error:
        raise error
