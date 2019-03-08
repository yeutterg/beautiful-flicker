import csv

import numpy as np

from scipy.signal import savgol_filter, blackmanharris

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


def frequency(data):
    # Get the frame rate
    framerate = int(round(1/(data[1,0]-data[0,0])))

    # Compute Fourier transform of windowed signal
    windowed = data[:,1] * blackmanharris(len(data[:,1]))
    f = np.fft.rfft(windowed)

    # Find the peak and interpolate to get a more accurate peak
    i = np.argmax(abs(f))  # Just use this for less-accurate, naive version
    print(parabolic(np.log(abs(f)),i))
    true_i = parabolic(np.log(abs(f)), i)[0]

    # Convert to equivalent frequency
    return framerate * true_i / len(windowed)


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
    return None


"""
From https://gist.github.com/endolith/255291
"""
def parabolic(f, x):
    """Quadratic interpolation for estimating the true position of an
    inter-sample maximum when nearby samples are known.
   
    f is a vector and x is an index for that vector.
   
    Returns (vx, vy), the coordinates of the vertex of a parabola that goes
    through point x and its two neighbors.
   
    Example:
    Defining a vector f with a local maximum at index 3 (= 6), find local
    maximum if points 2, 3, and 4 actually defined a parabola.
   
    In [3]: f = [2, 3, 1, 6, 4, 2, 3, 1]
   
    In [4]: parabolic(f, argmax(f))
    Out[4]: (3.2142857142857144, 6.1607142857142856)
   
    """
    xv = 1/2. * (f[x-1] - f[x+1]) / (f[x-1] - 2 * f[x] + f[x+1]) + x
    yv = f[x] - 1/4. * (f[x-1] - f[x+1]) * (xv - x)
    return (xv, yv)
    