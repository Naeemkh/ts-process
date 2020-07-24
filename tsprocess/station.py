"""
station.py
====================================
The core module for the Station class.
"""

from math import radians, cos, sin, asin, sqrt

from .ts_utils import compute_azimuth
from .log import LOGGER

# this should follow object pool design pattern 
# we need to take a look at stations, if we find it, we should return it. 


class Station:
    """ Class Station """
    list_of_stations = []
    vicinity_estimations = 10 
    station_filter_types = [
        "epi_dist_lt",
        "epi_dist_gt",
        "epi_dist_lte",
        "epi_dist_gte",
        "azimuth_bt",
        "include_stlist_by_incident",
        "exclude_stlist_by_incident"
    ]

    station_filters = {}

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

    @classmethod
    def add_station_filter(cls, filter_name, filter_type, argument_dict):
        if filter_name in cls.station_filters:
            #TODO probably customize exception should be a better option
            #  to handle this.
            print("Filter name is already used. Has not been added.")
            return

        if filter_type not in cls.station_filter_types:
            #TODO probably customize exception should be a better option
            #  to handle this.
            print("Filter type is not supported. Has not been added.")
            return
        
        cls.station_filters[filter_name] = [filter_type, argument_dict]
    
    def _epi_dist_lt(self, distance):
        # we already have the record distance from the source. 
        # However, I think it is better if filter the source before
        # messing up with records. 
        # I keep both sides, to see which method works better.
        source_lat, source_lon, source_depth = self.pr_source_loc
        tmp_dist = self._haversine(source_lat,source_lon,self.lat, self.lon)/1000
        if tmp_dist < distance:
            return True
        else:
            return False

    def _epi_dist_gt(self, distance):
        # we already have the record distance from the source. 
        # However, I think it is better if filter the source before
        # messing up with records. 
        # I keep both sides, to see which method works better.
        source_lat, source_lon, source_depth = self.pr_source_loc
        tmp_dist = (self._haversine(source_lat,source_lon,self.lat,
         self.lon))/1000
        if tmp_dist > distance:
            return True
        else:
            return False

    def _azimuth_bt(self, azmth):
        
        if azmth[0] < 0 or azmth[1] < 0:
            LOGGER.error("Azimuth domain cannot be negative number (0-360)."
            "Azimuth filter ignored.")
            return True
        
        source_lat, source_lon, source_depth = self.pr_source_loc
        tmp_azimuth = compute_azimuth(source_lat,source_lon,self.lat, self.lon)

        if azmth[0] == azmth[1]:
            return True

        if azmth[0] < azmth[1]:
            if tmp_azimuth >= azmth[0] and tmp_azimuth <= azmth[1]:
                return True
            else:
                return False
        else:
            if tmp_azimuth >= azmth[1] or tmp_azimuth <= azmth[0]:
                return True
            else:
                return False
  
    def _include_stlist_by_incident(self, incident_name, stations):

        if self.inc_st_name[incident_name] in stations:
            return True
        else:
            return False

    def _check_station_filter(self,station_filter_name):

        if station_filter_name not in self.station_filters.keys():
            # this should never be invoked. I have checked the labels before. 
            print("Filter is not supported, ignored.")
            return
        
        filter_type = self.station_filters[station_filter_name][0]
        filter_kwargs = self.station_filters[station_filter_name][1]

        if filter_type == 'epi_dist_lt':
            return self._epi_dist_lt(**filter_kwargs)

        if filter_type == 'epi_dist_gte':
            return not self._epi_dist_lt(**filter_kwargs)

        if filter_type == 'epi_dist_gt':
            return self._epi_dist_gt(**filter_kwargs)

        if filter_type == 'epi_dist_lte':
            return not self._epi_dist_gt(**filter_kwargs)

        if filter_type == 'azimuth_lt':
            return self._azimuth_lt(**filter_kwargs)

        if filter_type == 'azimuth_gte':
            return not self._azimuth_lt(**filter_kwargs)

        if filter_type == 'azimuth_gt':
            return self._azimuth_gt(**filter_kwargs)

        if filter_type == 'azimuth_lte':
            return not self._azimuth_gt(**filter_kwargs)
        
        if filter_type == 'azimuth_bt':
            return self._azimuth_bt(**filter_kwargs)

        if filter_type == 'include_stlist_by_incident':
            return self._include_stlist_by_incident(**filter_kwargs)

        if filter_type == 'exclude_stlist_by_incident':
            return not self._include_stlist_by_incident(**filter_kwargs)

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
            if (cls._haversine(lat,lon,st_item.lat,st_item.lon) < 
            cls.vicinity_estimations and abs(depth - st_item.depth) < 1):
               # this station is available
               st_item.inc_st_name[incident_name] = station_name
               return st_item
        
        tmp_st = Station(lat,lon, depth)
        tmp_st.inc_st_name[incident_name] = station_name
        cls.list_of_stations.append(tmp_st)
        return tmp_st