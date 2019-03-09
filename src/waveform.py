import csv
import numpy as np
from scipy.signal import savgol_filter, blackmanharris, argrelextrema
from scipy.integrate import simps
from .utils import round_output
from .plot import waveform_graph

class Waveform:
    def __init__(self, filename, name):
        self.name = name
        self.data = import_waveform_csv(filename)
        self.data = denoise(self.data)
        self.framerate = framerate(self.data)
        self.v_max = self.data[:,1].max()
        self.v_min = self.data[:,1].min()
        self.v_pp = self.v_max - self.v_min
        self.v_avg = np.mean([self.v_max, self.v_min])  
        self.frequency = frequency(self.data, self.framerate, self.v_avg)
        self.period = 1 / self.frequency
        self.one_period = n_periods(self.data, self.v_avg, self.period, num_periods=1)
        self.flicker_index = flicker_index(self.one_period, self.v_avg)
        self.percent_flicker = percent_flicker(self.v_max, self.v_min)


    def get_name(self):
        return self.name

    def get_data(self):
        return self.data

    def get_framerate(self):
        return self.framerate

    def get_v_max(self, rounded=True, digits=2):
        return round_output(self.v_max, rounded, digits)

    def get_v_min(self, rounded=True, digits=2):
        return round_output(self.v_min, rounded, digits)

    def get_v_pp(self, rounded=True, digits=2):
        return round_output(self.v_pp, rounded, digits)

    def get_v_avg(self, rounded=True, digits=2):
        return round_output(self.v_avg, rounded, digits)

    def get_frequency(self, rounded=True, digits=1):
        return round_output(self.frequency, rounded, digits)

    def get_period(self):
        return self.period

    def get_one_period(self):
        return self.one_period

    def get_n_periods(self, num_periods=1):
        if num_periods == 1:
            return self.one_period
        else:
            return n_periods(self.data, self.v_avg, self.period, num_periods)

    def get_percent_flicker(self, rounded=True, digits=1):
        return round_output(self.percent_flicker, rounded, digits)

    def get_flicker_index(self, rounded=True, digits=1):
        return round_output(self.flicker_index, rounded, digits)

    def plot(self, num_periods=None, filename=None, showstats=True, fullheight=False):
        return waveform_graph(waveform=self, num_periods=num_periods, filename=filename, showstats=showstats, \
                              fullheight=fullheight)

    def get_summary(self, verbose=False, format='String', rounded=True):
        if format == 'String':
            out = "Frequency: " + str(self.get_frequency(rounded=rounded)) + " Hz\n" + \
                "Percent Flicker: " + str(self.get_percent_flicker(rounded)) + "%\n" + \
                "Flicker Index: " + str(self.get_flicker_index(rounded))

            if verbose:
                out += "\nPeriod: " + str(self.get_period()) + " s\n" + \
                    "Frame Rate: " + '{:,}'.format(self.get_framerate()) + " samples per second\n" + \
                    "V_min: " + str(self.get_v_min(rounded)) + " V\n" + \
                    "V_max: " + str(self.get_v_max(rounded)) + " V\n" + \
                    "V_avg: " + str(self.get_v_avg(rounded)) + " V\n" + \
                    "V_pp: " + str(self.get_v_pp(rounded)) + " V"

        elif format == 'Dict':
            out = {}
            out['name'] = self.get_name()
            out['frequency'] = self.get_frequency(rounded)
            out['percent flicker'] = self.get_percent_flicker(rounded)
            out['flicker index'] = self.get_flicker_index(rounded)

            if verbose:
                out['period'] = self.get_period()
                out['frame rate'] = self.get_framerate()
                out['v_min'] = self.get_v_min(rounded)
                out['v_max'] = self.get_v_max(rounded)
                out['v_avg'] = self.get_v_avg(rounded)
                out['v_pp'] = self.get_v_pp(rounded)

        else:
            out = 'Unidentified data format'

        return out


"""
Imports a waveform from a CSV file

Note: Format should be [time(seconds), volts] and header info should be removed

:param filename:    The name of the CSV file
:returns:           A 2D numpy array in the format [time(seconds), volts]
"""
def import_waveform_csv(filename:str) -> np.array:
    # Import from the file
    data = np.genfromtxt(filename, delimiter=',')

    # Set the time axis to 0
    t_0 = data[0,0]
    data[:,0] -= t_0 

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
def framerate(data):
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


"""
Gets the flicker index

:param one_period:      One period of the waveform
:param v_avg:           The average voltage
:returns:               The flicker index
"""
def flicker_index(one_period, v_avg):
    # Split the curve across the average
    curve_top = [i if i > v_avg else v_avg for i in one_period[:,1]]

    # Subtract the average from the top curve
    curve_top = curve_top - v_avg

    # Get the area under the curve for the top and all using Simpson's rule
    area_top = simps(curve_top)
    area_all = simps(one_period[:,1])

    # Return the flicker index 
    return area_top / area_all


"""
Returns a truncated waveform shortened to n periods

:param data:            The waveform
:param v_avg:           The average voltage
:param period:          The period in seconds
:param num_periods:     The number of periods to return
:returns:               The waveform truncated to the specified periods
"""
def n_periods(data, v_avg, period, num_periods=1):
    # Slice the array to the first period (so we can find the rising edge average)
    t_0 = data[0,0]
    delta = data[1,0] - t_0
    idx_1 = int(period / delta)
    t_1 = data[idx_1,0]
    
    # Find the first instance of the average
    idx_avg = find_nearest_idx_rising(data[:,1], v_avg)

    # Slice the array to the number of periods and return
    return data[idx_avg:idx_avg+num_periods*idx_1,:]
