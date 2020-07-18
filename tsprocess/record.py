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


class Record:
    """ Record Class """

    pr_db = None

    def __init__(self, time_vec, disp_h1, disp_h2, disp_ver,
                vel_h1, vel_h2, vel_ver,
                acc_h1, acc_h2, acc_ver,
                station, source_params):
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
        self.unique_id_1 = None 
        self.unique_id_2 = None
        self.notes = []
        self.this_record_hash = None
        self.epicentral_distance = None
        self.jb_distance = None
        self.azimuth = None
        self.back_azimuth = None
        self._compute_source_dependent_params()
        self._compute_record_unique_ids()
        self._compute_freq_vector()
        self.processed = []

    def __str__(self):
        return f"Record at {self.station.lat, self.station.lon} with"\
               f"{self.epicentral_distance} km distance from source."     

    @classmethod
    def connect_to_database(cls, database_name, cache_size):
        """ connecting to the projects databse """
        cls.mydb = DataBase(database_name,cache_size)

    def _compute_source_dependent_params(self):
        # compute distance and azimuth
        # extract source hyper parameters and record to source distance. 
        source_lat, source_lon, source_depth = self.source_params
        self.epicentral_distance = self._haversine(source_lat, source_lon,
         self.station.lat, self.station.lon)
    
    @staticmethod
    def generate_uid():
        """ generates 16 chars random combo from string and numbers"""
        char_list = string.ascii_uppercase + string.digits
        return ''.join(random.choice(char_list) for _ in range(16))

    def _compute_record_unique_ids(self):
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
            # we need to load the data 
            if incident_type == "hercules":
                station_folder = incident_metadata["output_stations_directory"]
                station_file = os.path.join(incident_metadata["incident_folder"]\
                    ,station_folder,st_name)
                try:
                    record_org = Record._from_hercules(station_file,station_obj,\
                        Station.pr_source_loc)
                    record_org.this_record_hash = hash_val
    
                    # put the record in the database.
                    Record.pr_db.set_value(hash_val,record_org)
                
                except Exception as e:
                    LOGGER.debug(e)
                    record_org = None
               
            if incident_type == "awp":
                print("AWP method is not implemented.")

            if incident_type == "rwg":
                print("RWG method is not implemented.")

        if not record_org:
            # this should never happen. 
            # if by this point record is still is None, something is
            # wrong with the record. 
            # TODO handle corrupt record.
            print('something is wrong with the record.')
            LOGGER.debug(f"{st_name} from {incident_name} could not load")
            return
            
        if not list_process:
            # no need for processed data. Return original record.
            return record_org

        
        processed_record = Record._get_processed_record(record_org,\
             list_process)

        return processed_record

    @staticmethod
    def _get_processed_record(record, list_process):
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
                return Record._get_processed_record(tmp_rec,list_process)
            
               
        # if the code flow gets here, it means the requested label is not
        # computed, or it is computed, however, some how could not retireve
        # from db. As a result, we need to apply that label to the record, 
        # add the hash value to the processed attribute, and put the hash and
        # value into the database.
        proc_record = Record._apply(record, pl)
        proc_record.this_record_hash = proc_hash_val
        
        # put data in the database
        Record.pr_db.set_value(proc_hash_val,proc_record)

        # add hash value into processed values
        # and update it on the data base.
        Record._add_proc_key(record, proc_hash_val)
        
        return Record._get_processed_record(proc_record, list_process)
 
    @staticmethod
    def _add_proc_key(record, hash_val):
        record.processed.append(hash_val)
        this_record_hash = record.this_record_hash
        Record.pr_db.set_value(this_record_hash,record)

    @staticmethod    
    def _apply(record, processing_label):

        # you are repeating yourself. Refactor it at the earliest
        # convenient.
        tmp_disp_h1 = record.disp_h1._apply(processing_label)
        tmp_disp_h2 = record.disp_h2._apply(processing_label)
        tmp_disp_ver = record.disp_ver._apply(processing_label)
        tmp_vel_h1 = record.vel_h1._apply(processing_label)
        tmp_vel_h2 = record.vel_h2._apply(processing_label)
        tmp_vel_ver = record.vel_ver._apply(processing_label)
        tmp_acc_h1 = record.acc_h1._apply(processing_label)
        tmp_acc_h2 = record.acc_h2._apply(processing_label)
        tmp_acc_ver = record.acc_ver._apply(processing_label)

        
        # TODO: check time vector
        tmp_time_vector = range(len(tmp_disp_h1.value))*\
                record.acc_h1.delta_t + record.acc_h1.t_init_point


        return Record(tmp_time_vector, tmp_disp_h1, tmp_disp_h2, tmp_disp_ver,
                                       tmp_vel_h1, tmp_vel_h2, tmp_vel_ver,
                                       tmp_acc_h1, tmp_acc_h2, tmp_acc_ver,
                                       record.station, record.source_params)

    @staticmethod
    def _haversine(lat1, lon1, lat2, lon2):
        # convert decimal degrees to radians 
        # this method is also defined in station module.
        # TODO: move them to a util module. 
        try:
            lon1, lat1, lon2, lat2 = map(radians, [lon1, lat1, lon2, lat2])
        except Exception:
            return None
        # haversine formula 
        dlon = lon2 - lon1 
        dlat = lat2 - lat1 
        a = sin(dlat/2)**2 + cos(lat1) * cos(lat2) * sin(dlon/2)**2
        c = 2 * asin(sqrt(a)) 
        r = 6371 # in kilometers
        return c * r

    @staticmethod
    def _from_hercules(filename,station_obj,source_hypocenter):
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
                # Write timeseries to files. Please not that Hercules files 
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
            print(e)
            # sys.exit(-1)
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
    
        # self.delta_t = times[1] - times[0]
        # Group headers
        # headers = [dis_header, vel_header, acc_header]

        return Record(times, disp_h1, disp_h2, disp_ver,
                    vel_h1, vel_h2, vel_ver,
                    acc_h1, acc_h2, acc_ver,
                    station_obj, source_hypocenter)

