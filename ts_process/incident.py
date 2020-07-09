"""
incident.py
====================================
The core module for the Incident class.
"""

import database as db


class Incident:
    """ Incident Class """
    pr_db = None

    def __init__(self,folder_path):
        """ initiating a project"""
        self.folder_path = folder_path
        