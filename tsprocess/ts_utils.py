"""
ts_utils.py
====================================
The core module for timeseries helper functions.
"""

import math
import inspect
from math import radians, cos, sin, asin, sqrt, atan2

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

   
def haversine(lat1, lon1, lat2, lon2):
    """ Computes distance of two geographical points.
    
    Inputs:
        | lat and lon for point 1 and point 2
    Outputs:
        | distance betwee two points in km.
    
     """
    # convert decimal degrees to radians 
    # this method is also defined in station module which returns meters.
   
    try:
        lon1, lat1, lon2, lat2 = map(radians, [lon1, lat1, lon2, lat2])
    except Exception:
        return None
    # haversine formula 
    dlon = lon2 - lon1 
    dlat = lat2 - lat1 
    a = sin(dlat/2)**2 + cos(lat1) * cos(lat2) * sin(dlon/2)**2
    c = 2 * asin(sqrt(a)) 
    r = 6371 # in kilometers
    return c * r

def compute_azimuth(lat1, lon1, lat2, lon2):
    """ Computes azimuth from point one to point2.
    
    Inputs:
        | lat and lon for point 1 and point 2
    Outputs:
        | azimuth from point1 to point2.
    
    Examples:

    >>> p1 = [37.577019, -112.561856]
    >>> p2 = [37.214750, -117.545706]
    >>> az = compute_azimuth(p1[0], p1[1], p2[0], p2[1])
    >>> print(f"{az :0.5f}")
    266.28959
    """

    try:
        lon1, lat1, lon2, lat2 = map(radians, [lon1, lat1, lon2, lat2])
    except Exception:
        return None

    y = sin(lon2 - lon1) * cos(lat2)
    x = cos(lat1)*sin(lat2) - sin(lat1)*cos(lat2)*cos(lon2-lon1)
    t1 = atan2(y, x)
    deg = (t1*180/math.pi + 360) % 360
    
    return deg


def rotate_record(record, rotation_angle):
    """ Rotates a given record instance by rotation angle
    
    Input:
        record: instance of Record class
        rotation_angle: rotation angle in degrees

    Output:
        rotated record instane        
    """


    # Check rotation angle
    if rotation_angle is None:
        # Nothing to do!
        return record

    
    # check if rotateion angle is valid.
    if rotation_angle < 0 or rotation_angle > 360:
        LOGGER.error(f"Rotation angle is not valid {rotation_angle:f}."
         "Command ignored.")
        return record

    # these info should be read from records:
    x = record.hc_or1
    y = record.hc_or2

    # Make sure channels are ordered properly
    if x > y:
        # This should never happen.
        LOGGER.error("there is a problem with orientaiton ordering."
         "Command ignored.")
        return record

        # Swap channels
        # I think swaping channels may cause unknown bugs in the longrun
        # temp = station[0]
        # station[0] = station[1]
        # station[1] = temp

    # Calculate angle between two components
    angle = round(y - x,2)


    # We need two orthogonal channels
    if abs(angle) != 90 and abs(angle) != 270:
        LOGGER.error("Rotation needs two orthogonal channels!"
         "Command ignored.")
        return record
    
        # Create rotation matrix
    if angle == 90:
        matrix = np.array([(math.cos(math.radians(rotation_angle)),
                            -math.sin(math.radians(rotation_angle))),
                           (math.sin(math.radians(rotation_angle)),
                            math.cos(math.radians(rotation_angle)))])
    else:
        # Angle is 270!
        matrix = np.array([(math.cos(math.radians(rotation_angle)),
                            +math.sin(math.radians(rotation_angle))),
                           (math.sin(math.radians(rotation_angle)),
                            -math.cos(math.radians(rotation_angle)))])
    
    rc_dis_1 = record.disp_h1.value.copy()
    rc_dis_2 = record.disp_h2.value.copy()
    rc_dis_v = record.disp_ver.value.copy()
    
    rc_vel_1 = record.vel_h1.value.copy()
    rc_vel_2 = record.vel_h2.value.copy()
    rc_vel_v = record.vel_ver.value.copy()
    
    rc_acc_1 = record.acc_h1.value.copy()
    rc_acc_2 = record.acc_h2.value.copy()
    rc_acc_v = record.acc_ver.value.copy()

    # Make sure they all have the same number of points
   
    # find the shortest timeseries and cut others based on that. 

    n_points = min(len(rc_dis_1), len(rc_dis_2), len(rc_dis_v),
                   len(rc_vel_1), len(rc_vel_2), len(rc_vel_v),
                   len(rc_acc_1), len(rc_acc_2), len(rc_acc_v),
                   len(record.time_vec))

    rcs_tmp = np.array([rc_dis_1,rc_dis_2,rc_dis_v,
                   rc_vel_1,rc_vel_2,rc_vel_v,
                   rc_acc_1,rc_acc_2,rc_acc_v, record.time_vec])
    
    rcs = rcs_tmp[:,0:n_points]
   
    # Rotate
    [rcs_dis_1, rcs_dis_2] = matrix.dot([rcs[0], rcs[1]])
    [rcs_vel_1, rcs_vel_2] = matrix.dot([rcs[3], rcs[4]])
    [rcs_acc_1, rcs_acc_2] = matrix.dot([rcs[6], rcs[7]])

    # Compute the record orientation        
    n_hc_or1 = record.hc_or1 - rotation_angle
    n_hc_or2 = record.hc_or2 - rotation_angle
    
    if n_hc_or1 < 0:
        n_hc_or1 = 360 + n_hc_or1

    if n_hc_or2 < 0:
        n_hc_or2 = 360 + n_hc_or2

    
    return  (rcs[9],  rcs_dis_1, rcs_dis_2, rcs[2],
                        rcs_vel_1, rcs_vel_2, rcs[5],
                        rcs_acc_1, rcs_acc_2, rcs[8],
                        record.station, record.source_params,
                        n_hc_or1, n_hc_or2)