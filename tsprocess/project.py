"""
project.py
====================================
The core module for the project class.
"""

from .database import DataBase
from typing import Any, List, Set, Dict, Tuple, Optional
from .incident import Incident
import os



class Project:
    """ Project Class """
    def __init__(self,name):
        """ initiating a project"""
        self.name = name
        self.pr_db = None
        self.incidents = {}
        self._connect_to_database()

    def _connect_to_database(self):
        self.pr_db = DataBase(self.name+"_db", cache_size=2000)
        
    def add_incident(self, incident_folder):
        """
        Adds a new incident to the project. 
        """
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

        if inc_des["incident_type"] == "hercules":
            self._load_hercules_incident(incident_folder)
            return

        if inc_des["incident_type"] == "awp":
            self._load_awp_incident(incident_folder)
            return

        if inc_des["incident_type"] == "rwg":
            self._load_rwg_incident(incident_folder)
            return

      
    def _load_awp_incident(self, incident_folder):
        print("Loading AWP incident is not implemented.")
        return
    
    def _load_rwg_incident(self, incident_folder):
        print("Loading RWG incident is not implemented.")
        return

    def _load_hercules_incident(self, incident_folder):
        print("Loading Hercules incident is not implemented.")
        return

    @staticmethod
    def _read_incident_description(incident_folder):
        incident_description = {}
        with open(os.path.join(incident_folder,'description.txt'),'r') as fp:
            while True:
                line = fp.readline()
                if not line:
                    break
                key, value = tuple(line.strip().split("="))
                incident_description[key.strip()] = value.strip()
        return incident_description

    


    def remove_incident(self, incident_name):
        """Removes incident from the project. """
        pass

    
