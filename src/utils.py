"""Miscellaneous Utilities

Helper functions.

The functions are:

    * round_output - Function to round floats on return
    * bool_to_pass_fail - Converts a boolean True to "Pass" and False to "Fail"
"""


def round_output(value:float, toround:bool=True, digits:int=2):
    """Function to round floats on return

    Wrap return values with this function to easily round output.
    e.g. To round to one decimal place: 
    return round_output(return_value, toround=True, digits=1)

    Parameters
    ----------
    value : float
        The value to round
    toround : bool
        Whether or not to round
    digits : int or None
        The number of digits to round to. 
        To round to a whole number (int), set digits to None or 0

    Returns
    -------
    float or int
        If toround=True: The input value, rounded to an int or float
        If toround=False: The input value, not rounded
    """

    if toround:
        if digits is not None or digits != 0:
            return round(value, digits)
        else: 
            return int(round(value))
    else:
        return value


def bool_to_pass_fail(value:bool) -> str:
    """Converts a boolean True to "Pass" and False to "Fail"

    Parameters
    ----------
    value : bool
        A boolean value representing True for Pass and False for Fail

    Returns
    -------
    str
        "Pass" or "Fail"
    """

    if value:
        return "Pass"
    else:
        return "Fail"
