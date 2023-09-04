"""
Common functionality related to error handling that can be used by any SML method

For Copyright information, please see LICENCE.
"""

from typing import List


def get_mandatory_param_error(param_name: str) -> str:
    """
    This function will take an input parameter
    name and return an error message that states the parameter must be
    specified.

    :param param_name: Input parameter name
    :type param_name: str
    ...
    :return: Error message telling the user the parameter must be specified
    :rtype: str
    """

    return f"{param_name} is a mandatory parameter and must be specified"


def get_params_is_not_a_number_error(param_name: str) -> str:
    """
    This function will take an input parameter
    name and return an error message that states the parameter is not a number.

    :param param_name: Input parameter name
    :type param_name: str
    ...
    :return: Error message telling the user the parameter is not a number
    :rtype: str
    """

    return f"{param_name} is not a number"


def get_one_of_params_mandatory_error(param_list: List[str]) -> str:
    """
    This function returns an error message that specifies that one of the
    parameters in the list (input provided by user) must be specified.

    :param param_list: List of parameters to be returned as part of the error message.
    :type param_list: List[str]
    ...
    :return: Error string which contains the parameters and highlights the parameter
             that must be specified
    :rtype: str
    """

    separator = " or "
    param_list_text = separator.join(param_list)

    return f"one of {param_list_text} must be specified"


def get_param_outside_range_error(tag: str, param_list: List[str]) -> str:
    """
    The function will take a tag/label and a parameter list that contains upper
    and lower thresholds. It will then return an error message that highlights
    the parameter must be within range.

    :param tag: This is to identify what parameter is breaching the boundary
    :type tag: str
    :param param_list: List containing the lower and upper bounds
    :type param_list: List[str]
    ...
    :return: Error highlighting that the parameter has broken
             the boundary rules
    :rtype: str
    """

    separator = " to "
    param_list_text = separator.join(param_list)

    return f"{tag} is outside of range {param_list_text}"


def get_boundary_error(param_list: List[int]) -> str:
    """
    This function returns an error message that specifies that a lower boundary is
    greater than its corresponding upper boundary.

    :param param_list: List of parameters to be returned as part of the error message.
    :type param_list: List[str]
    ...
    :return: Error string which contains the parameters and highlights the parameter
             that must be specified
    :rtype: str
    """
    list_string = map(str, param_list)
    separator = ":"
    param_list_text = separator.join(list_string)

    return f"Lower limit is larger than the upper limit ({param_list_text})"
