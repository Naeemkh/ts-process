"""
project.py
====================================
The core module for the project class.
"""

import os
import hashlib
from typing import Any, List, Set, Dict, Tuple, Optional

from .record import Record
from .station import Station
from .incident import Incident
from .database import DataBase
from .timeseries import TimeSeries


class Project:
    """ Project Class """
    def __init__(self,name):
        """ initiating a project"""
        self.name = name
        self.pr_db = None
        self.incidents = {}
        self._connect_to_database()
        self.metadata = {}

    # database
    def _connect_to_database(self):
        self.pr_db = DataBase(self.name+"_db", cache_size=2000)
        Record.pr_db = self.pr_db

    def close_database(self):
        """ Terminating the connection to the database."""
        self.pr_db.close_db()

    # Incidents
    def add_incident(self, incident_folder):
        """
        Adds a new incident to the project. 
        """
        if not self.pr_db.connected:
            print("database is not connected")
            return
        
        # read the description file of incident
        inc_des = self._read_incident_description(incident_folder)

        #TODO these checks do not follow EAFP
        if "incident_name" not in inc_des.keys():
            print("incident name is not provided in the description.txt file.")
            return

        if "incident_type" not in inc_des.keys():
            print("incident type is not provided in the description.txt file.")
            return

        if inc_des["incident_type"] not in Incident.valid_incidents:
            print(f"Incident type is not supported (valid incidents:\
             {Incident.valid_incidents})")
            return

        if inc_des["incident_name"] in self.incidents.keys():
            print([f"incident name should be a unique name. Current incidents:\
             {self.incidents.keys} "])
            return

        # load incident
        self._load_incident(incident_folder,inc_des)
      
    def _load_incident(self, incident_folder, incident_description):
        """ load incidents into the project's incidents dictionary """

        if incident_description["incident_type"] == "hercules":
            self.incidents[incident_description["incident_name"]] = \
            Incident(incident_folder, incident_description)
            return

        if incident_description["incident_type"] == "awp":
            print("Incident details has not been added. Ignoring the command.")
            return 

        if incident_description["incident_type"] == "rwg":
            print("Incident details has not been added. Ignoring the command.")
            return 

    @staticmethod
    def _read_incident_description(incident_folder):
        incident_description = {}
        incident_description["incident_folder"] = incident_folder
        with open(os.path.join(incident_folder,'description.txt'),'r') as fp:
            while True:
                line = fp.readline()
                if not line:
                    break
                key, value = tuple(line.strip().split("="))
                incident_description[key.strip()] = value.strip()
        return incident_description

    def _extract_records(self, list_inc, list_process, list_filters):
        """ Extracts the requested records. Loop through all available
         stations and choose them based on list_filters. For list of
         incidents with N incidents, each station will return a list of 
         N records, corresponding the list of incidents. If for some 
         station there is no record for that incident, it should return 
         None. 
        """
        records = []
        for station in Station.list_of_stations:
            # if station passes the list_filters
            # go forward.
            # else continue.

           
            ignore_this_station = False
            for st_f in list_filters:
                if not station._check_station_filter(st_f):
                    # station could not pass at list one of filters.
                    ignore_this_station = True
                    break
            
            if ignore_this_station:
                continue


            st_records = []
            for i,incident_item in enumerate(list_inc):
                # choose the equivalent station for that incident.

                incident_metadata = self.incidents[incident_item].metadata

                st_name_inc = station.inc_st_name[incident_item]
                tmp_record = Record.get_record(station, incident_metadata, list_process[i])
                st_records.append(tmp_record)

            records.append(st_records)

        return records

    def _is_incident_valid(self,list_incidents):
        """ Checks if the requested processing label is a valid lable """
        for inc in list_incidents:
            if inc not in self.incidents:
                print(\
                    f"{inc} is not a valid incident name. Command ignored."\
                    )
                return False
        
        return True

    def remove_incident(self, incident_name):
        """Removes incident from the project. """
        pass
    
    # source
    def add_source_hypocenter(self,lat, lon, depth):
        self.metadata["project_source_hypocenter"] = (lat, lon, depth)
        Station.pr_source_loc = (lat, lon, depth)

    # processing labels
    def add_processing_label(self, label_name, label_type, hyper_parameters):
        """ Creates a processing label """
        TimeSeries._add_processing_label(label_name, label_type, hyper_parameters)
        
    def list_of_processing_labels(self):
        """ Returns a list of available processing labels"""
        if not TimeSeries.processing_labels:
            return
        for item in TimeSeries.processing_labels:
            print(item, '-->', TimeSeries.processing_labels[item])

    def _is_processing_label_valid(self,list_process):
        """ Checks if the requested processing label is a valid lable """
        for group in list_process:
            for pr_l in group:
                if pr_l not in TimeSeries.processing_labels:
                    print(\
                        f"{pr_l} is not a valid processing label. Command ignored."\
                        )
                    return False
        
        return True

    def valid_processing_labels(self):
        for i,item in enumerate(TimeSeries.label_types):
            print(f"{i}: {item}")

    # station filtering
    def add_station_filter(self, station_filter_name, station_filter_type, hyper_parameters):
        Station.add_station_filter(station_filter_name, station_filter_type, hyper_parameters)
    

    def valid_station_filter_type(self):
        for i,item in enumerate(Station.station_filter_types):
            print(f"{i}: {item}")

    # Analysis interface
    def plot_velocity_records(self, list_inc,list_process,list_filters):
        """ Plots 3 velocity timeseries one page per station."""
        
        if not self._is_incident_valid(list_inc):
            return

        if not self._is_processing_label_valid(list_process):
            return

        records = self._extract_records(list_inc, list_process, list_filters)
        
        for item in records:
            print(item[0]) 

    def which_records(self, list_inc,list_process,list_filters):
        """Represent all records that will pass a given filters"""
        if not self._is_incident_valid(list_inc):
            return

        if not self._is_processing_label_valid(list_process):
            return

        records = self._extract_records(list_inc, list_process, list_filters)
        
        for item in records:
            print(item[0]) 


        
    



    
