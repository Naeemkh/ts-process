import math

import numpy as np

def max_osc_response(acc, dt, csi, period, ini_disp, ini_vel):
    """
    Returns maximum values of displacement, velocity, and acceleration.
    
    Inputs:
    
    acc: accleration input signal\n
    dt:  time step\n
    csi: damping ratio\n
    period: oscilator's period\n
    ini_disp: initial displacement\n
    ini_vel: initial velocity\n

    Originial version is writting by: Leonardo Ramirez-Guzman
    TODO: this function is very slow requires some attention. 
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

    period: osilator's period\n
    data: acceleration input signal\n
    delta_ts: time step\n

    """
    rsp = np.zeros(len(period))
    for i,p in enumerate(period):
        rsp[i] = max_osc_response(data, delta_t, 0.05, p, 0, 0)[-1]
    return rsp


def get_period(tmin, tmax):
    """ Return an array of period T """
    # tmin = 1/fmax
    # tmax = 1/fmin
    a = np.log10(tmin)
    b = np.log10(tmax)

    period = np.linspace(a, b, 20)
    period = np.power(10, period)
    return period


def get_points(samples):
    # points is the least base-2 number that is greater than max samples
    power = int(math.log(max(samples), 2)) + 1
    return 2**power