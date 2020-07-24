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
from .ts_utils import haversine, compute_azimuth, rotate_record


class Record:
    """ Record Class """

    pr_db = None
    processing_labels = {}
    label_types = {
        'rotate': 'angle: rotation angle'
    }

    def __init__(self, time_vec, disp_h1, disp_h2, disp_ver,
                vel_h1, vel_h2, vel_ver,
                acc_h1, acc_h2, acc_ver,
                station, source_params,
                hc_or1, hc_or2):

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
        hash_val = hashlib.sha256((incident_name+st_name).\
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
                station_file = os.path.join(incident_metadata[
                    "incident_folder"],station_folder,st_name)
                try:
                    record_org = Record._from_hercules(station_file,
                        station_obj, Station.pr_source_loc, hr_or1, hr_or2)
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
                                       n_hc_or1, n_hc_or2)

    @staticmethod
    def _from_hercules(filename,station_obj,source_hypocenter, hr_or1, hr_or2):
        """ Loads an instance of Hercules simulation results at one station.
        Returns a Record object.
        
        Inputs:
            | filename: station file name (e.g., station.10)
            | station_obj: a station object corresponding that filename
            | source_hypocenter: project source location

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
                
                # Write timeseries to files. Please note that Hercules files 
                # have the vertical component positive pointing down so we have
                # to flip it here to match the BBP format in which vertical
                # component points up

                times.append(pieces[0])
                dis_h1.append(pieces[1])
                dis_h2.append(pieces[2])
                dis_ver.append(-1 * pieces[3])
                vel_h1.append(pieces[4])
                vel_h2.append(pieces[5])
                vel_ver.append(-1 * pieces[6])
                acc_h1.append(pieces[7])
                acc_h2.append(pieces[8])
                acc_ver.append(-1 * pieces[9])

        except IOError as e:
            LOGGER.debug(str(e))            
        finally:
            input_fp.close()
            
        # Convert to NumPy Arrays
        times = np.array(times)
        vel_h1 = np.array(vel_h1)
        vel_h2 = np.array(vel_h2)
        vel_ver = np.array(vel_ver)
        acc_h1 = np.array(acc_h1)
        acc_h2 = np.array(acc_h2)
        acc_ver = np.array(acc_ver)
        dis_h1 = np.array(dis_h1)
        dis_h2 = np.array(dis_h2)
        dis_ver = np.array(dis_ver)

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
                    hr_or1, hr_or2)