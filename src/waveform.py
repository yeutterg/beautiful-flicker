import csv

import numpy as np

from scipy.signal import savgol_filter, blackmanharris, argrelextrema
from scipy.integrate import simps


class Waveform:
    def __init__(self, filename):
        self.data = import_waveform_csv(filename)
        self.data = denoise(self.data)
        self.framerate = get_framerate(self.data)
        self.v_max = self.data[:,1].max()
        self.v_min = self.data[:,1].min()
        self.v_pp = self.v_max - self.v_min
        self.v_avg = np.mean([self.v_max, self.v_min])  
        self.frequency = frequency(self.data, self.framerate, self.v_avg)
        self.period = 1 / self.frequency
        self.one_period = self.get_n_periods()
        self.flicker_index = self.get_flicker_index()
        self.percent_flicker = percent_flicker(self.v_max, self.v_min)


    """
    Shortens the data to n periods

    :param num_periods:     The number of periods to return
    :returns:               The waveform truncated to the specified periods
    """
    def get_n_periods(self, num_periods=1):
        # Slice the array to the first period (so we can find the rising edge average)
        t_0 = self.data[0,0]
        delta = self.data[1,0] - t_0
        idx_1 = int(self.period / delta)
        t_1 = self.data[idx_1,0]
        
        # Find the first instance of the average
        idx_avg = find_nearest_idx_rising(self.data[:,1], self.v_avg)

        # Slice the array to the number of periods and return
        return self.data[idx_avg:idx_avg+num_periods*idx_1,:]


    """
    Gets the flicker index

    :returns:       The flicker index
    """
    def get_flicker_index(self):
        # Split the curve across the average
        curve_top = [i if i > self.v_avg else self.v_avg for i in self.one_period[:,1]]

        # Subtract the average from the top curve
        curve_top = curve_top - self.v_avg

        # Get the area under the curve for the top and all using Simpson's rule
        area_top = simps(curve_top)
        area_all = simps(self.one_period[:,1])

        # Return the flicker index 
        return area_top / area_all



"""
Imports a waveform from a CSV file

Note: Format should be [time(seconds), volts] and header info should be removed

:param filename:    The name of the CSV file
:returns:           A 2D numpy array in the format [time(seconds), volts]
"""
def import_waveform_csv(filename:str) -> np.array:
    return np.genfromtxt(filename, delimiter=',')


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

:param data:        The waveform
:param framerate:   The frame rate (samples per second)
:param v_avg:       The average voltage
:returns:           The frequency, in Hz
"""
def frequency(data, framerate, v_avg):
    # Center the data on zero
    zdata = data[:,1] - v_avg

    # Count the zero crossings
    zero_crossings = np.where(np.diff(np.sign(zdata)))[0]

    # Linear interpolation
    return framerate / np.mean(np.diff(zero_crossings)) / 2


"""
Computes the percent flicker

:param v_max:   The max voltage
:param v_pp:    The peak-to-peak voltage
:returns:       The flicker percentage
"""
def percent_flicker(v_max, v_pp):
    return v_pp / v_max * 100
