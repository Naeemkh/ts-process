"""
project.py
====================================
The core module for the project class.
"""

from .database import DataBase


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
        """ Adds a new incident to the project. """
        pass

    def remove_incident(self, incident_name):
        """Removes incident from the project. """
        pass

    
