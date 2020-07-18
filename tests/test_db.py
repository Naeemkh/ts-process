import os
import glob
import unittest
import doctest

import tsprocess.database as database
from tsprocess.database import DataBase

class TestDataBase(unittest.TestCase):
    def setUp(self):
        self.dbname = 'test_database'
        self.csize = 10

    def test_create_database_singleton(self):
        db_1 = DataBase(self.dbname, self.csize)
        db_2 = DataBase(self.dbname, self.csize)

        self.assertEqual(db_1,db_2)
    
    def test_set_and_get_value(self):
        db_3 = DataBase('mytest',10)
        db_3.set_value('x1',100)
        self.assertEqual(db_3.get_value('x1'),100)

    def tearDown(self):
        files = [glob.glob(e) for e in ['*.sqlite', '*.log']]
        flat_list = [item for sublist in files for item in sublist]
        f_files = [os.path.join(os.path.dirname(os.path.realpath(__file__)),e)
         for e in flat_list]
       
        for f in f_files:
            try:
                os.remove(f)
            except Exception:
                pass

    def load_tests(loader, tests, ignore):
        tests.addTests(doctest.DocTestSuite(database))
        return tests
        




suite = unittest.TestSuite()
suite.addTest(doctest.DocTestSuite(database))
runner = unittest.TextTestRunner(verbosity=2)
runner.run(suite)