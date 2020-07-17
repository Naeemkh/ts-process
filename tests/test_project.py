import os
import glob
import unittest

from tsprocess.project import Project

class TestProject(unittest.TestCase):

    def test_create_project_singleton(self):
        p_1 = Project("project_1")
        self.assertTrue(isinstance(p_1,Project))

        p_2 = Project("project2")
        self.assertFalse(isinstance(p_2,Project))

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
