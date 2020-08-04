"""
record.py
====================================
The core module for the Record class.
"""
import os
import random
import string
import hashlib
from math import radians, cos, sin, asin, sqrt

import numpy as np

from .log import LOGGER
from .station import Station
from .database import DataBase
from .timeseries import  Disp, Vel, Acc, Raw, Unitless
from .ts_utils import (haversine, compute_azimuth, rotate_record, read_smc_v2,
                       unit_convention_factor)


class Record:
    """ Record Class """

    pr_db = None
    ver_orientation_conv = None
    unit_convention = None
    processing_labels = {}
    label_types = {
        'rotate': 'angle: rotation angle'
    }

    def __init__(self, time_vec, disp_h1, disp_h2, disp_ver,
                vel_h1, vel_h2, vel_ver,
                acc_h1, acc_h2, acc_ver,
                station, source_params,
                hc_or1, hc_or2, ver_or):

        self.station = station
        self.time_vec = time_vec
        self.freq_vec = None
        self.disp_h1 = disp_h1
        self.disp_h2 = disp_h2
        self.disp_ver = disp_ver
        self.vel_h1 = vel_h1
        self.vel_h2 = vel_h2
        self.vel_ver = vel_ver
        self.acc_h1 = acc_h1
        self.acc_h2 = acc_h2
        self.acc_ver = acc_ver
        self.source_params = source_params
        self.hc_or1 = hc_or1
        self.hc_or2 = hc_or2
        self.ver_or = ver_or
        self.unique_id_1 = None 
        self.unique_id_2 = None
        self.notes = []
        self.this_record_hash = None
        self.epicentral_distance = None
        self.jb_distance = None
        self.azimuth = None
        self._compute_source_dependent_params()
        self._compute_record_unique_ids()
        self._compute_freq_vector()
        self.processed = []

    def __str__(self):
        return f"Record at {self.station.lat, self.station.lon} with "\
               f"{self.epicentral_distance:.2f} km distance from source."    

    def __repr__(self):
        return f"Record({self.time_vec},"\
               f"{self.disp_h1},{self.disp_h2},{self.disp_ver}"\
               f"{self.vel_h1},{self.vel_h2},{self.vel_ver}"\
               f"{self.acc_h1},{self.acc_h2},{self.acc_ver}"\
               f"{self.station}.{self.source_params})"
                        
    @classmethod
    def _add_processing_label(cls, label_name, label_type, argument_dict):
        """ Adds new processing label to the Record class. 

        Inputs:
            | label_name: optional processing label name
            | label_type: should be one of the valid label types
            | argument_dict: dictionary of arguments that is required for that 
              processing label type.

        """

        if label_name in cls.processing_labels:
            LOGGER.warning(f"label name: '{label_name}' has been already used. "
            "Try another name.")
            return

        if label_type not in cls.label_types:
            LOGGER.warning("Label type is not supported. Command is ignored.")
            return
        
        cls.processing_labels[label_name] = [label_type, argument_dict]


    def _compute_source_dependent_params(self):
        """ Computes parameters that are dependent to the distance and azimuth
        between source and the station. 
        """
        # compute distance and azimuth
        # extract source hyper parameters and record to source distance. 
        source_lat, source_lon, source_depth = self.source_params
        self.epicentral_distance = haversine(source_lat, source_lon,
         self.station.lat, self.station.lon)
        self.azimuth = compute_azimuth(source_lat, source_lon,
         self.station.lat, self.station.lon)
    
    @staticmethod
    def generate_uid():
        """ generates 16 chars random combination from string and numbers"""
        char_list = string.ascii_uppercase + string.digits
        return ''.join(random.choice(char_list) for _ in range(16))

    def _compute_record_unique_ids(self):
        """ Assigns two randomly generated 16 char id to each record. """
        self.unique_id_1 = self.generate_uid()
        self.unique_id_2 = self.generate_uid()
        return
 
    
    def _compute_time_vec(self):
        # all records should have the most common length and dt
        pass

    def _compute_freq_vector(self):
        # all records should have same length, and df
        # choosing value from one of signals
        # however, make sure that all are the same. 
        df = self.acc_h1.delta_f
        s_size = len(self.acc_h1.fft_value)
        self.freq_vec = np.array(range(s_size))*df + self.acc_h1.f_init_point

    def export_to_hercules(self, filename):
        pass

    def export_to_bbp(self, filename):
        pass

    def export_to_awp(self, filename):
        pass

    def export_to_rwg(self, filename):
        pass

    def export_to_edge(self, filename):
        pass

    @staticmethod
    def get_record(station_obj, incident_metadata, list_process):
        """ Returns final processed reocord based on station, incident, and
        required list of processes. If the record is found in database, it will
        be returned, otherwise, it will be processed and will be returned. The
        processed record will be stored in the database for future use.

        Inputs:
            | station_obj: a station object
            | incident_metadata: a dictionary of incidance metadata
            | list_process: list of required processes
        
        Output:
            | record object
        """

        incident_name = incident_metadata["incident_name"]
        incident_type = incident_metadata["incident_type"]
       
       
        # extract station name:
        try:
            st_name = station_obj.inc_st_name[incident_name]
        except KeyError as e:
            print(e)
            return

        # generate original record hash value.
        hash_val = hashlib.sha256(
            (incident_name + st_name + Record.ver_orientation_conv +\
             Record.unit_convention).\
            encode('utf-8')).hexdigest()

        # retrieve the record from database.
        record_org = Record.pr_db.get_value(hash_val)

        if not record_org:
            LOGGER.debug(f"Original Record of incident: {incident_name}  -"
             f" type: {incident_type} at station: {st_name} has not been loaded"
              " to the database. Loading ... " )
            # we need to load the data 
            if incident_type == "hercules":

                station_folder = incident_metadata["output_stations_directory"]
                hr_or1 = float(incident_metadata["hr_comp_orientation_1"])
                hr_or2 = float(incident_metadata["hr_comp_orientation_2"])
                ver_or = incident_metadata["ver_comp_orientation"]
                inc_unit = incident_metadata["incident_unit"]

                station_file = os.path.join(incident_metadata[
                    "incident_folder"],station_folder,st_name)
                try:
                    record_org = Record._from_hercules(station_file,
                        station_obj, Station.pr_source_loc, hr_or1, hr_or2,
                         ver_or, inc_unit)
                    record_org.this_record_hash = hash_val
    
                    # put the record in the database.
                    Record.pr_db.set_value(hash_val,record_org)
                    Record.pr_inc_tracker.track_incident_hash(incident_name,
                     hash_val)
                
                except Exception as e:
                    record_org = None
                    LOGGER.warning(f"{st_name} from {incident_name} could not"
                     " load. " + str(e))
               
            if incident_type == "cesmdv2":
                station_file = os.path.join(incident_metadata[
                    "incident_folder"],'seismic_records',st_name)

                try:
                    
                    # load cesmdv2 file
                    tmp_loaded_data, tmp_meta_data = read_smc_v2(station_file)

                    # create a record object
                    record_org = Record._from_cesmdv2(tmp_loaded_data, 
                     tmp_meta_data, station_obj, Station.pr_source_loc)

                    record_org.this_record_hash = hash_val
    
                    # put the record in the database.
                    Record.pr_db.set_value(hash_val,record_org)
                    Record.pr_inc_tracker.track_incident_hash(incident_name,
                     hash_val)
                
                except Exception as e:
                    record_org = None
                    LOGGER.warning(f"{st_name} from {incident_name} could not"
                     " load. " + str(e))
            
            if incident_type == "awp":
                print("AWP method is not implemented.")

            if incident_type == "rwg":
                print("RWG method is not implemented.")

        if not record_org:
            # this should never happen. 
            # if by this point record is still is None, something is
            # wrong with the record. 
            # TODO handle corrupt record.
            return
            
        if not list_process:
            # no need for processed data. Return original record.
            return record_org

        
        processed_record = Record._get_processed_record(incident_name, 
         record_org, list_process)

        return processed_record

    @staticmethod
    def _get_processed_record(incident_name, record, list_process):
        """ Returns the processed records based on hash value of the 
        record and the processing label. Developers should call this
        function only by original record.
        """

        # by this point the list of process has been controled for valid items. 
        
        try:
            pl = list_process.pop(0)
        except IndexError:
            return record

        hash_content = record.unique_id_1 + record.unique_id_1 + pl
        proc_hash_val = hashlib.sha256((hash_content).encode('utf-8')).\
            hexdigest()

        if proc_hash_val in record.processed:
            # this process has been done before, get it from database.
            tmp_rec = Record.pr_db.get_value(proc_hash_val)
            if tmp_rec:
                return Record._get_processed_record(incident_name, tmp_rec,
                 list_process)
            
               
        # if the code flow gets here, it means the requested label is not
        # computed, or it is computed, however, some how could not retireve
        # from db. As a result, we need to apply that label to the record, 
        # add the hash value to the processed attribute, and put the hash and
        # value into the database.
        proc_record = Record._apply(record, pl)
        proc_record.this_record_hash = proc_hash_val
        
        # put data in the database
        Record.pr_db.set_value(proc_hash_val,proc_record)
        Record.pr_inc_tracker.track_incident_hash(incident_name,
                    proc_hash_val)

        # add hash value into processed values
        # and update it on the data base.
        Record._add_proc_key(record, proc_hash_val)
        
        return Record._get_processed_record(incident_name, proc_record,
         list_process)
 
    @staticmethod
    def _add_proc_key(record, hash_val):
        """ Includes the hash value of the new processed record of this record
         into record's processed attribute. It also updates the record on the
         database.
        """ 
        record.processed.append(hash_val)
        this_record_hash = record.this_record_hash
        Record.pr_db.set_value(this_record_hash,record)
        # this hash value is already in the tracker. No need to add agian. 

    @staticmethod    
    def _apply(record, label_name):
        """ Applies the requested processing label on the record. Returns a 
        new Record object representing the processed record. """
        
        if label_name in Record.processing_labels:
            if  Record.processing_labels[label_name][0] == "rotate":
                def extract_params(angle):
                    return angle
    
                if label_name not in Record.processing_labels.keys():
                    # this should never be invoked. 
                    # I have checked the labels before. 
                    LOGGER.warning("Label is not supported, ignored.")
                    return
    
                
                label_kwargs = Record.processing_labels[label_name][1]
    
                p = extract_params(**label_kwargs)
                proc_record = rotate_record(record, p)
                tmp_time_vector = proc_record[0]
                tmp_disp_h1 = Disp(proc_record[1],record.disp_h1.delta_t,
                 record.disp_h1.t_init_point)
                tmp_disp_h2 = Disp(proc_record[2],record.disp_h2.delta_t,
                 record.disp_h2.t_init_point)
                tmp_disp_ver = Disp(proc_record[3],record.disp_ver.delta_t,
                 record.disp_ver.t_init_point)
                tmp_vel_h1 = Vel(proc_record[4],record.vel_h1.delta_t,
                 record.vel_h1.t_init_point)
                tmp_vel_h2 = Vel(proc_record[5],record.vel_h2.delta_t,
                 record.vel_h2.t_init_point)
                tmp_vel_ver = Vel(proc_record[6],record.vel_ver.delta_t,
                 record.vel_ver.t_init_point)
                tmp_acc_h1 = Acc(proc_record[7],record.acc_h1.delta_t,
                 record.acc_h1.t_init_point)
                tmp_acc_h2 = Acc(proc_record[8],record.acc_h2.delta_t,
                 record.acc_h2.t_init_point)
                tmp_acc_ver = Acc(proc_record[9],record.acc_ver.delta_t,
                 record.acc_ver.t_init_point)
                n_hc_or1 = proc_record[12]
                n_hc_or2 = proc_record[13]
            
                       
            else:
                LOGGER.warning("The processing lable is not defined.")
                return record

        else: 
        
        # you are repeating yourself. Refactor it at the earliest
        # convenient.
            tmp_disp_h1 = record.disp_h1._apply(label_name)
            tmp_disp_h2 = record.disp_h2._apply(label_name)
            tmp_disp_ver = record.disp_ver._apply(label_name)
            tmp_vel_h1 = record.vel_h1._apply(label_name)
            tmp_vel_h2 = record.vel_h2._apply(label_name)
            tmp_vel_ver = record.vel_ver._apply(label_name)
            tmp_acc_h1 = record.acc_h1._apply(label_name)
            tmp_acc_h2 = record.acc_h2._apply(label_name)
            tmp_acc_ver = record.acc_ver._apply(label_name)
            n_hc_or1 = record.hc_or1
            n_hc_or2 = record.hc_or2
            
    
            
            # TODO: check time vector
            tmp_time_vector = range(len(tmp_disp_h1.value))*\
                    record.acc_h1.delta_t + record.acc_h1.t_init_point   
    

        return Record(tmp_time_vector, tmp_disp_h1, tmp_disp_h2, tmp_disp_ver,
                                       tmp_vel_h1, tmp_vel_h2, tmp_vel_ver,
                                       tmp_acc_h1, tmp_acc_h2, tmp_acc_ver,
                                       record.station, record.source_params,
                                       n_hc_or1, n_hc_or2, record.ver_or)

    @staticmethod
    def _from_hercules(filename,station_obj,source_hypocenter, hr_or1, hr_or2,
     ver_or, inc_unit):
        """ Loads an instance of Hercules simulation results at one station.
        Returns a Record object.
        
        Inputs:
            | filename: station file name (e.g., station.10)
            | station_obj: a station object corresponding that filename
            | source_hypocenter: project source location
            | hr_or1: first horizontal component's orientation
            | hr_or2: second horizontal component's orientation
            | ver_or: vertical component's orientation
            | inc_unit: Incident unit

        Outputs:
            | Record object 
        """
        times = []
        acc_h1 = []
        vel_h1 = []
        dis_h1 = []
        acc_h2 = []
        vel_h2 = []
        dis_h2 = []
        acc_ver = []
        vel_ver = []
        dis_ver = []
        dis_header = []
        vel_header = []
        acc_header = []

        try:
            input_fp = open(filename, 'r')
        
            for line in input_fp:
                line = line.strip()
                # Skip comments
                if line.startswith("#") or line.startswith("%"):
                    pieces = line.split()[1:]
                    # Write header
                    if len(pieces) >= 10:
                        dis_header.append("# her header: # %s %s %s %s\n" %
                                         (pieces[0], pieces[1], pieces[2],
                                          pieces[3]))
                        vel_header.append("# her header: # %s %s %s %s\n" %
                                         (pieces[0], pieces[4], pieces[5],
                                          pieces[6]))
                        acc_header.append("# her header: # %s %s %s %s\n" %
                                         (pieces[0], pieces[7], pieces[8],
                                          pieces[9]))
                    else:
                        dis_header.append("# her header: %s\n" % (line))
                    continue
                pieces = line.split()
                pieces = [float(piece) for piece in pieces]
                
                if ver_or not in ["up", "down"]:
                    LOGGER.error("should not get here. Something is wrong with"
                    " vertical component orientation")
                    return

                if ver_or == Record.ver_orientation_conv:
                    ver_or_switch_factor = 1
                else:
                    ver_or_switch_factor = -1

                times.append(pieces[0])
                dis_h1.append(pieces[1])
                dis_h2.append(pieces[2])
                dis_ver.append(ver_or_switch_factor * pieces[3])
                vel_h1.append(pieces[4])
                vel_h2.append(pieces[5])
                vel_ver.append(ver_or_switch_factor * pieces[6])
                acc_h1.append(pieces[7])
                acc_h2.append(pieces[8])
                acc_ver.append(ver_or_switch_factor * pieces[9])

        except IOError as e:
            LOGGER.debug(str(e))            
        finally:
            input_fp.close()


        ucf = unit_convention_factor(Record.unit_convention, inc_unit)

        # Convert to NumPy Arrays
        times = np.array(times)
        vel_h1 = np.array(vel_h1)*ucf
        vel_h2 = np.array(vel_h2)*ucf
        vel_ver = np.array(vel_ver)*ucf
        acc_h1 = np.array(acc_h1)*ucf
        acc_h2 = np.array(acc_h2)*ucf
        acc_ver = np.array(acc_ver)*ucf
        dis_h1 = np.array(dis_h1)*ucf
        dis_h2 = np.array(dis_h2)*ucf
        dis_ver = np.array(dis_ver)*ucf

        dt = times[1] - times[0]

        disp_h1 = Disp(dis_h1, dt, times[0])
        disp_h2 = Disp(dis_h2, dt, times[0])
        disp_ver = Disp(dis_ver, dt, times[0])
    
        vel_h1 = Vel(vel_h1, dt, times[0])
        vel_h2 = Vel(vel_h2, dt, times[0])
        vel_ver = Vel(vel_ver, dt, times[0])
    
        acc_h1 = Acc(acc_h1, dt, times[0])
        acc_h2 = Acc(acc_h2, dt, times[0])
        acc_ver = Acc(acc_ver, dt, times[0])
    
        # Group headers
        # headers = [dis_header, vel_header, acc_header]

        return Record(times, disp_h1, disp_h2, disp_ver,
                    vel_h1, vel_h2, vel_ver,
                    acc_h1, acc_h2, acc_ver,
                    station_obj, source_hypocenter,
                    hr_or1, hr_or2, ver_or)

    @staticmethod
    def _from_cesmdv2(r_data, r_metadata, station_obj,source_hypocenter):
        """ Loads an instance of Hercules simulation results at one station.
        Returns a Record object.
        
        Inputs:
            | r_data: nested list of data. See ts_utils.read_smc_v2 funtions first
              return value
            | r_metadata: dictionary of metadata regarding the loaded record. See
              ts_utils.read_smc_v2 functions second return value
            | station_obj: a station object corresponding that filename
            | source_hypocenter: project source location

        Outputs:
            | Record object 
        """
         
        # TODO:if number of data samples and dt for different records are 
        # different, we need create a common dt and time vecotr.
        
        if len(r_data) != 3:
            LOGGER.warning(f"Station with id: {r_metadata.get('station_id','')}"
            "and type cesmdv2 record has missing component(s)."
            " Handling this situation is not implemented.")

        
        # generate the common dt and timevector
        dt_vector = []
        n_s = []
        orient = []
        for item in r_data:
            n_s.append(item[0])
            dt_vector.append(item[1])
            orient.append(item[2])

        if len(set(dt_vector)) != 1 or len(set(n_s)) !=1:
            LOGGER.warning(f"Station with id: {r_metadata.get('station_id','')}"
            "and type cesmdv2 record has different dt or number of samples."
            " Handling this situation is not implemented.")
            return None

        channels_unit = r_metadata['channels_unit']
        if "unknown" in channels_unit:
            LOGGER.warning(f"Station with id: {r_metadata.get('station_id','')}"
            "and type cesmdv2 record has at least one channel with unknown"
            " unit. Handling this situation is not implemented.")
            return None
              
        
        # choosing the smalles dt, and longest record.
        dt = dt_vector[0]
        n_sample = n_s[0]
        time_vec = np.arange(0,n_sample)*dt
        
        # show different combination of orientation for future improvement.
        LOGGER.debug(str(orient))
        
        tmp_disp_h = []
        tmp_vel_h  = []
        tmp_acc_h  = []
        h_orient = []

        while r_data:
            item = r_data.pop(0) 
            ch_unit = channels_unit.pop(0)
            ufc = unit_convention_factor(Record.unit_convention, ch_unit)

            if item[2] in ["up","down"]:
                # it is a vertical component.
                ver_or = item[2].lower()
                tmp_disp_ver = Disp(item[3][0]*ufc, item[1], 0)
                tmp_vel_ver = Vel(item[3][1]*ufc, item[1], 0)
                tmp_acc_ver = Acc(item[3][2]*ufc, item[1], 0)

            h_orient.append(item[2])
            tmp_disp_h.append(Disp(item[3][0]*ufc, item[1], 0))
            tmp_vel_h.append(Vel(item[3][1]*ufc, item[1], 0))
            tmp_acc_h.append(Acc(item[3][2]*ufc, item[1], 0))

        
        return Record(time_vec, tmp_disp_h[0], tmp_disp_h[1], tmp_disp_ver,
                    tmp_vel_h[0], tmp_vel_h[1], tmp_vel_ver,
                    tmp_acc_h[0], tmp_acc_h[1], tmp_acc_ver,
                    station_obj, source_hypocenter,
                    h_orient[0], h_orient[1], ver_or)




        


        





