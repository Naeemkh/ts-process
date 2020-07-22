"""
ts_utils.py
====================================
The core module for timeseries helper functions.
"""

import math
import inspect

import numpy as np
from scipy.signal import kaiser

from .log import LOGGER

def max_osc_response(acc, dt, csi, period, ini_disp, ini_vel):
    """
    Returns maximum values of displacement, velocity, and acceleration.
    
    Inputs:
        | acc: accleration input signal
        | dt:  time step
        | csi: damping ratio
        | period: oscilator's period
        | ini_disp: initial displacement
        | ini_vel: initial velocity

        | Originial version is writting by: Leonardo Ramirez-Guzman
        | TODO: this function is very slow requires some attention. 

    """
    signal_size = acc.size

    # initialize numpy arrays
    d = np.empty((signal_size))
    v = np.empty((signal_size))
    aa = np.empty((signal_size))

    d[0] = ini_disp
    v[0] = ini_vel

    w = 2*math.pi/period
    ww = w**2
    csicsi = csi**2
    dcsiw = 2*csi*w

    rcsi = math.sqrt(1-csicsi)
    csircs = csi/rcsi
    wd = w*rcsi
    ueskdt = -1/(ww*dt)
    dcsiew = 2*csi/w
    um2csi = (1-2*csicsi)/wd
    e = math.exp(-w*dt*csi)
    s = math.sin(wd*dt)
    c0 = math.cos(wd*dt)
    aa[0] = -ww*d[0]-dcsiw*v[0]

    ca = e*(csircs*s+c0)
    cb = e*s/wd
    cc = (e*((um2csi-csircs*dt)*s-(dcsiew+dt)*c0)+dcsiew)*ueskdt
    cd = (e*(-um2csi*s+dcsiew*c0)+dt-dcsiew)*ueskdt
    cap = -cb*ww
    cbp = e*(c0-csircs*s)
    ccp = (e*((w*dt/rcsi+csircs)*s+c0)-1)*ueskdt
    cdp = (1-ca)*ueskdt

    for i in range(1, signal_size):
        d[i] = ca*d[i-1]+cb*v[i-1]+cc*acc[i-1]+cd*acc[i]
        v[i] = cap*d[i-1]+cbp*v[i-1]+ccp*acc[i-1]+cdp*acc[i]
        aa[i] = -ww*d[i]-dcsiw*v[i]

    maxdisp = np.amax(np.absolute(d))
    maxvel = np.amax(np.absolute(v))
    maxacc = np.amax(np.absolute(aa))

    return maxdisp, maxvel, maxacc

def cal_acc_response(period, data, delta_t):
    """
    Returns the response for acceleration only

    Inputs:
        | period: osilator's period
        | data: acceleration input signal
        | delta_ts: time step

    """
    rsp = np.zeros(len(period))
    for i,p in enumerate(period):
        rsp[i] = max_osc_response(data, delta_t, 0.05, p, 0, 0)[-1]
    return rsp


def get_period(tmin, tmax):
    """ Return an array of period T 
    
    >>> a = get_period(0.1,10)
    >>> print(f"{a[2] :.8f}")
    0.16237767
    """

    a = np.log10(tmin)
    b = np.log10(tmax)

    period = np.linspace(a, b, 20)
    period = np.power(10, period)

    return period

def get_points(samples):
    # points is the least base-2 number that is greater than max samples
    power = int(math.log(max(samples), 2)) + 1
    return 2**power

def check_opt_param_minmax(opt_params, key):
    x_lim = None
    if opt_params.get(key, None):
        try:
            x_min, x_max = (opt_params.get(key, None))
            x_lim = [x_min, x_max]
            if x_min > x_max:
                raise ValueError
        except ValueError:
            LOGGER.error(key + " limit min should be less than max")
            x_lim = None
        except Exception as e:
            LOGGER.error(e)
            x_lim = None
    return x_lim

def smooth(data, factor):
    """
    Smooth the data in the input array

    Inputs:
        | data - input array
        | factor - used to calculate the smooth factor

    Outputs:
        | data - smoothed array
    """
    # factor = 3; c = 0.5, 0.25, 0.25
    # TODO: fix coefficients for factors other than 3
    c = 0.5 / (factor - 1)
    for i in range(1, data.size - 1):
        data[i] = 0.5 * data[i] + c * data[i - 1] + c * data[i + 1]
    return data


def FAS(data, dt, points, fmin, fmax, s_factor):
    """
    Calculates the FAS of the input array using NumPy's fft Library

    Inputs:
        | data - input array
        | dt - delta t for the input array
        | points - length of the transformed axis in the fft output
        | fmin - min frequency for results
        | fmax - max frequency for results
        | s_factor - smooth factor to be used for the smooth function
        
    Outputs:
        | freq - frequency array
        | afs - fas
    """

    afs = abs(np.fft.fft(data, points)) * dt
    freq = (1 / dt) * np.array(range(points)) / points

    deltaf = (1 / dt) / points

    inif = int(fmin / deltaf)
    endf = int(fmax / deltaf) + 1

    afs = afs[inif:endf]
    afs = smooth(afs, s_factor)
    freq = freq[inif:endf]
    return freq, afs


def taper(flag, m, ts_vec):
        """
        Returns a Kaiser window created by a Besel function
    
        Inputs:
            | flag - set to 'front', 'end', or 'all' to taper at the beginning,
                   at the end, or at both ends of the timeseries
            | m - number of samples for tapering
            | window - Taper window
        """
        samples = len(ts_vec)
    
        window = kaiser(2*m+1, beta=14)
    
        if flag == 'front':
            # cut and replace the second half of window with 1s
            ones = np.ones(samples-m-1)
            window = window[0:(m+1)]
            window = np.concatenate([window, ones])
    
        elif flag == 'end':
            # cut and replace the first half of window with 1s
            ones = np.ones(samples-m-1)
            window = window[(m+1):]
            window = np.concatenate([ones, window])
    
        elif flag == 'all':
            ones = np.ones(samples-2*m-1)
            window = np.concatenate([window[0:(m+1)], ones, window[(m+1):]])
    
        # avoid concatenate error
        if window.size < samples:
            window = np.append(window, 1)
    
        if window.size != samples:
            # print(window.size)
            # print(samples)
            print("[ERROR]: taper and data do not have the same number of\
                 samples.")
            window = np.ones(samples)
    
        return window

def seism_appendzeros(flag, t_diff, m, timeseries, delta_t):
    """
    Adds zeros in the front or at the end of an numpy array, applies taper 
    before adding zeros.

    Inputs:
        | flag - 'front' or 'end' - tapering flag passed to the taper function
        | t_diff - how much time to add (in seconds)
        | m - number of samples for tapering
        | ts_vec - Input timeseries
    
    Outputs:
        | timeseries - zero-padded timeseries.    
    """
    ts_vec = timeseries.copy()
    num = int(t_diff / delta_t)
    zeros = np.zeros(num)

    if flag == 'front':
        # applying taper in the front
        if m != 0:
            window = taper('front', m, ts_vec)
            ts_vec = ts_vec * window

        # adding zeros in front of data
        ts_vec = np.append(zeros, ts_vec)

    elif flag == 'end':
        if m != 0:
            # applying taper in the front
            window = taper('end', m, ts_vec)
            ts_vec = ts_vec * window

        ts_vec = np.append(ts_vec, zeros)

    return ts_vec

def seism_cutting(flag, t_diff, m, timeseries, delta_t):
    """
    Cuts data in the front or at the end of an numpy array
    apply taper after cutting

    Inputs:
        | flag - 'front' or 'end' - flag to indicate from where to cut samples
        | t_diff - how much time to cut (in seconds)
        | m - number of samples for tapering
        | timeseries - Input timeseries

    Outputs:
        | timeseries - Output timeseries after cutting

    """
    ts_vec = timeseries.copy()
    num = int(t_diff / delta_t)

    if num >= len(ts_vec):
        print("[ERROR]: fail to cut timeseries.")
        return timeseries

    if flag == 'front' and num != 0:
        # cutting timeseries
        ts_vec = ts_vec[num:]

        # applying taper at the front
        window = taper('front', m, ts_vec)
        ts_vec = ts_vec * window

    elif flag == 'end' and num != 0:
        num *= -1
        # cutting timeseries
        ts_vec = ts_vec[:num]

        # applying taper at the end
        window = taper('front', m, ts_vec)
        ts_vec = ts_vec * window

    return ts_vec


def is_lat_valid(lat):
    """ 
    Controls if latitude is in a valide range. 
    
    Inputs:    
        | lat: latitude in degrees
    
    Output:
        | True or False

    Example:

    >>> is_lat_valid(-130)
    False
    """
    try:
        if lat<-90 or lat>90:
            return False
    except Exception as e:
            LOGGER.error('Input is not valid for latitude ' + str(e))
            return False
    return True


def is_lon_valid(lon):
    """ 
    Controls if longitude is in a valide range. 
    
    Inputs:    
        | lat: latitude in degrees
    
    Output:
        | True or False

    Example:

    >>> is_lon_valid(122)
    True
    """
    try:
        if lon<-180 or lon>180:
            return False
    except Exception as e:
            LOGGER.error('Input is not valid for longitude '+ str(e))
            return False
    return True



def is_depth_valid(depth):
    """ 
    Controls if depth is a valid number. Depth is considered positive towards
    the earth interior.  
    
    Inputs:    
        | depth: depth in km
    
    Output:
        | True or False

    Example:

    >>> is_depth_valid('twenty')
    False
    """

    if not isinstance(depth, (float,int)):
        LOGGER.error('Input is not valid for depth. Should be a numeric value.')
        return False

    return True


def query_opt_params(opt_params, key):
    """ Returns the provided key in optional parameters dictionayr.
    Returns None if not found."""
    return opt_params.get(key, None)


def write_into_file(filepath, message):

    with open(filepath, 'a') as file1:
        for item in message:
            file1.writelines(item)


def list2message(lst):
    """ converts list of processing details into string message
    details include: 
    | file_name, list_inc, list_processing, list_station_filter, 
    station_incident dictionary
    """
    st = lst[0] 
    for i,inc in enumerate(lst[1]):
        st = st + "\n" + inc + ": "
        for j,p in enumerate(lst[2][i]):
            sep = ""
            if j != 0:
                sep = ", "
            st = st + sep + p

    st = st + "\nStation filters: "
    for j in lst[3]:
        st = st + j
    st = st + "\nStation equivalency: "
    for key, value in lst[4].items():
        st = st + key + ": " + value + " | "
    
    return st






