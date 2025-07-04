"""Handles Flicker Waveform Data

The classes and methods contained herein allow you to generate flicker waveforms and 
perform relevant calculations, including flicker index, frequency, and percent. 
Plots can also be generated directly from the waveform.

For single waveforms: It is recommended to simply create instances of the Waveform class, 
as opposed to using methods outside the class, as this will automatically perform all necessary
calculations on initialization. In addition, class methods are easily callable
(e.g. Waveform.plot(), Waveform.get_frequency())

For multiple waveforms: It is recommended to import a whole directory using instances of
the WaveformCollection class.

The classes are:

    * Waveform - A class used to represent a flicker waveform
    * WaveformCollecion - A class used to quickly import and contain multiple Waveforms

The functions are:

    * import_waveform_csv - Imports a waveform from a CSV file, typically produced by an oscilloscope
    * import_directory - Imports all valid waveforms from the CSV files in the directory (and subdirectories)
    * get_files_in_directory - Gets the paths and filenames of all files in the directory (and subdirectories)
    * get_names_in_waveform_list - Gets the names of all Waveform objects in a list of Waveforms
    * denoise - Applies the Savitzky-Golay Filter to remove noise
    * framerate - Gets the frame rate (samples per second) of the data
    * find_nearest_idx - Finds the index of the nearest value in an array
    * find_nearest_idx_rising - Finds the closest rising-edge value in a 1D array
    * frequency - Calculates the dominant frequency of the waveform
    * percent_flicker - Computes the flicker percentage of the waveform
    * flicker_index - Gets the flicker index of the waveform
    * n_periods - Truncates a waveform to n periods
"""

import numpy as np
from os import walk
from scipy.signal import savgol_filter, butter, filtfilt
try:
    from scipy.integrate import simpson
except ImportError:
    # Fallback for older scipy versions
    from scipy.integrate import simps as simpson
from .utils import round_output, bool_to_pass_fail
from .plot import waveform_graph
from .standards import well_building_standard_v2, california_ja8_2019, ieee_1789_2015


class Waveform:
    """A class used to represent a flicker waveform

    This class should be used in lieu of the other functions in this file, as all 
    necessary computations are completed in initialization (waveform import from CSV)
    and class methods are easily callable (e.g. Waveform.plot(), Waveform.get_frequency())

    Attributes
    ----------
    name : str
        The name of the waveform. Use this to keep track of multiple waveforms and for plotting
    data : ndarray
        The 2D array holding waveform data. Format is [time(seconds):float, voltage:float]
    denoised : bool
        Whether or not the waveform has been filtered to remove noise
    framerate : int
        The number of samples per second of the waveform
    v_max : float
        The maximum voltage
    v_min : float
        The minimum voltage
    v_avg : float
        The average voltage (mean of v_max and v_min)
    v_pp : float
        The peak-to-peak voltage (v_max - v_min)
    frequency : float
        The dominant flicker frequency, in Hertz
    period : float
        The period (1 / frequency), in seconds
    one_period : ndarray
        A 2D array containing just one period of the waveform. 
        Format is [time(seconds):float, voltage:float]
    flicker_index : float
        The flicker index of the waveform
    percent_flicker : float
        The percent flicker of the waveform
    ieee_1789_2015 : str
        Whether this waveform complies with IEEE 1789-2015
    well_standard_v2 : bool
        Whether this waveform complies with WELL v2 L7
    california_ja8_2019 : bool
        Whether this waveform complies with California JA8 2019

    Methods
    -------
    rename(new_name)
        Renames the Waveform
    get_name()
        Gets the name of this waveform instance
    get_data()
        Gets the 2D array containing waveform data
    get_framerate()
        Gets the framerate (samples per second) of the data
    get_denoised()
        Whether this waveform has been filtered for noise
    get_v_max(rounded=True, digits=2)
        Gets the maximum voltage of this waveform instance
    get_v_min(rounded=True, digits=2)
        Gets the minimum voltage of this waveform instance
    get_v_pp(rounded=True, digits=2)
        Gets the peak-to-peak voltage of this waveform instance
    get_v_avg(rounded=True, digits=2)
        Gets the average voltage of this waveform instance
    get_frequency(rounded=True, digits=1)
        Gets the flicker frequency of this waveform instance
    get_period()
        Gets the period of one oscillation of this waveform instance
    get_one_period()
        Gets the 2D array containing one period of the waveform data
    get_n_periods(num_periods=1)
        Gets the 2D array containing the specified number of periods in the waveform data
    get_percent_flicker(rounded=True, digits=1)
        Gets the percent flicker of this instance of the waveform
    get_flicker_index(rounded=True, digits=1)
        Gets the flicker index of this instance of the waveform
    plot(num_periods=None, filename=None, showstats=True, fullheight=False, figsize=(8,4))
        Plots the time-series waveform graphic
    summary(verbose=False, format='String', rounded=True)
        Returns a summary of the parameters of this waveform instance
    get_ieee_1789_2015()
        Whether this waveform complies with the IEEE 1789-2015 flicker requirements
    get_well_standard_v2()
        Whether this waveform complies with the WELL v2 L7 flicker requirements
    get_california_ja8_2019()
        Whether this waveform complies with the California JA8 2019 flicker requirements
    """

    def __init__(self, filename:str, name:str, remove_noise:bool=True):
        """Initializes this Waveform instance and automatically computes all values

        Parameters
        ----------
        filename : str
            The name of the CSV file to import
        name : str
            The name of the waveform. Use this to keep track of multiple waveforms and for plotting
        remove_noise : bool
            If True (default), data will be automatically denoised
            If False, data will not be denoised
        """

        try: 
            self.name = name
            self.data = import_waveform_csv(filename)
            if remove_noise:
                self.data = denoise(self.data)
                self.denoised = True
            else:
                self.denoised = False
            self.framerate = framerate(self.data)
            self.v_max = self.data[:,1].max()
            self.v_min = self.data[:,1].min()
            self.v_pp = self.v_max - self.v_min
            self.v_avg = np.mean([self.v_max, self.v_min])  
            self.frequency = frequency(self.data, self.framerate, self.v_avg)
            self.period = 1 / self.frequency
            self.one_period = n_periods(self.data, self.v_avg, self.period, num_periods=1)
            self.flicker_index = flicker_index(self.one_period, self.v_avg)
            self.percent_flicker = percent_flicker(self.v_max, self.v_pp)
            self.ieee_1789_2015 = ieee_1789_2015(self.frequency, self.percent_flicker)
            self.well_standard_v2 = well_building_standard_v2(self.frequency, self.percent_flicker)
            self.california_ja8_2019 = california_ja8_2019(self.frequency, self.percent_flicker)
        except Exception as e:
            print('WARNING: Could not import waveform at file location ' + filename)
            print(e)
            self = None


    # Setters:

    def rename(self, new_name):
        """Renames the Waveform

        Parameters
        ----------
        new_name : str
            The new name of this Waveform instance
        """

        self.name = new_name

    # Getters:

    def get_name(self) -> str:
        """Gets the name of this Waveform instance

        Returns
        -------
        str
            The name of this Waveform instance
        """

        return self.name


    def get_data(self) -> np.ndarray:
        """Gets the 2D array containing waveform data

        Returns
        -------
        ndarray
            The 2D array holding waveform data. Format is [time(seconds):float, voltage:float]
        """

        return self.data


    def get_framerate(self) -> int:
        """Gets the framerate (samples per second) of the data

        Returns
        -------
        int
            The number of samples per second of the waveform
        """

        return self.framerate


    def get_denoised(self) -> bool:
        """Whether this waveform has been filtered for noise

        Returns
        -------
        bool
            True if the waveform has been denoised, False if not
        """

        return self.denoised


    def get_v_max(self, rounded:bool=True, digits:int=2) -> float:
        """Gets the maximum voltage of this waveform instance

        Parameters
        ----------
        rounded : bool
            If True (default), will round the output
            If False, will not round the output
        digits : int
            The number of decimal points to round to

        Returns
        -------
        float
            The max voltage
        """

        return round_output(self.v_max, rounded, digits)


    def get_v_min(self, rounded:bool=True, digits:int=2) -> float:
        """Gets the minimum voltage of this waveform instance

        Parameters
        ----------
        rounded : bool
            If True (default), will round the output
            If False, will not round the output
        digits : int
            The number of decimal points to round to

        Returns
        -------
        float
            The min voltage
        """

        return round_output(self.v_min, rounded, digits)


    def get_v_pp(self, rounded:bool=True, digits:int=2) -> float:
        """Gets the peak-to-peak voltage of this waveform instance

        Peak-to-peak voltage is v_max - v-min

        Parameters
        ----------
        rounded : bool
            If True (default), will round the output
            If False, will not round the output
        digits : int
            The number of decimal points to round to

        Returns
        -------
        float
            The peak-to-peak voltage
        """

        return round_output(self.v_pp, rounded, digits)


    def get_v_avg(self, rounded:bool=True, digits:int=2) -> float:
        """Gets the average voltage of this waveform instance

        Average voltage is the mean of v_max and v_min

        Parameters
        ----------
        rounded : bool
            If True (default), will round the output
            If False, will not round the output
        digits : int
            The number of decimal points to round to

        Returns
        -------
        float
            The average voltage
        """

        return round_output(self.v_avg, rounded, digits)


    def get_frequency(self, rounded:bool=True, digits:int=1) -> float:
        """Gets the flicker frequency of this waveform instance

        Parameters
        ----------
        rounded : bool
            If True (default), will round the output
            If False, will not round the output
        digits : int
            The number of decimal points to round to

        Returns
        -------
        float
            The flicker frequency in Hertz
        """

        return round_output(self.frequency, rounded, digits)


    def get_period(self) -> float:
        """Gets the period of one oscillation of this waveform instance

        Returns
        -------
        float
            The period in seconds
        """

        return self.period


    def get_one_period(self) -> np.ndarray:
        """Gets the 2D array containing one period of the waveform data

        Returns
        -------
        ndarray
            The 2D array holding one period of the waveform. 
            Format is [time(seconds):float, voltage:float]
        """

        return self.one_period


    def get_n_periods(self, num_periods:int=1) -> np.ndarray:
        """Gets the 2D array containing the specified number of periods in the waveform data

        Parameters
        ----------
        num_periods : int
            The number of periods to return.
            NOTE: Must be fewer than the number of periods in the input data

        Returns
        -------
        ndarray
            The 2D array holding the specified number of periods of the waveform data. 
            Format is [time(seconds):float, voltage:float]
        """

        if num_periods == 1:
            return self.one_period
        else:
            return n_periods(self.data, self.v_avg, self.period, num_periods)


    def get_percent_flicker(self, rounded:bool=True, digits:int=1) -> float:
        """Gets the percent flicker of this instance of the waveform

        Parameters
        ----------
        rounded : bool
            If True (default), will round the output
            If False, will not round the output
        digits : int
            The number of decimal points to round to

        Returns
        -------
        float
            The percent flicker (will be in the format XX.XXXX, NOT 0.XXXXXX)
        """

        return round_output(self.percent_flicker, rounded, digits)


    def get_flicker_index(self, rounded:bool=True, digits:int=2) -> float:
        """Gets the flicker index of this instance of the waveform

        Parameters
        ----------
        rounded : bool
            If True (default), will round the output
            If False, will not round the output
        digits : int
            The number of decimal points to round to

        Returns
        -------
        float
            The flicker index
        """

        return round_output(self.flicker_index, rounded, digits)


    def get_ieee_1789_2015(self) -> str:
        """Whether this waveform complies with the IEEE 1789-2015 flicker requirements

        Returns
        -------
        str
            Either of: "No Risk", "Low Risk", "High Risk"
        """

        return self.ieee_1789_2015


    def get_well_standard_v2(self) -> bool:
        """Whether this waveform complies with the WELL v2 L7 flicker requirements

        Returns
        -------
        bool
            True if the waveform passes, False if not
        """

        return self.well_standard_v2


    def get_california_ja8_2019(self) -> bool:
        """Whether this waveform complies with the California JA8 2019 flicker requirements

        Returns
        -------
        bool
            True if the waveform passes, False if not
        """

        return self.california_ja8_2019

    
    def plot_extrapolated(self, time_ms:int=None, filename:str=None, showstats:bool=True, figsize:tuple=(8,4)):

        (ext_data, _) = extrapolate(self.one_period, self.v_pp, self.framerate, time_ms=time_ms)

        waveform_graph(waveform=self, data=ext_data, filename=filename, \
                       showstats=showstats, fullheight=True, figsize=figsize)


    def plot(self, num_periods:int=None, filename:str=None, showstats:bool=True, 
             fullheight:bool=False, figsize:tuple=(8,4)):
        """
        Plots the time-series waveform graphic

        Parameters
        ----------
        num_periods : int or None
            The number of periods to plot. If None, will show the whole waveform
        filename : str or None
            If specified, will save the file in the specified location.
            e.g.: filename='../out/this_graph.png'
            If None, the plot will not be saved
        showstats : bool
            If True, will show the flicker frequency, percent, and index on the plot
        fullheight : bool
            If True, will set the Y axis limits from 0 to 1.
            If False, will set the limits from v_min to 1
        figsize : tuple
            The (x,y) size of the figure
        """

        waveform_graph(waveform=self, num_periods=num_periods, filename=filename, showstats=showstats, \
                       fullheight=fullheight, figsize=figsize)


    def summary(self, verbose:bool=False, format:str='String', rounded:bool=True):
        """Returns a summary of the parameters of this waveform instance

        Parameters
        ----------
        verbose : bool
            If False, will display: 
                Frequency, Percent Flicker, Flicker Index (and Name for dict format)
            If True, will display all of the above, plus:
                Period, Frame Rate, V_min, V_max, V_avg, V_pp, IEEE 1789-2015, WELL v2 L7, California JA 2019
        format : str
            The format of the output, either 'String' or 'Dict'
        rounded : bool
            If True (default), will round the output values
            If False, will not round the output values

        Returns
        -------
        str or dict
            If format = 'String': A String summarizing the waveform
            If format = 'Dict': A dict summarizing the waveform
        """

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
                    "V_pp: " + str(self.get_v_pp(rounded)) + " V\n" + \
                    "IEEE 1789-2015: " + self.ieee_1789_2015 + "\n" + \
                    "WELL v2 L7: " + bool_to_pass_fail(self.well_standard_v2) + "\n" + \
                    "California JA8 2019: " + bool_to_pass_fail(self.california_ja8_2019)

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
                out['IEEE 1789-2015'] = self.ieee_1789_2015
                out['WELL v2 L7'] = self.well_standard_v2
                out['California JA8 2019'] = self.california_ja8_2019

        else:
            out = 'Unidentified data format'

        return out


class WaveformCollection():
    """A class used to quickly import and contain multiple Waveforms

    This class is initialized by specifying a path containing waveform CSVs. All valid waveforms
    in the directories (and subdirectories) will be imported. The names of all imported waveforms
    are available via get_names(), and you can get a specific waveform by calling get('Name of waveform')

    Attributes
    ----------
    waveforms : list
        A list of Waveform objects
    names : list
        The names of all the Waveform objects in the collection

    Methods
    -------
    get_names()
        Returns a list of the names of this waveforms in the collection
    get_waveforms()
        Returns a list of the Waveform objects in the collection
    get(name)
        Returns a Waveform based on its name
    """

    def __init__(self, path):
        """Initializes this WaveformCollection

        Parameters
        ----------
        path : str
            The path to the directory where the waveform CSVs are located
        """

        self.waveforms = import_directory(path)
        self.names = get_names_in_waveform_list(self.waveforms)


    def get_names(self) -> list:
        """Returns a list of the names of this waveforms in the collection

        Returns
        -------
        list
            A list of names of the waveforms in this collection
        """

        return self.names


    def get_waveforms(self) -> list:
        """Returns a list of the Waveform objects in the collection

        Returns
        -------
        list
            A list of Waveform objects in this collection
        """

        return self.waveforms


    def get(self, name:str) -> Waveform:
        """Returns a Waveform based on its name

        Parameters
        ----------
        name : str
            The name of the Waveform

        Returns
        -------
        Waveform
            The Waveform object
        """

        for w in self.waveforms:
            if w.get_name() == name:
                return w


def import_waveform_csv(filename:str) -> np.ndarray:
    """Imports a waveform from a CSV file, typically produced by an oscilloscope

    NOTE: Format should be [time(seconds), volts] and header info should be removed

    Parameters
    ----------
    filename : str
        The name of the CSV file

    Returns
    -------
    ndarray
        A 2D numpy array in the format [time(seconds), volts]    
    """

    # Import from the file
    data = np.genfromtxt(filename, delimiter=',', dtype=None)

    # Set the time axis to 0
    t_0 = data[0,0]
    data[:,0] -= t_0 

    return data


def import_directory(dir:str) -> list:
    """Imports all valid waveforms from the CSV files in the directory (and subdirectories)

    NOTE: For each file, format should be [time(seconds), volts] and header info should be removed

    Parameters
    ----------
    dir : str
        The path to the directory

    Returns
    -------
    list
        A list of the Waveform objects imported    
    """

    # Get all the files in this directory (including subdirectories)
    (filenames, paths) = get_files_in_directory(dir)

    # Import the waveforms
    waveforms = []
    for i, f in enumerate(filenames):
        w = Waveform(paths[i], f)
        if w is not None:
            waveforms.append(w)

    return waveforms

    
def get_files_in_directory(dir:str) -> tuple:
    """Gets the paths and filenames of all files in the directory (and subdirectories)

    Parameters
    ----------
    dir : str
        The path to the directory

    Returns
    -------
    tuple
        (The file names with formatting and extensions removed, the path to the file including filename)
    """

    names = []
    paths = []

    for (dirpath, dirnames, filenames) in walk(dir):
        # Add the files in this directory
        for f in filenames:
            # Add a / if not at the end of the path (for subdirectories)
            if dirpath[-1] != '/':
                dirpath += '/'

            # Append the file, unless it is a system/hidden file like .DS_Store
            if f[0] != '.':
                # Append the file with its path
                paths.append(dirpath + f)

                # Format the string to remove the format and underscores
                f = f.split('.')[0]
                f = f.replace('_', ' ')
                names.append(f)
                
    return (names, paths)


def get_names_in_waveform_list(waveform_list) -> list:
    """Gets the names of all Waveform objects in a list of Waveforms

    Parameters
    ----------
    waveform_list : list
        A list of Waveform objects

    Returns
    -------
    list
        A list of the names of the Waveform objects in waveform_list
    """

    names = []

    for w in waveform_list:
        names.append(w.get_name())

    return names


def denoise(data:np.ndarray, window_length:int=901) -> np.ndarray:
    """Applies the Savitzky-Golay Filter to remove noise

    Parameters
    ----------
    data : ndarray
        The waveform data as a 2D array
    window_length : int
        The window length for the filter. Higher equals more smoothing

    Returns
    -------
    ndarray
        The waveform with noise removed
    """

    data2 = np.copy(data)
    filter_order = 3
    data2[:,1] = savgol_filter(data2[:,1], window_length, filter_order)
    return data2


def framerate(data:np.ndarray) -> int:
    """Gets the frame rate (samples per second) of the data

    Parameters
    ----------
    data : ndarray
        The waveform data as a 2D array

    Returns
    -------
    int
        The number of samples per second in the data
    """
    return int(round(1/(data[1,0]-data[0,0])))


def find_nearest_idx(array:np.ndarray, value:float) -> int:
    """Finds the index of the nearest value in an array

    Parameters
    ----------
    array : ndarray
        A 1D array to search
    value : float
        The closest value to search for in the array

    Returns
    -------
    int
        The first index of the array value that is closest to the search value
    """

    return (np.abs(array-value)).argmin()


def find_nearest_idx_rising(array:np.ndarray, value:float) -> int:
    """Finds the closest rising-edge value in a 1D array
    
    This function is primarily used to find the start of a period.
    It recursively calls find_nearest_index()

    Parameters
    ----------
    array : ndarray
        A 1D array to search
    value : float
        The closest value to search for in the array

    Returns
    -------
    int
        The first index of the array value that is both closest to the search value and on a rising edge
    """

    idx = find_nearest_idx(array, value)

    if array[idx] > array[idx-1] and array[idx] < array[idx+1]:
        # Got a rising edge, return
        return idx
    else:
        # Slice the array so we can find the next index
        new_array = array[idx+1:]

        # Recursively run this function until a rising edge is found
        return find_nearest_idx_rising(new_array, value)


def frequency(data:np.ndarray, framerate:int, v_avg:float) -> float:
    """Calculates the dominant frequency of the waveform
    
    Uses the zero-crossing method for fast and accurate frequency calculation

    Parameters
    ----------
    data : ndarray
        The waveform data as a 2D array
    framerate : int
        The frame rate (samples per second)
    v_avg : float
        The average voltage

    Returns
    -------
    float
        The frequency in Hertz
    """

    # Center the data vertically on zero
    zdata = data[:,1] - v_avg

    # Count the zero crossings
    zero_crossings = np.where(np.diff(np.sign(zdata)))[0]

    # Estimate the frequency
    est_freq = round(framerate / np.mean(np.diff(zero_crossings)) / 2)

    # For now, round everything in the range 115-130 Hz to 120 Hz
    if est_freq >= 115 and est_freq <= 130:
        est_freq = 120.0

    return est_freq


def percent_flicker(v_max:float, v_pp:float) -> float:
    """Computes the flicker percentage of the waveform

    Parameters
    ----------
    v_max : float
        The max voltage
    v_pp : float
        The peak-to-peak voltage
    
    Returns
    -------
    float
        The flicker percentage
    """

    return v_pp / v_max * 100


def flicker_index(one_period:np.ndarray, v_avg:float) -> float:
    """Gets the flicker index of the waveform

    Parameters
    ----------
    one_period : ndarray
        One period of the waveform as a 2D array
    v_avg : float
        The average voltage

    Returns
    -------
    float
        The flicker index
    """

    # Split the curve across the average
    curve_top = [i if i > v_avg else v_avg for i in one_period[:,1]]

    # Subtract the average from the top curve
    curve_top = curve_top - v_avg

    # Get the area under the curve for the top and all using Simpson's rule
    area_top = simpson(curve_top)
    area_all = simpson(one_period[:,1])

    # Return the flicker index 
    return area_top / area_all


def n_periods(data:np.ndarray, v_avg:float, period:float, num_periods:int=1) -> np.ndarray:
    """Truncates a waveform to n periods

    NOTE: The number of periods must be shorter than the input waveform

    Parameters
    ----------
    data : ndarray
        The waveform data as a 2D array
    v_avg : float
        The average voltage
    period : float
        The period in seconds
    num_periods : int
        The number of periods to return

    Returns
    -------
    ndarray
        The waveform truncated to the specified number of periods    
    """

    # Slice the array to the first period (so we can find the rising edge average)
    data = np.copy(data)
    t_0 = data[0,0]
    delta = data[1,0] - t_0
    idx_1 = int(period / delta)
    t_1 = data[idx_1,0]
    
    # Find the first instance of the average
    idx_avg = find_nearest_idx_rising(data[:,1], v_avg)

    # Slice the array to the number of periods
    out = data[idx_avg:idx_avg+num_periods*idx_1,:]

    # Make the time series start at 0
    min_val = out[0,0]
    out[:,0] -= min_val

    return out


def extrapolate(one_period:np.ndarray, v_pp:float, framerate:int, time_ms:int=None) -> tuple:

    if time_ms is None:
        # Get the number of periods needed to extend y axis to 0
        num_periods = int(1 / v_pp) + 1
    else:
        # Get the number of periods in the specified number of ms
        num_periods = int(framerate / 1000 * time_ms)

    # Copy the first period directly
    out_array = np.copy(one_period)
    
    for i in range(1, num_periods):
        # Get the maximum time step of the array so far, in addition the time interval
        max_out = out_array[-1,0]
        time_interval = 1 / framerate

        # Make a new period picking up at the end of the previous maximum time step
        new_period = np.copy(one_period)
        new_period[:,0] += (max_out + time_interval)

        # Stack the output array so far with the 
        out_array = np.vstack((out_array, new_period))  

    return (out_array, num_periods)
