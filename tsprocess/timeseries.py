"""
timeseries.py
====================================
The core module for the TimeSeries class.
"""

from .database import DataBase as db
from scipy.signal import sosfiltfilt, filtfilt, ellip, butter, zpk2sos, decimate


class TimeSeries:
    """ TimeSeries Abstract Class """
    processing_labels = {}
    label_types = [
        'lowpass_filter',
        'highpass_filter',
        'bandpass_filter',
        'rotate',
        'scale',
        'shift',
        'taper',
        'cut',
        'zero_pad'
    ]

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
            print("Label name is already used. Is not added.")
            return

        if label_type not in cls.label_types:
            #TODO probably customize exception should be a better option
            #  to handle this.
            print("Label type is not supported. Is not added.")
            return
        
        cls.processing_labels[label_name] = [label_type, argument_dict]

    def _lowpass_filter(self, N, Wn, btype, output = 'zpk'):
        Fs = 1/self.delta_t
        Wn = Wn/(Fs/2)
        z, p, k = butter(N=N, Wn=Wn, btype=btype, analog=False, output='zpk')
        butter_sos = zpk2sos(z, p, k)
        data = sosfiltfilt(butter_sos, self.value)
        return data

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