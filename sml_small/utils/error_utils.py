
"""
Common functionality related to error handling that can be used by any SML method

For Copyright information, please see LICENCE.
"""

# Error messages that can be incorporated across the board.

def get_mandatory_param_error(param_name) -> str:
    """
    This function will take an input parameter
    name and return an error message that states the parameter must be
    specified.

    :param param_name: Input parameter name
    :type param_name: Any
    :return: Error message telling the user the parameter must be specified
    :rtype: str
    """

    return f"{param_name} is a mandatory parameter and must be specified"


def get_params_is_not_a_number_error(param_name) -> str:
    """
    This function will take an input parameter
    name and return an error message that states the parameter is not a number.

    :param param_name: Input parameter name
    :type param_name: Any
    :return: Error message telling the user the parameter is not a number
    :rtype: str
    """

    return f"{param_name} is not a number"


def get_one_of_params_mandatory_error(param_list) -> str:
    """
    This function returns an error message
    that specifies that one of the parameters in the list (input provided by user)
    must be specified.

    :param param_list: List of parameters to be returned as part of the error message.
    :type param_list: List
    :return: Error string which contains the parameters and highlights the parameter
             that must be specified
    :rtype: str
    """

    separator = " or "
    param_list_text = separator.join(param_list)

    return f"one of {param_list_text} must be specified"


def get_param_outside_range_error(tag, param_list) -> str:
    """
    The function will take a tag/label and a parameter list that contains upper
    and lower thresholds. It will then return an error message that highlights
    that the parameter must be within range.

    :param tag: This is to identify what parameter is breaching the boundary
    :type tag: str
    :param param_list: List containing the lower and upper bounds
    :type param_list: List
    :return: Error highlighting that the parameter has broken
             the boundary rules
    :rtype: str
    """

    separator = " to "
    param_list_text = separator.join(param_list)

    return f"{tag} is outside of range {param_list_text}"
