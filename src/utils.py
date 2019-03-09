"""Miscellaneous Utilities

Helper functions.

Currently, the only function is:

    * round_output - Function to round floats on return
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
        if digits is not None or digits is not 0:
            return round(value, digits)
        else: 
            return int(round(value))
    else:
        return value
