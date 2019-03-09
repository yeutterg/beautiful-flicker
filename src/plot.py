import math
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.colors
import itertools
from matplotlib.ticker import PercentFormatter, ScalarFormatter
from sklearn.preprocessing import minmax_scale
from pylab import text

"""
Plots the IEEE PAR 1789 graphic

@param list data                            The data points as a list of tuples as [(freq, mod, 'Name')], where mod is <= 1
@param tuple figsize [optional]             The (width,height) of the plotted figure
@param string filename [optional]           If specified, will save plot as the specified filename
@param bool showred [optional]              Whether to show the unsafe region in red
@param bool showyellow [optional]           Whether to show the low-risk region in yellow
@param bool noriskcolor [optional]          If False, no risk region will show in gray. If True, green
@param int max_freq [optional]              The maximum frequency, in kHz
@param float min_pct [optional]             The minimum percent to display
@param bool supress [optional]              If True, the plot will not be shown
"""
def ieee_par_1789_graphic(
        data, figsize=(8,4), filename=None, showred=True, showyellow=True, noriskcolor=True, max_freq=3000, min_pct=0.1, 
        suppress=False
    ):
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
    norisk_region = [[1, min_pct], [1, 0.001], [10, 0.001], [100, 0.01], [100, 0.03], [3000, 1], [max_freq, 1], [max_freq, min_pct], ]
    fc_color = 'g'
    if not noriskcolor:
        fc_color = 'gray'
    norisk = plt.Polygon(norisk_region, fc=fc_color, alpha=0.3)
    plt.gca().add_patch(norisk)

    # plot low risk region
    if showyellow:
        lowrisk_region = [[1, 0.001], [1, 0.002], [8, 0.002], [90, 0.025], [90, 0.075], [1200, 1], [3000, 1], [100, 0.03], [100, 0.025], [100, 0.01], [10, 0.001]]
        lowrisk = plt.Polygon(lowrisk_region, fc='y', alpha=0.3)
        plt.gca().add_patch(lowrisk)

    # plot high risk region
    if showred:
        highrisk_region = [[1, 0.002], [8, 0.002], [90, 0.025], [90, 0.075], [1200, 1], [1, 1]]
        highrisk = plt.Polygon(highrisk_region, fc='r', alpha=0.2)
        plt.gca().add_patch(highrisk)

    # Plot the data
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


"""
Plots the time-domain flicker waveform

:param data:
:param figsize:
:param suppress:
:param filename:        If specified, will save the graphic named as such
:param showstats:       Will display
:param num_periods:     If not None, will shorten display to the number of periods
:param fullheight:      If true, the xmin will be zero. Otherwise, it will auto-set from the waveform v_min
"""
def waveform_graph(waveform, figsize=(8,4), suppress=False, filename=None, showstats=True,
                   num_periods=None, fullheight=False):
    data = waveform.get_data()

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
        text(0.02, 0.1, waveform.get_summary(), ha='left', va='center', transform=ax.transAxes)

    # save the figure if a filename was specified
    if filename:
        plt.savefig(filename, dpi=300)

    # show the plot
    if not suppress:
        plt.show()



# ieee_par_1789_graphic(data=[(120, 1, 'Test'), (60, 0.6, 'Test2')], min_pct=0.1)
    