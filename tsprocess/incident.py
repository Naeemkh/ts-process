"""
incident.py
====================================
The core module for the Incident class.
"""

import os

from .log import LOGGER
from .station import Station
from .database import DataBase
from .seismicsource import SeismicSource
from .ts_utils import is_lat_valid, is_lon_valid, is_depth_valid


class Incident:
    """ Incident Class """
    pr_db = None

    valid_incidents = [
        "hercules",
        "awp",
        "rwg",
        "cesmdv2"]

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

        if self.metadata["incident_type"] == "cesmdv2":
            LOGGER.debug("cesmdv2 incidents are considered as observations" 
            ", so they do not have input parameters.")
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
                                try:
                                    if not (is_lat_valid(float(
                                        tmp_line[0].strip()))
                                       and
                                       is_lon_valid(float(
                                        tmp_line[1].strip()))
                                       and
                                       is_depth_valid(float(
                                           tmp_line[2].strip()))):
                                       
                                       LOGGER.warning(f"station.{str(i)}'s" 
                                       "location is not valid location."
                                       " Ignored.")
                                       continue

                                except ValueError as v:
                                       LOGGER.warning(f"station.{str(i)}'s"
                                       " location is not valid input. Ignored. "
                                       + str(v))
                                       continue

                                self.stations_list.append(
                                    ['station.'+str(i),\
                                        Station.add_station(\
                                            float(tmp_line[0].strip()),\
                                            float(tmp_line[1].strip()),\
                                            float(tmp_line[2].strip()),\
                                            self.metadata["incident_name"],
                                             'station.'+str(i))] 
                                    )
                                LOGGER.debug(
                                    f"station.{str(i)} location added.")
                                i = i + 1
                            elif len(tmp_line) == 0:
                                # empty line, ignore it.
                                pass
                            else:
                                LOGGER.debug(
                                    f"station.{str(i)}'s location is not valid."
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

        if self.metadata["incident_type"] == "cesmdv2":
            with open(os.path.join(self.metadata["incident_folder"],
             'stations_list.txt'), 'r') as fp:
                while True:
                    line = fp.readline()
                    if not line:
                        break
                    if line.startswith("#"):
                        continue

                    tmp_line = line.split()
                    if len(tmp_line) == 4:
                        try:
                            if not (is_lat_valid(float(
                                    tmp_line[1].strip()))
                                    and
                                    is_lon_valid(float(
                                    tmp_line[2].strip()))
                                    and
                                    is_depth_valid(float(
                                    tmp_line[3].strip()))):
                                     
                                LOGGER.warning(f"{str(tmp_line[0])}'s" 
                                "location is not valid location."
                                " Ignored.")
                                continue

                        except ValueError as v:
                               LOGGER.warning(f"{tmp_line[0]}'s"
                               " location is not valid input. Ignored. "
                               + str(v))
                               continue

                        self.stations_list.append(
                            [tmp_line[0],\
                                Station.add_station(\
                                    float(tmp_line[1].strip()),\
                                    float(tmp_line[2].strip()),\
                                    float(tmp_line[3].strip()),\
                                    self.metadata["incident_name"],
                                     tmp_line[0]+".V2")] 
                            )
                        LOGGER.debug(
                            f"{tmp_line[0]} location added.")

                    elif len(tmp_line) == 0:
                        # empty line, ignore it.
                        pass
                    else:
                        LOGGER.debug(
                            f"{tmp_line[0]}'s location is not valid."
                            )
                                
    def _extract_seismic_source_data(self):
        """ extracts seismic source details. """
        self.metadata["incident_source_hypocenter"] = \
        tuple([float(i.strip()) for
         i in self.metadata["source_hypocenter"].split(",")])
        
        ## TODO: incidents seismic source requires comprehensive attention.
        if self.metadata["incident_type"] == "hercules":
            source_relative_path = self.metadata["source_directory"]
            source_folder = os.path.join(self.metadata["incident_folder"],
             source_relative_path) 
            self.source = SeismicSource(source_folder,
             self.metadata["incident_type"])