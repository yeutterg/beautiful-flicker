"""Flicker Plotting Functions

These functions generate commonly-used flicker graphics.

The functions are:

    * ieee_par_1789_graph - Plots the IEEE PAR 1789 logarithmic graph
    * waveform_graph - Plots the time-domain flicker waveform
    * standards_color - Returns colors for decorating standards result labels
"""

import math
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.colors
import itertools
from matplotlib.ticker import PercentFormatter, ScalarFormatter
from .utils import bool_to_pass_fail
from sklearn.preprocessing import minmax_scale
from pylab import text


def ieee_par_1789_graph(
        data, figsize:tuple=(8,4), filename:str=None, showred:bool=True, showyellow:bool=True, 
        noriskcolor:bool=True, max_freq:int=3000, min_pct:float=0.1, suppress:bool=False
    ):
    """Plots the IEEE PAR 1789 logarithmic graph

    Parameters
    ----------
    data : list
        The data points as a list of tuples as [(freq, mod, 'Name')], where mod is <= 1
    figsize : tuple
        The (width,height) of the plotted figure
    filename : str or None
        If specified, will save plot as the specified filename, e.g.: filename='../out/this_graph.png'
    showred : bool
        Whether to show the unsafe region in red
    showyellow : bool
        Whether to show the low-risk region in yellow
    noriskcolor : bool
        If False, no risk region will show in gray. If True, will show in green
    max_freq : int
        The maximum frequency, in kHz
    min_pct : float
        The minimum percent to display
    suppress : bool
        If True, the plot will not be shown        
    """

    # count minimum percent decimals and recompute 
    if min_pct is not 0:
        decimals = str(min_pct)[::-1].find('.')
        min_pct = min_pct / 100.0
    else:
        decimals = 1
        min_pct = 0.001
    
    # set up plot
    fig, ax = plt.subplots(1, 1, figsize=figsize, tight_layout=True)
    plt.xlim([1,max_freq])
    plt.ylim([min_pct,1])
    plt.xscale('log')
    plt.yscale('log')
    plt.xlabel('Frequency (Hz)')
    plt.ylabel('Modulation (%)')
    plt.gca().xaxis.set_major_formatter(ScalarFormatter())
    plt.gca().yaxis.set_major_formatter(PercentFormatter(1, decimals=decimals))
    plt.grid(which='both')
    ax.set_axisbelow(True)

    # plot no risk region
    norisk_region = [[1, min_pct], [1, 0.001], [10, 0.001], [100, 0.01], [100, 0.03], [3000, 1], \
        [max_freq, 1], [max_freq, min_pct], ]
    fc_color = 'g'
    if not noriskcolor:
        fc_color = 'gray'
    norisk = plt.Polygon(norisk_region, fc=fc_color, alpha=0.3)
    plt.gca().add_patch(norisk)

    # plot low risk region
    if showyellow:
        lowrisk_region = [[1, 0.001], [1, 0.002], [8, 0.002], [90, 0.025], [90, 0.075], [1200, 1], \
            [3000, 1], [100, 0.03], [100, 0.025], [100, 0.01], [10, 0.001]]
        lowrisk = plt.Polygon(lowrisk_region, fc='y', alpha=0.3)
        plt.gca().add_patch(lowrisk)

    # plot high risk region
    if showred:
        highrisk_region = [[1, 0.002], [8, 0.002], [90, 0.025], [90, 0.075], [1200, 1], [1, 1]]
        highrisk = plt.Polygon(highrisk_region, fc='r', alpha=0.2)
        plt.gca().add_patch(highrisk)

    # plot the data
    markers = itertools.cycle(('o', '^', 's', 'D', 'p', 'P'))
    for pt in data:
        plt.scatter(pt[0], pt[1], label=pt[2], marker=next(markers), alpha=1)
    plt.legend()

    # save the figure if a filename was specified
    if filename:
        plt.savefig(filename, dpi=300)

    # show the plot
    if not suppress:
        plt.show()


def waveform_graph(waveform, figsize:tuple=(8,4), suppress:bool=False, filename:str=None, 
                   showstats:bool=True, showstandards:bool=True, num_periods:int=None, 
                   fullheight:bool=False, data=None):
    """Plots the time-domain flicker waveform

    Parameters
    ----------
    waveform : Waveform
        The Waveform object
    figsize : tuple
        The (horizontal, vertical) figure size
    suppress : bool
        If True, will not run plt.show()
    filename : str or None 
        If specified, will save the file named as such, e.g.: filename='../out/this_graph.png'
    showstats : bool
        If True, will show the flicker frequency, percent, and index on the bottom left of the graph
    showstandards : bool
        If True, will display IEEE, WELL, and JA8 test results on the bottom right of the graph
    num_periods : int or None
        If not None, will truncate the graph to the specified number of periods. 
        NOTE: Must be less than the number of periods present in the data
    fullheight : bool
        If True, will set the bottom y limit to zero. 
        If False, will display the non-scaled waveform starting from v_min
    data : np.ndarray or None
        If None, will plot the regular waveform
        If ndarray, will plot the array 
    """
    
    # Get the data from the waveform
    if data is None:
        data = waveform.get_data()

    # Create the figure
    fig, ax = plt.subplots(1, 1, figsize=figsize)
    plt.ylabel('Light Output')
    plt.xlabel('Time (ms)')

    # hide the top and right axes
    ax.spines['top'].set_color('none')
    ax.spines['right'].set_color('none')

    # get the number of periods to display
    if num_periods:
        data = waveform.get_n_periods(num_periods=num_periods)

    # scale the x axis to milliseconds
    x_data = data[:,0] * 1000

    # get minimum for y axis scaling
    y_min = waveform.get_v_min() / waveform.get_v_max()

    # display the waveform full height? (xmin=0)
    if fullheight:
        plt.ylim((0,1))
        plt.yticks(np.linspace(0, 1, 6))

        # scale y axis to 0.99 because of strange clipping at 1.0
        y_data = minmax_scale(data[:,1], feature_range=(y_min,0.99)) 
    else:
        ax.spines['left'].set_smart_bounds(True)

        # scale y axis to (0,1)
        y_data = minmax_scale(data[:,1], feature_range=(y_min,0.99))

    # make the left and bottom axis look cleaner
    ax.spines['bottom'].set_smart_bounds(True)
    
    # plot
    ax.plot(x_data, y_data)

    # show stats on the graph
    if showstats:
        text(0.02, 0.1, waveform.summary(), ha='left', va='center', transform=ax.transAxes)

    # show standard test results on the graph
    if showstandards:
        std_text = "IEEE 1789: " + waveform.get_ieee_1789_2015() + \
            "\nCalifornia JA8: " +  bool_to_pass_fail(waveform.get_california_ja8_2019()) + \
            "\nWELL v2: " +  bool_to_pass_fail(waveform.get_well_standard_v2())
        text(0.955, 0.1, std_text, ha='right', va='center', transform=ax.transAxes) #, backgroundcolor='silver')

    # save the figure if a filename was specified
    if filename:
        plt.savefig(filename, dpi=300)

    # show the plot
    if not suppress:
        plt.show()


def standards_color(result:str) -> str:
    """Returns colors for decorating standards result labels

    For example, "Pass" returns 'green' and "Fail" returns 'red'

    Parameters
    ----------
    result : str
        The text string to apply color to

    Returns
    -------
    str
        The color, either 'green', 'yellow', or 'red'
    """

    if result is "Pass" or result is "No Risk":
        return 'green'
    elif result is "Low Risk":
        return 'yellow'
    else:
        return 'red'
    