"""
timeseries.py
====================================
The core module for the TimeSeries class.
"""
import numpy as np
from scipy.signal import (sosfiltfilt, filtfilt, ellip, butter, zpk2sos,
                          decimate, kaiser)

from .database import DataBase as db

class TimeSeries:
    """ TimeSeries Abstract Class """
    processing_labels = {}
    label_types = {
        'lowpass_filter':'fc: corner freq (Hz); N: order (default:4)',
        'highpass_filter':'fc: corner freq (Hz); N: order (default:4)',
        'bandpass_filter':'',
        'rotate':'',
        'scale':'',
        'shift':'',
        'taper':'flag: front, end, all; m: number of samples for tapering',
        'cut':'',
        'zero_pad':''
    }

    def __init__(self):
        self.value = None
        self.delta_t = None
        self.init_point = None
        self.type = None
        self.unit = None
        self.fft_value = None
        self.delta_f = None
        self.notes = None
        self.peak_vv = None
        self.peak_vt = None
        

    def add_note(self):
        pass

    @classmethod
    def _add_processing_label(cls, label_name, label_type, argument_dict):
        if label_name in cls.processing_labels:
            #TODO probably customize exception should be a better option
            #  to handle this.
            print("Label name has been used. Command is ignored.")
            return

        if label_type not in cls.label_types:
            #TODO probably customize exception should be a better option
            #  to handle this.
            print("Label type is not supported. Command is ignored.")
            return
        
        cls.processing_labels[label_name] = [label_type, argument_dict]

    def _lowpass_filter(self, fc, N = 4):
        """ Returns a lowpass filtered (the Butterworth filter) signal value."""
        Fs = 1/self.delta_t
        Wn = fc/(Fs/2)
        z, p, k = butter(N=N, Wn=Wn, btype='lowpass', analog=False,
         output='zpk')
        butter_sos = zpk2sos(z, p, k)
        data = sosfiltfilt(butter_sos, self.value)
        return data

    def _highpass_filter(self, fc, N = 4):
        """ Returns a lowpass filtered (the Butterworth filter) signal value."""
        Fs = 1/self.delta_t
        Wn = fc/(Fs/2)
        z, p, k = butter(N=N, Wn=Wn, btype='highpath', analog=False,
         output='zpk')
        butter_sos = zpk2sos(z, p, k)
        data = sosfiltfilt(butter_sos, self.value)
        return data    

    

    def _taper(self, flag, m):
        """
        Returns a Kaiser window created by a Besel function
    
        Inputs:

            flag - set to 'front', 'end', or 'all' to taper at the beginning,
                   at the end, or at both ends of the timeseries

            m - number of samples for tapering

            window - Taper window

        """
        samples = len(self.value)
    
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
            print(window.size)
            print(samples)
            print("[ERROR]: taper and data do not have the same number of\
                 samples.")
            window = np.ones(samples)
    
        return window


    def _apply(self, label_name):
        """ Applies the requested label_name on the timeseries """
        
        if label_name not in self.processing_labels.keys():
            # this should never be invoked. I have checked the labels before. 
            print("Label is not supported, ignored.")
            return
        
        #timeseries type
        ts_type = self.type

        label_type = self.processing_labels[label_name][0]
        label_kwargs = self.processing_labels[label_name][1]

        if label_type == 'lowpass_filter':
            proc_data = self._lowpass_filter(**label_kwargs)
 
        if label_type == 'highpass_filter':
            proc_data = self._highpass_filter(**label_kwargs)
 
        if label_type == 'bandpass_filter':
            print(f"{label_type} is not implemented.")
 
        if label_type == 'rotate':
            print(f"{label_type} is not implemented.")
 
        if label_type == 'scale':
            print(f"{label_type} is not implemented.")

        if label_type == 'shift':
            print(f"{label_type} is not implemented.")

        if label_type == 'taper':
            taper_window = self._taper(**label_kwargs)
            proc_data = self.value * taper_window            

        if label_type == 'cut':
            print(f"{label_type} is not implemented.")

        if label_type == 'zero_pad':
            print(f"{label_type} is not implemented.")
        
          
        if ts_type == "Disp":
            return Disp(proc_data, self.delta_t, self.init_point)

        if ts_type == "Vel":
            return Vel(proc_data, self.delta_t, self.init_point)

        if ts_type == "Acc":
            return Acc(proc_data, self.delta_t, self.init_point)

        if ts_type == "Raw":
            print("Not implemented.")
            return 

    
    def _add_values(self,value,dt,init_point):
        # double check to see if it is a numbpy array.
        # if not convert it into numpy array.
        # ########## <<<<<<<<<<<<<<<<<<<
        self.value = value
        self.delta_t = dt
        self.init_point = init_point





class Disp(TimeSeries):
    """ Disp Class """
    def __init__(self, value, dt, init_point):
        super().__init__()
        self.type = "Disp"
        self._add_values(value, dt, init_point)
        
    def compute_diff(self):
        """ Returns Vel instance """
        pass


class Vel(TimeSeries):
    """ Vel Class """
    def __init__(self, value, dt, init_point):
        super().__init__()
        self.type = "Vel"
        self._add_values(value, dt, init_point)

    def compute_diff(self):
        """ Returns ACC instance """
        pass

    def compute_integral(self):
        """ Returns Disp instance """
        pass


class Acc(TimeSeries):
    """ Acc Class """
    def __init__(self, value, dt, init_point):
        super().__init__()
        self.type = "Acc"
        self._add_values(value, dt, init_point)
        self.response_spectra = None
        self._compute_response_spectra()

    def compute_integral(self):
        """ Returns Vel instance """
        pass

    def _compute_response_spectra(self):
        """ Computes response spectra """
        pass


class Raw(TimeSeries):
    """ Raw Class """
    def __init__(self, raw_value, dt, init_point, poles, zeros, constant):
        super().__init__()
        self.raw_value = raw_value
        self.type = "Raw"

    def to_velocity(self):
        """ Returns Vel instance """
        pass


class Unitless(TimeSeries):
    """ Unitless Class """
    pass