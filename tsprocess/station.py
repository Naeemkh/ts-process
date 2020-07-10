"""
station.py
====================================
The core module for the Station class.
"""

from math import radians, cos, sin, asin, sqrt

# this should follow object pool design pattern 
# we need to take a look at stations, if we find it, we should return it. 

class Station:
    """ Class Station """
    list_of_stations = []
    vicinity_estimations = 10 

    def __init__(self, lat, lon, depth):
        #TODO add setter and getter to double check the lat and lon. 
        self.lat = lat
        self.lon = lon
        self.depth = depth
        self.vs_1d = None
        self.inc_st_name={}

    def add_vs_1d(self):
        pass

    def plot_station_location(self):
        pass

    def add_note(self):
        pass

    def _add_location(self):
        pass

    
    @staticmethod
    def _haversine(lat1, lon1, lat2, lon2):
        # convert decimal degrees to radians 
        try:
            lon1, lat1, lon2, lat2 = map(radians, [lon1, lat1, lon2, lat2])
        except Exception:
            return None
        # haversine formula 
        dlon = lon2 - lon1 
        dlat = lat2 - lat1 
        a = sin(dlat/2)**2 + cos(lat1) * cos(lat2) * sin(dlon/2)**2
        c = 2 * asin(sqrt(a)) 
        r = 6371000 # in meters
        return c * r

    @classmethod
    def add_station(cls, lat, lon, depth,incident_name,station_name):
   
        for st_item in cls.list_of_stations:           
            if cls._haversine(lat,lon,st_item.lat,st_item.lon) < cls.vicinity_estimations and abs(depth - st_item.depth) < 1:
               # this station is available
               st_item.inc_st_name[incident_name] = station_name
               return st_item
        
        tmp_st = Station(lat,lon, depth)
        tmp_st.inc_st_name[incident_name] = station_name
        cls.list_of_stations.append(tmp_st)
        return tmp_st