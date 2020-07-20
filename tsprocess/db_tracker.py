"""
db_tracker.py
====================================
The core module for the DatabaseTracker class.
"""

from .log import LOGGER

class DataBaseTracker:
    """ DatabaseTracker Class """

    def __init__(self, name, project,  buffer_capacity = 3):
        self.name = name
        self.project = project
        self.buffer_capacity = buffer_capacity
        self.dt_db = self.project.pr_db
        self.buffer = dict()
        self._initiate_tracker()

    def _initiate_tracker(self):
        try:
            tracker = self.dt_db.get_nested_container(self.name)
            if not tracker:            
                self.dt_db.set_value(self.name, dict())
        except Exception as e:
            LOGGER.error(str(e))

    def start_tracking_incident(self, incident_name):
        """ creates an empty list for a new incident. """

        current_tracker = self.dt_db.get_nested_container(self.name)

        if incident_name in list(current_tracker.keys()):
            LOGGER.debug(f"Tracker is found for Incident: '{incident_name}'.")
        else:
            self.dt_db.update_nested_container(self.name, incident_name,[])
            LOGGER.debug(f"Tracker is set up for Incident: '{incident_name}'.")

        self.buffer[incident_name] = list()

    def track_incident_hash(self, incident_name, hash_value):
        
        if incident_name not in list(self.project.incidents.keys()):
            LOGGER.warning('Incident is not added to the projcet. Ignored.')
            return
        
        if incident_name in list(self.buffer.keys()):
            self.buffer[incident_name].append(hash_value)
            LOGGER.debug(f"Value {hash_value} is added to the buffer.")
        else:
            self.buffer[incident_name] = [hash_value]
            LOGGER.debug(f"Buffer initiated and value {hash_value} is added to the buffer.")

        buffer_size = sum([val for val in  {key: len(value) for key, value in self.buffer.items()}.values()])

        if buffer_size > self.buffer_capacity:
            try:
                self.add_to_database()
                self.buffer = {key: []  for
                 key, _ in self.buffer.items()}
            except Exception:
                pass

    def add_to_database(self):
        # here update nested container should be called. 

        try:
            
            for key, item in self.buffer.items():
                try:
                    self.dt_db.update_nested_container(self.name, key, item)
                    LOGGER.debug(f"incident '{key}' hash values are updated.")
                except:
                    raise Exception
                    # current_hash_values[key] = item
        except Exception as e:
            print(e)
            LOGGER.debug(f"Something went wrong in adding tracking data.")
            
    def remove_incident(self, incident_name):
        self.dt_db.update_nested_container(self.name, incident_name, [], append=False)              


    

