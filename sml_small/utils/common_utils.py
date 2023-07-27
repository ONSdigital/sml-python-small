
from typing import List


def print_table(table_name: str, **kwargs):
    """
    Prints the parsed attributes

    :param kwargs:
    :type kwargs: kwargs
    :return: N/A
    """
    # Print table of variable names and values
    print("\n")
    print(table_name)
    print("Variable Name   |   Value")
    print("----------------|---------")
    for var_name, var_value in kwargs.items():
        print(f"{var_name:<15}|   {var_value}")