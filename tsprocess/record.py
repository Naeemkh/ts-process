"""
record.py
====================================
The core module for the Record class.
"""

from .database import DataBase
import hashlib
from .timeseries import  Disp, Vel, Acc, Raw, Unitless
import numpy as np 

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

    @staticmethod
    def _from_hercules(filename,station_obj):
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
                                         (pieces[0], pieces[1], pieces[2], pieces[3]))
                        vel_header.append("# her header: # %s %s %s %s\n" %
                                         (pieces[0], pieces[4], pieces[5], pieces[6]))
                        acc_header.append("# her header: # %s %s %s %s\n" %
                                         (pieces[0], pieces[7], pieces[8], pieces[9]))
                    else:
                        dis_header.append("# her header: %s\n" % (line))
                    continue
                pieces = line.split()
                pieces = [float(piece) for piece in pieces]
                # Write timeseries to files. Please not that Hercules files have
                # the vertical component positive pointing down so we have to flip it
                # here to match the BBP format in which vertical component points up
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
            sys.exit(-1)
        finally:
            # All done
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
                    station_obj)

