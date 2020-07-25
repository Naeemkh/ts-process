"""
project.py
====================================
The core module for the project class.
"""

import os
import hashlib
from typing import Any, List, Set, Dict, Tuple, Optional

import pandas as pd
import sqlite3
from ipywidgets import HTML
from datetime import datetime
import matplotlib.pyplot as plt
import matplotlib.gridspec as gridspec
from matplotlib.font_manager import FontProperties
from ipyleaflet import Map, Marker, basemaps, basemap_to_tiles, AwesomeIcon, Popup

from .log import LOGGER
from .record import Record
from .station import Station
from .incident import Incident
from .database import DataBase
from .timeseries import TimeSeries
from .db_tracker import DataBaseTracker
from .ts_utils import (check_opt_param_minmax, query_opt_params, write_into_file,
                      list2message, is_lat_valid, is_lon_valid, is_depth_valid)
from .ts_plot_utils import (plot_displacement_helper, plot_velocity_helper,
                            plot_acceleration_helper, plot_recordsection_helper)


class Project:
    """ Project Class    
    p1 = Project('myproject')
    """

    color_code  = ['k', 'r', 'b', 'm', 'g', 'c', 'y', 'brown',
                   'gold', 'blueviolet', 'grey', 'pink']

    _instance = None

    def __new__(cls,name):
        if cls._instance is None:
            cls._instance = super(Project,cls).__new__(cls)
            cls._instance.name = name
            cls._instance.tracker_name = name + "_dbtracker"
            cls._instance.pr_db = None
            cls._instance.path_to_output_dir = None
            cls._instance.incidents = {}
            cls._instance._connect_to_database()
            cls._instance._make_output_dir()
            cls._instance.metadata = {}
            return cls._instance
        else:
            LOGGER.warning(f"Project named {cls._instance.name} "
             "is already generated. Each session can support one project."
             "This command will be ignored.")
            return cls._instance
         
    # database
    @classmethod
    def _connect_to_database(cls):
        """ Creates and connects to a database."""
        cls._instance.pr_db = DataBase(cls._instance.name+"_db", cache_size=2000)
        Record.pr_db = cls._instance.pr_db
        
        cls._instance.pr_inc_tracker = DataBaseTracker(cls._instance.tracker_name,
         cls._instance, buffer_capacity=3)
        Record.pr_inc_tracker = cls._instance.pr_inc_tracker        

    def close_database(self):
        """ Terminating the connection to the database."""

        # writing data tracker in the buffer into the database
        self.pr_inc_tracker.add_to_database()
        self.pr_inc_tracker.buffer = {key: [] for 
         key, _ in self.pr_inc_tracker.buffer.items()}

        # closing database
        self.pr_db.close_db()

    @classmethod
    def _make_output_dir(cls):
        """ Makes output_tsprocess directory in the working path. """
        path_to_output = os.path.join(os.getcwd(),"output_tsprocess")

        try:
            os.mkdir(path_to_output)
            cls._instance.path_to_output_dir = path_to_output
            LOGGER.debug(f"{path_to_output} forlder is created.")
        
        except FileExistsError:
            cls._instance.path_to_output_dir = path_to_output
            LOGGER.debug(f"{path_to_output} forlder exists.")
        
        except OSError:
            LOGGER.warning(f"Failed to create {path_to_output} folder.")
  
    # Incidents
    def add_incident(self, incident_folder):
        """ Adds a new incident to the project.
        
        Inputs:

            incident_folder: absolute or relative path to the incident folder.
        
        """

        if not hasattr(self, 'pr_db'):
            LOGGER.error("Project does not have database."
             "Regenerate the project.")
            return

        elif not self.pr_db.connected:
            LOGGER.error("Project has database. But not connected." 
            "Regenerate the project.")
            return

        # read the description file of incident
        inc_des = self._read_incident_description(incident_folder)
        
        #TODO these checks do not follow EAFP
        if "incident_name" not in inc_des.keys():
            LOGGER.warning("incident name is not provided in the"
            " description.txt file.")
            return

        if "incident_type" not in inc_des.keys():
            LOGGER.warning("incident name is not provided in the"
            " description.txt file.")
            return

        if inc_des["incident_type"] not in Incident.valid_incidents:
            LOGGER.warning(f"The incident type is not supported (valid "
             f"incidents: {Incident.valid_incidents})")
            return

        if inc_des["incident_name"] in self.incidents.keys():
            LOGGER.warning(f"The provided incident name" 
              f" ({inc_des['incident_name']}) has been used before.\n"
              "The incident name should be a unique name. Current incidents: "
             f"{list(self.incidents.keys())} ")
            return

        # load incident
        self._load_incident(incident_folder,inc_des)
        self.pr_inc_tracker.start_tracking_incident(inc_des["incident_name"])
      
    def _load_incident(self, incident_folder, incident_description):
        """ load incidents into the project's incidents dictionary
        
        Inputs:

            | incident_folder: path to incident folder
            | incident_description: dictionary of incident's description

         """

        if incident_description["incident_type"] == "hercules":
            self.incidents[incident_description["incident_name"]] = \
            Incident(incident_folder, incident_description)
            return

        if incident_description["incident_type"] == "awp":
            print("AWP incident loading methods have not been added yet.")
            return 

        if incident_description["incident_type"] == "rwg":
            print("RWG incident loading methods have not been added yet.")
            return 

    @staticmethod
    def _read_incident_description(incident_folder):
        """ Extract incident descriptions
        
        Inputs:

            incident_folder: path to incident folder.
         """
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
         stations and choose them based on list_filters. For a list of
         incidents with N incidents, each station will return a list of 
         N records, corresponding to the list of incidents. If for some 
         stations there is no record for that incident, it should return 
         None. 
        """

        if len(list_inc) != len(list_process):
            LOGGER.error("Number of incidents, and number of nested lists of"
             "processing labels should be the same.")
            return

        records = []
        for station in Station.list_of_stations:
           
            ignore_this_station = False
            for st_f in list_filters:
                if not station._check_station_filter(st_f):
                    # station could not pass at least one of the filters.
                    ignore_this_station = True
                    break
            
            if ignore_this_station:
                continue

            st_records = []
            for i,incident_item in enumerate(list_inc):
                # choose the equivalent station for that incident.
                incident_metadata = self.incidents[incident_item].metadata

                st_name_inc = station.inc_st_name[incident_item]
                list_process_cp = list_process[i].copy()
                tmp_record = Record.get_record(station, incident_metadata,
                 list_process_cp)
                st_records.append(tmp_record)

            records.append(st_records)

        return records

    def _is_incident_valid(self,list_incidents):
        """ Checks if the requested processing label is a valid label """
        for inc in list_incidents:
            if inc not in self.incidents:
                LOGGER.warning(
                    f"{inc} is not a valid incident name. Command ignored."
                    )
                return False
        
        return True

    def remove_incident(self, incident_name):
        """Removes incident from the project."""
        
        if incident_name not in self.incidents:
            LOGGER.warning(f"'{incident_name}' is not exist."
             f"List of available incidents: {self.incidents}")
            return

        # first remove the incident related records from database.
        tmp_list_hash = self.pr_db.get_nested_container(
            self.tracker_name)[incident_name]

        # it might be a good idea to assign this to another thread or processor.
        try:
            for item in tmp_list_hash:
                self.pr_db.delete_value(item)
            LOGGER.debug(f"All records related to incident {incident_name}"
             ", has been removed from database.")
        except:
            pass
        
        try:
            self.incidents.pop(incident_name)
            LOGGER.info(f"Incident {incident_name} is deleted.")
        except Exception:
            LOGGER.error(f"Could not delete incident '{incident_name}'")
        
        # Sqlite3 removes the data however, does nor release it.
        # it keeps it for future use. We can manually clear the database.
        conn=sqlite3.connect(self.name + '_db.sqlite')
        conn.execute("VACUUM")
        conn.close()

        # clean the hash values from tracker:
        self.pr_inc_tracker.remove_incident(incident_name)
    
    # source
    def add_source_hypocenter(self,lat, lon, depth):
        """ Adds earthquake hypocenter to the project.
        
        Inputs: 

            | lat: latitude (-90,90)
            | lon: longitude (-180, 180)
            | depth: in meters (positive toward earth interior) 
                
        """
        
        if not(is_lat_valid(lat) and is_lon_valid(lon) and
         is_depth_valid(depth)):
            LOGGER.error('Source is not added.')  
            return
        
        self.metadata["project_source_hypocenter"] = (lat, lon, depth)
        Station.pr_source_loc = (lat, lon, depth)

    # processing labels
    def add_processing_label(self, label_name, label_type, hyper_parameters):
        """ Creates a processing label """
        if label_type == "rotate":
            Record._add_processing_label(label_name, label_type,
            hyper_parameters)
            return            
        
        TimeSeries._add_processing_label(label_name, label_type,
         hyper_parameters)

        
    def list_of_processing_labels(self):
        """ Returns a list of available processing labels"""
        if not TimeSeries.processing_labels:
            return
        for item in TimeSeries.processing_labels:
            print(item, '-->', TimeSeries.processing_labels[item])

    def _is_processing_label_valid(self,list_process):
        """ Checks if the requested processing label is a valid lable
        
        Input:
            list_process: List of processing labels
        
        """
        for group in list_process:
            for pr_l in group:
                if ((pr_l not in TimeSeries.processing_labels) and 
                    (pr_l not in Record.processing_labels)):
                    LOGGER.error(
                        f"{pr_l} is not a valid processing label. Command"
                            "ignored."
                        )
                    return False
        
        return True

    def valid_processing_labels(self):
        """ Returns a list of valid processing labels """
        for i,item in enumerate(TimeSeries.label_types):
            print(f"{i}: {item} - args: {TimeSeries.label_types[item]}")

    # station filtering
    def add_station_filter(self, station_filter_name, station_filter_type,
     hyper_parameters):
        """ Adds a new filter for selecting stations """
        Station.add_station_filter(station_filter_name, station_filter_type,
         hyper_parameters)
    
    def valid_station_filter_type(self):
        """ Returns a list of valid filters for selecting stations. """
        for i,item in enumerate(Station.station_filter_types):
            print(f"{i}: {item}")

    def list_of_station_filters(self):
        """ Returns a list of available processing labels """
        if not Station.station_filters:
            return
        for item in Station.station_filters:
            print(item, '-->', Station.station_filters[item])

    # Analysis interface
    def plot_displacement_records(self, list_inc,list_process,list_filters,
    opt_params):
        """ Plots 3 displacement timeseries one page per station and their 
        fft amplitude spectra plots
        
        Inputs:
            | list_inc: list of incidents
            | list_process: list of processes, one list per incident
            | list filters: list of filters defined for stations
            | opt_params: optional parameters (dictionary)

        Optional parameters:
            | zoom_in_time : [tmin, tmax] in seconds
            | Horizontal zoom in time axis for better presentation. Data is not
              modified. 
            | zoom_in_freq : [freq_min, freq_max] in Hertz
            | Horizontal zoom in period axis for better presentation. Data is 
              not modified. 
        """
        
        if not self._is_incident_valid(list_inc):
            LOGGER.warning("At least one incident is not valid.")
            return

        if not self._is_processing_label_valid(list_process):
            LOGGER.warning("At least one processing label is not valid.")
            return

        records = self._extract_records(list_inc, list_process, list_filters)
        
        # Check number of input timeseries
        if len(records[0]) > len(self.color_code):
            LOGGER.error(f"Number of timeseries are more than dedicated" 
            "colors.")
            return

        for record in records:
            fig, message, f_name_save = plot_displacement_helper(record,
             self.color_code,opt_params, list_inc, list_process, list_filters)
                
            if query_opt_params(opt_params, 'save_figure'):
                
                message = message + "\n----------------------------\n"
                write_into_file(os.path.join(self.path_to_output_dir,
                "output_item_description.txt"),message)

                # save item.
                plt.savefig(os.path.join(self.path_to_output_dir,f_name_save),
                 format='pdf',transparent=False, dpi=300)                 

    def plot_velocity_records(self, list_inc,list_process,list_filters,opt_params):
        """ Plots 3 velocity timeseries one page per station and their 
        fft amplitude spectra plots
        
        Inputs:
            | list_inc: list of incidents
            | list_process: list of processes, one list per incident
            | list filters: list of filters defined for stations
            | opt_params: optional parameters (dictionary)

        Optional parameters:
            | zoom_in_time : [tmin, tmax] in seconds
            | Horizontal zoom in time axis for better presentation. Data is not
              modified. 
            | zoom_in_freq : [freq_min, freq_max] in Hertz
            | Horizontal zoom in period axis for better presentation. Data is 
              not modified. 
        """
        
        if not self._is_incident_valid(list_inc):
            LOGGER.warning("At least one incident is not valid.")
            return

        if not self._is_processing_label_valid(list_process):
            LOGGER.warning("At least one processing label is not valid.")
            return

        records = self._extract_records(list_inc, list_process, list_filters)
        
        # Check number of input timeseries
        if len(records[0]) > len(self.color_code):
            LOGGER.error(f"Number of timeseries are more than dedicated" 
            "colors.")
            return

        for record in records:
            fig, message, f_name_save = plot_velocity_helper(record,
             self.color_code,opt_params, list_inc, list_process, list_filters)
                
            if query_opt_params(opt_params, 'save_figure'):
                
                # temp_record = None
                # for tmp_rc in record:
                #     if tmp_rc:
                #         temp_record = tmp_rc
                #         break

                # if not temp_record:
                #     LOGGER.warning(
                #         'All records at this station are None. Ignored.')

                message = message + "\n----------------------------\n"
                write_into_file(os.path.join(self.path_to_output_dir,
                "output_item_description.txt"),message)

                # save item.
                plt.savefig(os.path.join(self.path_to_output_dir,f_name_save),
                 format='pdf',transparent=False, dpi=300)  


    def plot_acceleration_records(self, list_inc,list_process,list_filters,
     opt_params):

        """ Plots 3 acceleration timeseries one page per station and their 
        response spectra plots
        
        Inputs:
            | list_inc: list of incidents
            | list_process: list of processes, one list per incident
            | list filters: list of filters defined for stations
            | opt_params: optional parameters (dictionary)

        Optional parameters:
            | zoom_in_time : [tmin, tmax] in seconds
            | Horizontal zoom in time axis for better presentation. Data is not
              modified. 
            | zoom_in_rsp : [period_min, period_max] in seconds
            | Horizontal zoom in period axis for better presentation. Data is 
              not modified. 
        """
        
        if not self._is_incident_valid(list_inc):
            LOGGER.warning("At least one incident is not valid.")
            return

        if not self._is_processing_label_valid(list_process):
            LOGGER.warning("At least one processing label is not valid.")
            return

        records = self._extract_records(list_inc, list_process, list_filters)
        
        # Check number of input timeseries
        if len(records[0]) > len(self.color_code):
            LOGGER.error(f"Number of timeseries are more than dedicated" 
            "colors.")
            return

        for record in records:
            fig, message, f_name_save = plot_acceleration_helper(record,
            self.color_code,opt_params,
             list_inc, list_process, list_filters)
                
            if query_opt_params(opt_params, 'save_figure'):
                
                message = message + "\n----------------------------\n"
                write_into_file(os.path.join(self.path_to_output_dir,
                "output_item_description.txt"),message)

                # save item.
                plt.savefig(os.path.join(self.path_to_output_dir,f_name_save),
                 format='pdf',transparent=False, dpi=300)  
          
    
    def plot_record_section(self, list_inc,list_process,list_filters,
     opt_params):
        """ Plots seismic record section  

        Inputs:
            | list_inc: list of incidents
            | list_process: list of processes, one list per incident
            | list filters: list of filters defined for stations
            | opt_params: optional parameters (dictionary)

        Optional parameters:
            | zoom_in_time : [tmin, tmax] in seconds
            | Horizontal zoom in time axis for better presentation. Data is not
              modified. 
        """
        
        if not self._is_incident_valid(list_inc):
            return

        if not self._is_processing_label_valid(list_process):
            return

        records = self._extract_records(list_inc, list_process, list_filters)

        fig, message, f_name_save = plot_recordsection_helper(records,
            self.color_code,opt_params,list_inc, list_process, list_filters)

        if query_opt_params(opt_params, 'save_figure'):
            
            message = message + "\n----------------------------\n"
            write_into_file(os.path.join(self.path_to_output_dir,
            "output_item_description.txt"),message)
            # save item.
            plt.savefig(os.path.join(self.path_to_output_dir,f_name_save),
             format='pdf',transparent=False, dpi=300)  

    def show_stations_on_map(self,list_inc,list_process,list_filters,
     opt_params):
        """ Returns an interactive map of source and stations, use only in 
        Jupyter Notebooks.  

        Inputs:
            | list_inc: list of incidents
            | list_process: list of processes, one list per incident
            | list filters: list of filters defined for stations
            | opt_params: optional parameters (dictionary)

        Optional parameters:

        """
                
        records = self._extract_records(list_inc, list_process, list_filters)

        m = Map(
            basemap=basemap_to_tiles(basemaps.Esri.WorldImagery, "2020-04-08"),
            center = (Station.pr_source_loc[0],Station.pr_source_loc[1]),
            zoom = 8,
            close_popup_on_click=True
        )

        for i in records:
            lat = i[0].station.lat
            lon = i[0].station.lon
            marker = Marker(location=(lat, lon), draggable=False,
             icon=AwesomeIcon(name="map-pin", marker_color='green',
             icon_color='darkgreen'), opacity=0.8)
            m.add_layer(marker)
            message = HTML()
            message.value = i[0].station.inc_st_name[list_inc[0]]
            marker.popup = message

        m.add_layer(Marker(icon=AwesomeIcon(name="star",
         marker_color='red', icon_color='darkred'),
         location=(Station.pr_source_loc[0],Station.pr_source_loc[1]),
         draggable=False))
        
        return m


    def which_records(self, list_inc,list_process,list_filters, opt_params):
        """ Print outs all records that pass the given filters 

        Inputs:
            | list_inc: list of incidents
            | list_process: list of processes, one list per incident
            | list filters: list of filters defined for stations
            | opt_params: optional parameters (dictionary)

        Optional parameters:
        """
        
        if not self._is_incident_valid(list_inc):
            return

        if not self._is_processing_label_valid(list_process):
            return

        records = self._extract_records(list_inc, list_process, list_filters)
        
        if not records:
            return

        for item in records:
            print(item[0]) 

    
    def list_of_incidents(self):
        """ Returns a list of incidents."""
        return list(self.incidents.keys())


    def compare_incidents(self,ls_inc, only_differences=False):
        """ 
        compares the incidents' meta data

        Inputs:
            | ls_inc: list of incident names
            | only_differerences: True or False

        """

        uni_keys = []

        column_names = ["parameters"]
        for inc in ls_inc:
            column_names.append(inc)
            uni_keys.extend(self.incidents[inc].metadata.keys())

        uni_keys = list(set(uni_keys))
        table = []
        for param in uni_keys:
            tmp = [param]
            for inc in ls_inc:
                tmp.append(self.incidents[inc].metadata.get(param, " "))
            
            if not (only_differences and len(set(tmp[1:])) == 1):
                table.append(tmp)

        table_df = pd.DataFrame(table, columns=column_names)
        return table_df

    #Database
    def database_summary(self):
        """ Returns a summary of database """

        try:
            db_file = self.name+'_db.sqlite'
            database_size = os.path.getsize(db_file)
        except OSError as e:
            LOGGER.warning(f"{db_file} is not found.")
            database_size = None
        
        db_keys = self.pr_db.db.keys()
        list_of_trackers = [key for key in db_keys if
         '_dbtracker' in key.lower()]

        if database_size:
            print(f"Database name: {db_file}")
            print(f"Database size: {str(database_size/1000000)} MB.")
            print(f"Number of items: {str(len(list(self.pr_db.db.keys())))}")
            print(f"List of database trackers: {list_of_trackers}")
            
    def database_content(self):

        for key, item in self.pr_db.db.items():
            print(key," : ", item)

        
    



    
