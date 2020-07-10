"""
timeseries.py
====================================
The core module for the TimeSeries class.
"""

from .database import DataBase as db
import hashlib

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

    def _add_values(self, value, dt, init_point):
        self.value = value 
        self.dt = dt
        self.init_point = init_point


class Disp(TimeSeries):
    """ Disp Class """
    def __init__(self, value, dt, init_point):
        super().__init__()
        self._add_values(value, dt, init_point)

    def compute_diff(self):
        """ Returns Vel instance """
        pass

class Vel(TimeSeries):
    """ Vel Class """
    def __init__(self, value, dt, init_point):
        super().__init__()
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
        self.response_spectra = None
        self._add_values(value,dt,init_point)
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

    def to_velocity(self):
        """ Returns Vel instance """
        pass


class Unitless(TimeSeries):
    """ Unitless Class """
    pass