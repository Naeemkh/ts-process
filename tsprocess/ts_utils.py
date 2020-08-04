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

def read_data(signal):
    """
        The function is to convert signal data into an numpy array of float
        numbers

        Inputs:
            | string of numbers
        
        Outputs:
            | numpy array of numbers
    
    """
    # avoid negative number being stuck
    signal = signal.replace('-', ' -')
    signal = signal.split()
    
    data = []
    for s in signal:
        data.append(float(s))
    data = np.array(data)
    return data


def read_smc_v2(input_file):
    """
    Reads and processes a COSMOS V2 file

    Inputes:
        | input_file: Input file path

    Outputs:

        | record_list: Includes list of records. Each item in this list includes
        | number of samples, delta t, orientation, and [disp, vel, acc] records.
        | station_metadata: Please see the end of this function for keys in the 
        | metadata attribute.
    """
    record_list = []

    # Loads station into a string
    try:
        fp = open(input_file, 'r')
    except IOError as e:
        LOGGER.warning(f"opening input file {input_file}")
        return False

    # Print status message
    LOGGER.debug(f"Reading {input_file} file.")

    # Read data
    channels = fp.read()
    fp.close()

    # Splits the string by channels
    channels = channels.split('/&')
    del(channels[len(channels)-1])

    # Splits the channels
    for i in range(len(channels)):
        channels[i] = channels[i].split('\n')

    # Clean the first row in all but the first channel
    for i in range(1, len(channels)):
        del channels[i][0]
    
    channels_unit = []
    for i in range(len(channels)):
        tmp = channels[i][0].split()
        # Check this is the corrected acceleration data
        ctype = (tmp[0] + " " + tmp[1]).lower()
        if ctype != "corrected accelerogram":
            print("[ERROR]: processing corrected accelerogram ONLY.")
            return False
        
        # detect unit of the record
        acc_unit = channels[i][17].split()[4]
        vel_unit = channels[i][18].split()[4]
        disp_unit = channels[i][19].split()[4]

        if (acc_unit == "cm/sec/sec" and vel_unit == "cm/sec" and
         disp_unit == "cm"):
            record_unit = "cm"
        elif (acc_unit == "m/sec/sec" and vel_unit == "m/sec" and
         disp_unit == "m"):
            record_unit = "m"
        else:
            record_unit = "unknown"
        
        channels_unit.append(record_unit)
        
        # Get network code and station id
        network = input_file.split('/')[-1].split('.')[0][0:2].upper()
        station_id = input_file.split('/')[-1].split('.')[0][2:].upper()

        # Get location's latitude and longitude
        tmp = channels[i][5].split()
        latitude = tmp[3][:-1]
        longitude = tmp[4]

        # Make sure we captured the right values
        if latitude[-1].upper() != "N" and latitude.upper() != "S":
            # Maybe it is an old file, let's try to get the values again...
            latitude = (float(tmp[3]) +
                        (float(tmp[4]) / 60.0) +
                        (float(tmp[5][:-2]) / 3600.0))
            latitude = "%s%s" % (str(latitude), tmp[5][-2])
            longitude = (float(tmp[6]) +
                         (float(tmp[7]) / 60.0) +
                         (float(tmp[8][:-1]) / 3600.0))
            longitude = "%s%s" % (str(longitude), tmp[8][-1])

        # Get orientation from integer header
        orientation = float(int(channels[i][26][50:55]))
        if orientation == 360:
            orientation = 0.0
        elif orientation == 500:
            orientation = "up"
        elif orientation == 600:
            orientation = "down"

        # Get filtering information
        tmp = channels[i][14].split()
        high_pass = float(tmp[8])
        low_pass = float(tmp[10])

        # Get station name
        station_name = channels[i][6][0:40].strip()

        # Get date and time; set to fixed format
        start_time = channels[i][4][37:80].split()
        try:
            date = start_time[2][:-1]
            tmp = start_time[3].split(':')
            hour = tmp[0]
            minute = tmp[1]
            seconds, fraction = tmp[2].split('.')
            # Works for both newer and older V2 files
            tzone = channels[i][4].split()[5]
        except IndexError:
            date = '00/00/00'
            hour = '00'
            minute = '00'
            seconds = '00'
            fraction = '0'
            tzone = '---'

        # Put it all together
        time = "%s:%s:%s.%s %s" % (hour, minute, seconds, fraction, tzone)

        # Get number of samples and dt
        tmp = channels[i][45].split()
        samples = int(tmp[0])
        delta_t = float(tmp[8])

        # Get signals' data
        tmp = channels[i][45:]
        a_signal = str()
        v_signal = str()
        d_signal = str()

        for s in tmp:
            # Detecting separate line and get data type
            if "points" in s.lower():
                line = s.split()
                if line[3].lower() == "accel" or line[3].lower() == "acc":
                    dtype = 'a'
                elif line[3].lower() == "veloc" or line[3].lower() == "vel":
                    dtype = 'v'
                elif line[3].lower() == "displ" or line[3].lower() == "dis":
                    dtype = 'd'
                else:
                    dtype = "unknown"

            # Processing data
            else:
                if dtype == 'a':
                    a_signal += s
                elif dtype == 'v':
                    v_signal += s
                elif dtype == 'd':
                    d_signal += s
        
        dis_data = read_data(d_signal)
        vel_data = read_data(v_signal)
        acc_data = read_data(a_signal)

        # print("[PROCESSING]: Found component: %s" % (orientation))
        record_list.append([samples, delta_t, orientation,
                                                [dis_data, vel_data, acc_data]])

    station_metadata = {}
    station_metadata['network'] = network
    station_metadata['station_id'] = station_id
    station_metadata['type'] = "V2"
    station_metadata['date'] = date
    station_metadata['time'] = time
    station_metadata['longitude'] = longitude
    station_metadata['latitude'] = latitude
    station_metadata['high_pass'] = high_pass
    station_metadata['low_pass'] = low_pass
    station_metadata['channels_unit'] = channels_unit

    return record_list, station_metadata


def unit_convention_factor(pr_unit, inc_unit):
    """
    controls project and incident units and returns multiplicaiton factor that
    converts the incident's or record's unit into projects unit. Only
    m(meter) anc cm(centimeter) are supported.  
    
    Inputs: 
        | pr_unit: The project conventional unit
        | inc_unit: Incident or record unit

    Output:
        | multiplication factor

    Example:
    >>> unit_convention_factor("cm", "cm")
    1
    >>> unit_convention_factor("m", "cm")
    0.01
    >>> unit_convention_factor("cm", "m")
    100

    """
    
    allowed_units = ["cm", "m"]
    if (pr_unit not in allowed_units) or (inc_unit not in allowed_units):
        LOGGER.error("Unit is not supported. Allowed units: "+str(a))
        return None

    if pr_unit == inc_unit:
        return 1

    if pr_unit == "cm" and inc_unit == "m":
        return 100

    if pr_unit == "m" and inc_unit == "cm":
        return 0.01

    # should not get here. 
    LOGGER.debug('Code logic does not sound right. DOUBLE CHECK.')

def is_incident_description_valid(inc_des, valid_incidents, current_incidents,
    valid_vertical_orientation, valid_incident_unit):
        """
        checks incident description and if it follows incident description 
        format, returns True, otherwise returns False.

        Inputs:
            | inc_des: Incident description key-value dictionary
            | valid_incidents: List of valid incidents type
            | current_incidents: List of current incidents name
            | valid_vertical_orientation: valid vertical orientation
            | valid_incident_unit: valid units for incidents

        Outputs:
            | True or False
        """
        try: 
            if "incident_name" not in inc_des.keys():
                LOGGER.warning("incident name is not provided in the"
                " description.txt file.")
                return False
    
            if "incident_type" not in inc_des.keys():
                LOGGER.warning("incident type is not provided in the"
                " description.txt file.")
                return False
    
            if inc_des["incident_type"] not in valid_incidents:
                LOGGER.warning(f"The incident type is not supported (valid "
                 f"incidents: {valid_incidents})")
                return False
    
            if inc_des["incident_name"] in current_incidents:
                LOGGER.warning(f"The provided incident name" 
                  f" ({inc_des['incident_name']}) has been used before.\n"
                  "The incident name should be a unique name. Current incidents: "
                 f"{current_incidents} ")
                return False
    
            
            # checks for hercules
            if inc_des["incident_type"] == "hercules":
    
                if "incident_unit" not in inc_des.keys():
                    LOGGER.warning("incident unit is not provided in the"
                     " description.txt file.")
                    return False
    
                if "ver_comp_orientation" not in inc_des.keys():
                    LOGGER.warning("incident vertical orientation is not provided"
                     " in the description.txt file.")
                    return False
    
                if (("hr_comp_orientation_1" not in inc_des.keys()) or
                    ("hr_comp_orientation_2" not in inc_des.keys())):
                    LOGGER.warning("At least one horizontal orientation is not"
                     " provided in the description.txt file.")
                    return False
    
                if "inputfiles_parameters" not in inc_des.keys():
                    LOGGER.warning("inputfiles_parameters is not provided"
                     " in the description.txt file.")
                    return False
    
                if inc_des["incident_unit"] not in valid_incident_unit:
                    LOGGER.warning(f"incident unit is not valid. "
                     f" List of valid units: {valid_incident_unit}")
                    return False
    
                if (inc_des["ver_comp_orientation"] not in
                 valid_vertical_orientation):
                    LOGGER.warning(f"incident vertical orientation is not valid. "
                     f" List of valid units: {valid_vertical_orientation}")
                    return False
    
                if (abs(float(inc_des["hr_comp_orientation_1"])) < 0 or 
                    abs(float(inc_des["hr_comp_orientation_1"])) > 360 or 
                    abs(float(inc_des["hr_comp_orientation_2"])) < 0 or 
                    abs(float(inc_des["hr_comp_orientation_2"])) > 360):
                    LOGGER.warning("At least one horizontal orientation is not a "
                     "valid number in the description.txt file. Valid range:"
                     "[0,360]")
                    return False

                # TODO: add check for perpendicular horizontal components.

        
        except Exception as e:
            LOGGER.error("description.txt: " + str(e))
            return False
                
        return True