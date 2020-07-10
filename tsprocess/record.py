"""
record.py
====================================
The core module for the Record class.
"""

from .database import DataBase
import hashlib

class Record:
    """ Record Class """

    pr_db = None

    def __init__(self, time_vec, disp_h1, disp_h2, disp_ver,
                vel_h1, vel_h2, vel_ver,
                acc_h1, acc_h2, acc_ver,
                station):
        self.station = station
        self.time_vec = time_vec
        self.disp_h1 = disp_h1
        self.disp_h2 = disp_h2
        self.disp_ver = disp_ver
        self.vel_h1 = vel_h1
        self.vel_h2 = vel_h2
        self.vel_ver = vel_ver
        self.acc_h1 = acc_h1
        self.acc_h2 = acc_h2
        self.acc_ver = acc_ver
        self.notes = []
        self.epicentral_distance = None
        self.jb_distance = None
        self.azimuth = None
        self.back_azimuth = None
        self._compute_source_params()
        self.processed = []     

    @classmethod
    def connect_to_database(cls, database_name, cache_size):
        """ connecting to the projects databse """
        cls.mydb = DataBase(database_name,cache_size)

    def _compute_source_params(self):
        # compute distance and azimuth
        pass
    
    def _compute_time_vec(self):
        # all records should have the most common length and dt
        pass

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

    def _apply(self):
        pass

    @staticmethod
    def get_record(filename, processing_label):
        
        # from the description.txt we know the type of record (hercules, AWP, and so on)
        # assume it is hercules

        record_type = "hercules"


        if record_type == "hercules":
            # create_hash_value: file_name+file_content:
                
            with open(filename, 'r') as file:
                file_content = file.read()

            if not file_content:
                # think about handling this
                return None

            file_content_and_name = file_content+filename

            hash_val = hashlib.sha256((file_content_and_name).encode('utf-8')).hexdigest()
            print(hash_val)
            

            # look for hash value 
            if Record.mydb.get_value(hash_val):
                return Record.mydb.get_value(hash_val)

            # if it is not in the database, we need to read the file. 
            value = Record._from_hercules(filename)
            Record.mydb.set_value(hash_val,value)
            return value