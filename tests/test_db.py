import unittest
from ..ts_process.database import DataBase

class TestDataBase(unittest.TestCase):
    def setUp(self):
        self.dbname = 'test_database'
        self.csize = 10

    def test_create_database_singleton(self):
        db_1 = DataBase(self.dbname, self.csize)
        db_2 = DataBase(self.dbname, self.csize)

        self.assertEqual(db_1,db_2)




if __name__ == "__main__":
    unittest.main()




