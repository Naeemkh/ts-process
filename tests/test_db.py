import unittest

from ts_process import database as db

class TestDataBase(unittest.TestCase):
    def setUp(self):
        self.dbname = 'test_database'
        self.csize = 10

    def test_create_database_singleton(self):
        db_1 = db.DataBase(self.dbname, self.csize)
        db_2 = db.DataBase(self.dbname, self.csize)

        self.assertEqual(db_1,db_2)
    
    def test_set_and_get_value(self):
        db_3 = db.DataBase('mytest',10)
        db_3.set_value('x1',100)
        self.assertEqual(db_3.get_value('x1'),100)
        




