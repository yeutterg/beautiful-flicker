"""Flicker Standard Adherence

These functions test flicker parameters for adherance to common standards.

The functions are:

    * ieee_1789_2015 - Tests for compliance with IEEE 1789-2015
    * california_ja8_2019 - Tests for compliance with California JA8 2019
    * well_building_standard_v2 - Tests for compliance with the WELL Building Standard flicker requirement
"""

def ieee_1789_2015(frequency:float, percent_flicker:float) -> str:
    """Tests for compliance with IEEE 1789-2015

    Refer to 8.1.1 Simple recommended practices in IEEE 1789-2015 for rule definitions

    Parameters
    ----------
    frequency : float
        The flicker frequency in Hertz
    percent_flicker : float
        The flicker percentage

    Returns
    -------
    str
        Either of: "No Risk", "Low Risk", "High Risk"
    """

    if frequency > 3000:
        return "No Risk"

    if frequency < 90:
        if percent_flicker < 0.01 * frequency:
            return "No Risk"

        if percent_flicker < 0.025 * frequency:
            return "Low Risk"

    # Other flicker <= 3 kHz
    if percent_flicker < 0.0333 * frequency:
        return "No Risk"
            
    if frequency <= 1250:
        if percent_flicker < 0.08 * frequency:
            return "Low Risk"

    return "High Risk"


def california_ja8_2019(frequency:float, percent_flicker:float) -> bool:
    """Tests for compliance with California JA8 2019

    California Joint Appendix 8 defines flicker thresholds in section
    JA 8.4.6 and table JA-8:
    https://efiling.energy.ca.gov/GetDocument.aspx?tn=223245-9&DocumentContentId=27701

    Parameters
    ----------
    frequency : float
        The flicker frequency in Hertz
    percent_flicker : float
        The flicker percentage

    Returns
    -------
    bool
        If True, the light source passes
        If False, the light source does not pass
    """

    if frequency > 200:
        # Pass for frequencies above 200 Hz
        return True
    elif percent_flicker < 30:
        # Pass for frequencies below 200 Hz with percent flicker below 30%
        return True
    else:
        # Fails
        return False


def well_building_standard_v2(frequency:float, percent_flicker:float) -> bool:
    """Tests for compliance with the WELL Building Standard flicker requirement

    The WELL Building Standard defines flicker thresholds in L07 part 2:
    https://v2.wellcertified.com/v/en/light/feature/7

    Parameters
    ----------
    frequency : float
        The flicker frequency in Hertz
    percent_flicker : float
        The flicker percentage

    Returns
    -------
    bool
        If True, the light source passes
        If False, the light source does not pass
    """

    if frequency > 90:
        """Satisfies part A:
        A minimum frequency of 90 Hz at all 10% light output intervals 
        from 10% to 100% light output.
        """
        return True
    elif percent_flicker < 5:
        """Satisfies part B:
        LED products with a “low risk” level of flicker (light modulation) of 
        less than 5%, especially below 90 Hz operation as defined by IEEE 
        standard 1789-2015 LED.
        """
        return True
    else:
        # Fails
        return False
