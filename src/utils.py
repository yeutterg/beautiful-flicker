"""
Fuction to round-on-return

:param value:           The value to round
:param toround:         Whether or not to round
:param digits:          The number of digits to round to.
                        Set digits=None to round to a whole number.

:returns:               The value, potentially rounded
"""
def round_output(value: float, toround=True, digits=2):
    if toround:
        if digits is not None:
            return round(value, digits)
        else: 
            return int(round(value))
    else:
        return value