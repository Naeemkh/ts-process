"""
project.py
====================================
The core module for the project class.
"""

import os
import hashlib
from typing import Any, List, Set, Dict, Tuple, Optional


import pandas as pd
from ipywidgets import HTML
import matplotlib.pyplot as plt
import matplotlib.gridspec as gridspec
from ipyleaflet import Map, Marker, basemaps, basemap_to_tiles, AwesomeIcon, Popup

from .log import LOGGER
from .record import Record
from .station import Station
from .incident import Incident
from .database import DataBase
from .timeseries import TimeSeries
from .ts_utils import check_opt_param_minmax


class Project:
    """ Project Class """

    color_code  = ['k', 'r', 'b', 'm', 'g', 'c', 'y', 'brown',
                   'gold', 'blueviolet', 'grey', 'pink']

    _instance = None

    def __new__(cls,name):
        if cls._instance is None:
            cls._instance = super(Project,cls).__new__(cls)
            # print("new in work")
            cls._instance.name = name
            cls._instance.pr_db = None
            cls._instance.incidents = {}
            cls._instance._connect_to_database()
            cls._instance.metadata = {}
            return cls._instance
        else:
            LOGGER.warning(f"Project named {cls._instance.name} "
             "is already generated. Each session can support one project."
             "This command will be ignored.")
            print("One project per session. Command is ignored,"
             "see the log file.")
            return None 
        
    # database
    @classmethod
    def _connect_to_database(cls):
        """ Creates and connects to a database.
        >>> 4 * 3
        12
        """
        cls.pr_db = DataBase(cls._instance.name+"_db", cache_size=2000)
        Record.pr_db = cls.pr_db

    def close_database(self):
        """ Terminating the connection to the database."""
        self.pr_db.close_db()

    # Incidents
    def add_incident(self, incident_folder):
        """ Adds a new incident to the project."""
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
            print("AWP incident loading methods have not been added yet.")
            return 

        if incident_description["incident_type"] == "rwg":
            print("RWG incident loading methods have not been added yet.")
            return 

    @staticmethod
    def _read_incident_description(incident_folder):
        """ Extract incident descriptions """
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
                list_process_cp = list_process[i].copy()
                tmp_record = Record.get_record(station, incident_metadata,
                 list_process_cp)
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
        """ Adds earthquake hypocenter to the project. """
        self.metadata["project_source_hypocenter"] = (lat, lon, depth)
        Station.pr_source_loc = (lat, lon, depth)

    # processing labels
    def add_processing_label(self, label_name, label_type, hyper_parameters):
        """ Creates a processing label """
        TimeSeries._add_processing_label(label_name, label_type,
         hyper_parameters)
        
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
                    print(
                        f"{pr_l} is not a valid processing label. Command\
                            ignored."
                        )
                    return False
        
        return True

    def valid_processing_labels(self):
        """ Returns a list of valid processing labels """
        for i,item in enumerate(TimeSeries.label_types):
            print(f"{i}: {item} - args: {TimeSeries.label_types[item]}")

    # station filtering
    def add_station_filter(self, station_filter_name, station_filter_type, hyper_parameters):
        """ Adds a new filter for selecting stations """
        Station.add_station_filter(station_filter_name, station_filter_type, hyper_parameters)
    
    def valid_station_filter_type(self):
        """ Returns a list of valid filters for selecting stations. """
        for i,item in enumerate(Station.station_filter_types):
            print(f"{i}: {item}")

    def list_of_station_filters(self):
        """ Returns a list of available processing labels"""
        if not Station.station_filters:
            return
        for item in Station.station_filters:
            print(item, '-->', Station.station_filters[item])

    # Analysis interface
    def plot_velocity_records(self, list_inc,list_process,list_filters,opt_params):
        """ Plots 3 velocity timeseries one page per station and their
         fft values"""
        
        if not self._is_incident_valid(list_inc):
            return

        if not self._is_processing_label_valid(list_process):
            return

        records = self._extract_records(list_inc, list_process, list_filters)
        
         # Check number of input timeseries
        if len(records[0]) > len(self.color_code):
            print("[ERROR]: Too many timeseries to plot!")
            # sys.exit(-1)
            return

        plt.figure()
        
        for record in records:
            
                 
            fig, axarr = plt.subplots(nrows=3, ncols=3, figsize=(14, 9))
            
            # h1, h2, UD
            for i in range(3):
                axarr[i][0] = plt.subplot2grid((3,3),(i,0),rowspan=1, colspan=2)
                axarr[i][1] = plt.subplot2grid((3,3),(i,2),rowspan=1, colspan=1)
                axarr[i][0].grid(True)

            x_lim_f = check_opt_param_minmax(opt_params, 'zoom_in_freq')
            x_lim_t = check_opt_param_minmax(opt_params, 'zoom_in_time')
                           

            for i,item in enumerate(record):
                if not item:
                    continue
                axarr[0][0].plot(item.time_vec,item.vel_h1.value,
                 self.color_code[i], label=list_inc[i])
                axarr[0][1].plot(item.freq_vec,abs(item.vel_h1.fft_value),
                 self.color_code[i], label=list_inc[i])   
                axarr[1][1].plot(item.freq_vec,abs(item.vel_h2.fft_value),
                 self.color_code[i], label=list_inc[i])  
                axarr[1][0].plot(item.time_vec,item.vel_h2.value,
                 self.color_code[i], label=list_inc[i])
                axarr[2][0].plot(item.time_vec,item.vel_ver.value,
                 self.color_code[i], label=list_inc[i])
                axarr[2][1].plot(item.freq_vec,abs(item.vel_ver.fft_value),
                 self.color_code[i], label=list_inc[i])   

            for i in range(3):
                axarr[i][0].set_xlim(x_lim_t)
                axarr[i][1].set_xlim(x_lim_f)
            
            axarr[0][0].legend()
            axarr[0][0].set_title(
                f'Station at incident {list_inc[0]}:'\
                f'{record[0].station.inc_st_name[list_inc[0]]} - epicenteral dist:'\
                f'{record[0].epicentral_distance: 0.2f} km'\
                )    
            fig.tight_layout()     
           
            # plt.savefig("output_plot.pdf", format='pdf',
            # transparent=False, dpi=300)  
            # TODO: add another dictionary as metadata to the timeseries, a

    def plot_acceleration_records(self, list_inc,list_process,list_filters, opt_params):
        """ Plots 3 velocity timeseries one page per station and their
         fft values"""
        
        if not self._is_incident_valid(list_inc):
            return

        if not self._is_processing_label_valid(list_process):
            return

        records = self._extract_records(list_inc, list_process, list_filters)
        
         # Check number of input timeseries
        if len(records[0]) > len(self.color_code):
            print("[ERROR]: Too many timeseries to plot!")
            # sys.exit(-1)
            return

        plt.figure()
        
        for record in records:
                             
            fig, axarr = plt.subplots(nrows=3, ncols=3, figsize=(14, 9))
            
            # h1, h2, ver
            for i in range(3):
                axarr[i][0] = plt.subplot2grid((3,3),(i,0),rowspan=1, colspan=2)
                axarr[i][1] = plt.subplot2grid((3,3),(i,2),rowspan=1, colspan=1)
                axarr[i][0].grid(True)

            x_lim_t = check_opt_param_minmax(opt_params, 'zoom_in_time')
            x_lim_rsp = check_opt_param_minmax(opt_params, 'zoom_in_rsp')
               
            for i,item in enumerate(record):
                if not item:
                    continue
                axarr[0][0].plot(item.time_vec,item.acc_h1.value,
                 self.color_code[i], label=list_inc[i])
                axarr[0][1].plot(item.acc_h1.response_spectra[0],
                 item.acc_h1.response_spectra[1], self.color_code[i],
                 label=list_inc[i])   

                axarr[1][0].plot(item.time_vec,item.acc_h2.value,
                 self.color_code[i], label=list_inc[i])
                axarr[1][1].plot(item.acc_h2.response_spectra[0],
                 item.acc_h2.response_spectra[1], self.color_code[i],
                 label=list_inc[i])   

                axarr[2][0].plot(item.time_vec,item.acc_ver.value,
                 self.color_code[i], label=list_inc[i])
                axarr[2][1].plot(item.acc_ver.response_spectra[0],
                 item.acc_ver.response_spectra[1], self.color_code[i],
                 label=list_inc[i])   

            for i in range(3):
                axarr[i][0].set_xlim(x_lim_t)
                axarr[i][1].set_xlim(x_lim_rsp)

            axarr[0][0].legend()
            axarr[0][0].set_title(
                f'Station at incident {list_inc[0]}:'\
                f'{record[0].station.inc_st_name[list_inc[0]]} - epicenteral dist:'\
                f'{record[0].epicentral_distance: 0.2f} km'\
                )    
            fig.tight_layout()     
           
            # plt.savefig("output_plot.pdf", format='pdf',
            # transparent=False, dpi=300)  
            # TODO: add another dictionary as metadata to the timeseries, a
    
    
    def plot_record_section(self, list_inc,list_process,list_filters,opt_params):
        """ Plots seismic record section """
        
        if not self._is_incident_valid(list_inc):
            return

        if not self._is_processing_label_valid(list_process):
            return

        records = self._extract_records(list_inc, list_process, list_filters)

        # Check number of input timeseries
        if len(records[0]) > len(self.color_code):
            print("[ERROR]: Too many timeseries to plot!")
            # sys.exit(-1)
            return
      
        x_lim_t = check_opt_param_minmax(opt_params, 'zoom_in_time')
        comp = opt_params.get('comp',None)

        if not comp or (comp not in ["h1","h2","ver"]):
            if comp:
                LOGGER.warning(f"The component: {comp} is not supported. "+
                     "h1 is used.")
            comp = "h1"
        
        fig, axarr = plt.subplots(nrows=1, ncols=1, figsize=(14, 9))

        for k,record in enumerate(records):
            for i,item in enumerate(record):
                if not item:
                    continue
                                               
                if comp=="h1":
                    tmp_data = (0.8*item.vel_h1.value/item.vel_h1.peak_vv)+\
                        item.epicentral_distance
                elif comp == "h2":
                    tmp_data = (0.8*item.vel_h2.value/item.vel_h2.peak_vv)+\
                        item.epicentral_distance
                elif comp == "ver":
                    tmp_data = (0.8*item.vel_ver.value/item.vel_ver.peak_vv)+\
                        item.epicentral_distance
                else: 
                    LOGGER.error("Should never get here. Double check.")
                                    
                if k == 0: 
                    legend_label=list_inc[i]    
                else:
                    legend_label=None

                axarr.plot(item.time_vec, tmp_data, self.color_code[i], 
                label=legend_label, linewidth=0.2)
            
        axarr.set_xlabel('Time (s)')
        axarr.set_ylabel('Epicentral Distance (km)')        
        axarr.set_xlim(x_lim_t)
        axarr.legend()
        axarr.set_title(
             f"Normalized Seismic Record Section -"
             f"Number of stations/incident: {k+1}"
             f"- Component: {comp}"
        )    
        fig.tight_layout()    



    def show_stations_on_map(self,list_inc,list_process,list_filters):
        
        
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


    def which_records(self, list_inc,list_process,list_filters):
        """Represent all records that will pass a given filters"""
        if not self._is_incident_valid(list_inc):
            return

        if not self._is_processing_label_valid(list_process):
            return

        records = self._extract_records(list_inc, list_process, list_filters)
        
        for item in records:
            print(item[0]) 

    
    def list_of_incidents(self):
        """Returns list of incidents."""
        return list(self.incidents.keys())


    def compare_incidents(self,ls_inc, only_differences=False):
        """ 
        compares the incidents' meta data

        Inputs:

            ls_inc: list of incident names

            only_differerences: True or False

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



        


        
    



    
