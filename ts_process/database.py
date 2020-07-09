"""
database.py
====================================
The core module for communicating with the database.
"""

from sqlitedict import SqliteDict
from collections import OrderedDict

class DataBase:
    """ database class (singleton pattern) """

    _instance = None

    def __new__(cls, dbname, cache_size):
        if not cls._instance:
            cls._instance = super(DataBase, cls).__new__(cls)
        return cls._instance

    def __init__(self, dbname, cache_size = 10000):
        self.db = SqliteDict(f'{dbname}.sqlite', autocommit=True)
        self.connected = True
        self.cache_size = cache_size
        self.cache = OrderedDict()

    def set_value(self, key, value):
        """ 
        Sets the key and given value in the database. If the key is exist,
        it will override the value. In that case, will remove the key from the
        cache. The cache will load the new value with the get_value command. 
        """
        try:
            self.db[key] = value
            del self.cache[key]
        except Exception:
            pass
        finally:
            pass 

    def delete_value(self,key):
        """ Deletes the key, and its value from both in-memory and on-disk.
        If the key is not found, simply ignores it.
        """
        try:
            del self.db[key]
            del self.cache[key]
        except KeyError:
            pass
    
    def get_value(self, key):
        """ Returns the value in the following order:\n
        1) It will look for the value in the cache and return it, if not found\n
        2) will look for the value in the disk and return it, if not found\n
        3) will return False.
        """
        value = None
        try:
            value = self.cache[key]
        except:
            pass

        if not value:
            try:
                tmp = self.db[key]
                if len(self.cache) >  self.cache_size:
                    self.cache.popitem(last=False)
                self.cache[key] = tmp
                return tmp
            except Exception:
                return False
        else:
            return value
        
    def close_db(self):
        """ Commits changes to the database, closes the database, clears the 
        cache."""

        self.db.commit()
        self.db.close()
        self.cache = None
        self.connected = False




