# Directory for holding dev utils and functions common across multiple methods.


# Error messages that can be incorporated across the board.

def get_mandatory_param_error(param_name) -> str:
    """
    get_mandatory_param_error This function will take an input parameter
    name and return an error message that states the parameter must be 
    specified.

    :param param_name: Input parameter name
    :type param_name: Any
    :return: Error message telling the user the parameter must be specified
    :rtype: str
    """

    return f"{param_name} is a mandatory parameter and must be specified"

def get_params_is_not_a_number(param_name) -> str:
    """
    get_params_is_not_a_number This function will take an input parameter
    name and return an error message that states the parameter is not a number.

    :param param_name: Input parameter name
    :type param_name: Any
    :return: Error message telling the user the parameter is not a number
    :rtype: str
    """    

    return f"{param_name} is not a number"


def get_one_of_the_params_mandatory(param_list) -> str:
    """
    get_one_of_the_params_mandatory This function returns an error message
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


def get_param_more_than_lower_threshold_less_than_or_equal_to_higher_threshold(tag, param_list) -> str:
    """
    get_param_more_than_lower_threshold_less_than_or_equal_to_higher_threshold.
    The function will take a tag/label and a parameter list that contains upper
    and lower thresholds. It will then return an error message that highlights
    that the parameter must be greater than the lower bound and less than or
    equal to the upper bound.

    :param tag: This is to identify what parameter is breaching the boundary
    :type tag: str
    :param param_list: List containing the lower and upper bounds
    :type param_list: List
    :return: Error highlighting that the parameter has broken
             the boundary rules
    :rtype: str
    """    

    separator = " and less than or equal to "
    param_list_text = separator.join(param_list)

    error_message = f"{tag} range must be more than {param_list_text}"

    return error_message