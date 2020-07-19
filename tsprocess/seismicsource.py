"""
seismicsource.py
====================================
The core module for the SeismicSource class.
"""

import os


class SeismicSource:
    """ SeismicSource Class """

    def __init__(self,source_directory, incident_type):
        self.source_directory = source_directory
        self.coords = []
        self.seismic_moment = []
        self.strike = []
        self.dip = []
        self.rake = []
        self.area = []
        self.slip_function = []
        self.metadata = {}
        self.domain_surface_corners = []
        self._load_source_from_disk(incident_type)
        self._load_domain_surface_corners()
        self._load_source_params_hercules()

    def _load_source_from_disk(self, incident_type):

        if incident_type == "hercules":

            with open((os.path.join(self.source_directory,'source.in')),
             'r') as fp:
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
        
        if incident_type == "awp":
            print("Methods for AWP is not implemented.")                 
            return

        if incident_type == "rwg":
            print("Methods for rwg is not implemented.")                 
            return


    def _load_domain_surface_corners(self):
        #TODO Upon getting the format of all sources, refactor this code.

        with open(os.path.join(self.source_directory,'source.in'), 'r') as fp:
         
            start_reading_corners = False
            while True:
                line = fp.readline()
                if not line:
                    break
                if line.startswith("#"):
                    continue
                if (("domain_surface_corners" in line) and ("=" in line) and
                 (len(line.split())==2)):
                    start_reading_corners = True
                
                if start_reading_corners:
                    i = 0
                    while i < 4:
                        line = fp.readline()
                        tmp_line = line.split()
                        if len(tmp_line) == 2:
                            self.domain_surface_corners.append(
                                [float(tmp_line[0].strip()),
                                float(tmp_line[1].strip())]
                                )
                            i = i + 1
                    break

    def _load_source_params_hercules(self):
        with open(os.path.join(self.source_directory,'area.in'), 'r') as fp:
            self.area = [float(i) for i in (fp.read().split())]
        
        with open(os.path.join(self.source_directory,'coords.in'), 'r') as fp:
            i = 0 
            while i < int(self.metadata["number_of_point_sources"]):
                line = fp.readline()
                tmp_line = line.split()
                if len(tmp_line) == 3:
                    self.coords.append([float(tmp_line[0].strip()),
                     float(tmp_line[1].strip()), float(tmp_line[2].strip())])
                    i = i + 1

        with open(os.path.join(self.source_directory,'dip.in'), 'r') as fp:
            self.dip = [float(i) for i in (fp.read().split())]

        with open(os.path.join(self.source_directory,'rake.in'), 'r') as fp:
            self.rake = [float(i) for i in (fp.read().split())]

        with open(os.path.join(self.source_directory,'slip.in'), 'r') as fp:
            self.slip = [float(i) for i in (fp.read().split())]
        
        with open(os.path.join(self.source_directory,'strike.in'), 'r') as fp:
            self.strike = [float(i) for i in (fp.read().split())]

        with open(os.path.join(self.source_directory,
         'slipfunction.in'), 'r') as fp:
            
            while True:
                line = fp.readline()
                if not line:
                    break
                self.slip_function.append([float(i) for i in (line.split())])