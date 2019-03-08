import csv

import numpy as np

from scipy.signal import savgol_filter, blackmanharris, argrelextrema

"""
Imports a waveform CSV showing the 

Note: skips the first line. Format should be [time, volt]
"""
def import_waveform_csv(filename:str, horizontal_units='us', horizontal_scale=2000,
                        vertical_scale_volts=0.20, vertical_offset=0.0,
                        sample_interval=0.0000000020000) -> np.array:
    
    data = np.genfromtxt(filename, delimiter=',')
    return data
    

"""
Applies the Savitzky-Golay Filter to remove noise

:param data:            The data to denoise
:param window_length:   The window length. Higher equals more smoothing
:returns:               The denoised data
"""
def denoise(data, window_length=1001):
    data2 = np.copy(data)
    data2[:,1] = savgol_filter(data2[:,1], window_length, 2)
    return data2


"""
Gets the frame rate (samples per second) of the data

:param data:        The waveform
:returns:           The number of samples per second
"""
def get_framerate(data):
    return int(round(1/(data[1,0]-data[0,0])))


"""
Shortens the data to x periods

:param data:            The waveform
:param num_periods:     The number of periods to return
:returns:               The data truncated to the specified periods
"""
def get_periods(data, num_periods=1):
    # Get the period in seconds
    period_s = period(data)

    # Slice the array to the first period (so we can find the rising edge average)
    t_0 = data[0,0]
    delta = data[1,0] - t_0
    idx_1 = int(period_s / delta)
    t_1 = data[idx_1,0]

    # Find the average
    v_max = data[:,1].max()
    v_min = data[:,1].min()
    v_avg = np.mean([v_max, v_min])  
    
    # Find the first instance of average
    idx_avg = find_nearest_idx_rising(data[:,1], v_avg)

    # Slice the array to the number of periods and return
    return data[idx_avg:idx_avg+num_periods*idx_1,:]


"""
Finds the index of the nearest value in an array

:param array:       A 1D array to search
:param value:       The closest value to find
:returns:           The index of the array entry closest to the value
"""
def find_nearest_idx(array, value):
    return (np.abs(array-value)).argmin()


"""
Finds the index of the nearest value in an array that is also a rising edge

:param array:       A 1D array to search
:param value:       The closest value to find
:returns:           The index of the array entry closest to the value
"""
def find_nearest_idx_rising(array, value):
    idx = find_nearest_idx(array, value)

    if array[idx] > array[idx-1] and array[idx] < array[idx+1]:
        # Got a rising edge, return
        return idx
    else:
        # Slice the array so we can find the next index
        new_array = array[idx+1:]

        # Recursively run this function until a rising edge is found
        return find_nearest_idx_rising(new_array, value)


"""
Calculates the frequency by counting zero crossings

:param data:    The waveform
:returns:       The frequency, in Hz
"""
def frequency(data):
    # Get the frame rate
    framerate = get_framerate(data)

    # Get the min, max, and average
    v_max = data[:,1].max()
    v_min = data[:,1].min()
    v_avg = np.mean([v_max, v_min])  # zero crossing

    # Center the data on zero
    zdata = data[:,1] - v_avg

    # Count the zero crossings
    zero_crossings = np.where(np.diff(np.sign(zdata)))[0]

    # Linear interpolation
    return framerate / np.mean(np.diff(zero_crossings)) / 2


"""
Calculates the period

:param data:    The waveform
:returns:       The period, in seconds
"""
def period(data):
    return 1 / frequency(data)


"""
Computes the percent flicker

:param data:                The waveform
:param vertical_offset:     The vertical offset, in volts
:returns:                   The flicker percentage
"""
def pct_flicker(data, vertical_offset=0.0):
    v_max = data[:,1].max()
    v_min = data[:,1].min()
    v_pp = v_max - v_min
    v_tot = v_max - vertical_offset
    return v_pp / v_tot * 100


def flicker_index():
    # Get one period of the data


    return None

