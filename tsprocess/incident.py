"""
incident.py
====================================
The core module for the Incident class.
"""

import os

from .station import Station
from .database import DataBase
from .seismicsource import SeismicSource


class Incident:
    """ Incident Class """
    pr_db = None

    valid_incidents = [
        "hercules",
        "awp",
        "rwg"]

    def __init__(self,folder_path, incident_description):
        """ Initiating an incident"""
        self.folder_path = folder_path
        self.metadata = dict()
        self.metadata.update(incident_description)
        self.stations_list = []
        self.records = []
        self._extract_input_parameters()
        self._extract_station_name_location()
        self._extract_seismic_source_data()

    def _extract_input_parameters(self):
        """ Extracts input parameters from the incident folder. Stores the
        results in the metadata attribute. """

        if self.metadata["incident_type"] == "hercules":
            # TODO move each part of reading files into a function.
            with open(os.path.join(self.folder_path,
             self.metadata['inputfiles_parameters']), 'r') as fp:
                while True:
                    line = fp.readline()
                    if not line:
                        break
                    if line.startswith("#"):
                        continue
                    if "=" in line: 
                        tmp_line = line.strip().split("=")
                        if len(tmp_line)== 2:
                            key, value = tuple(tmp_line)
                            if key and value:
                                self.metadata[key.strip()] = value.strip()
            return
       
        if self.metadata["incident_type"] == "awp":
            print("Methods for AWP is not implemented.")                 
            return

        if self.metadata["incident_type"] == "rwg": 
            print("Methods for RWG is not implemented.")                 
            return

    def _extract_station_name_location(self):
        """ Extracts stations' name and location from the incident folder. """

        if self.metadata["incident_type"] == "hercules":
            n_st = int(self.metadata["number_output_stations"])
            with open(os.path.join(self.metadata["incident_folder"],
             self.metadata['inputfiles_parameters']), 'r') as fp:
                
                start_reading_stations = False
                while True:
                    line = fp.readline()
                    if not line:
                        break
                    if line.startswith("#"):
                        continue
                    if (("output_stations" in line) and ("=" in line) and
                     (len(line.split())==2)):
                        start_reading_stations = True
                    
                    if start_reading_stations:
                        i = 0
                        while i < int(n_st):
                            line = fp.readline()
                            tmp_line = line.split()
                            if len(tmp_line) == 3:
                                self.stations_list.append(
                                    ['station.'+str(i),\
                                        Station.add_station(\
                                            float(tmp_line[0].strip()),\
                                            float(tmp_line[1].strip()),\
                                            float(tmp_line[2].strip()),\
                                            self.metadata["incident_name"],
                                             'station.'+str(i))] 
                                    )
                                i = i + 1
                        break
            return

        if self.metadata["incident_type"] == "awp":
            print("Methods for AWP is not implemented.")                 
            return

        if self.metadata["incident_type"] == "rwg":
            print("Methods for rwg is not implemented.")                 
            return
    
    def _extract_seismic_source_data(self):
        """ extracts seismic source details. """
        self.metadata["incident_source_hypocenter"] = \
        tuple([float(i.strip()) for
         i in self.metadata["source_hypocenter"].split(",")])
        source_relative_path = self.metadata["source_directory"]
        source_folder = os.path.join(self.metadata["incident_folder"],
         source_relative_path)
        self.source = SeismicSource(source_folder,
         self.metadata["incident_type"])