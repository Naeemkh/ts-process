import doctest
import unittest

import tsprocess.record as record
import tsprocess.station as station
import tsprocess.project as project
import tsprocess.ts_utils as ts_utils
import tsprocess.database as database
import tsprocess.incident as incident
import tsprocess.timeseries as timeseries
import tsprocess.ts_utils as ts_plot_utils
import tsprocess.seismicsource as seismicsource


def test_doctest_suit():
    test_suit = unittest.TestSuite()

    # add tests
    test_suit.addTest(doctest.DocTestSuite(record))
    test_suit.addTest(doctest.DocTestSuite(station))
    test_suit.addTest(doctest.DocTestSuite(project))
    test_suit.addTest(doctest.DocTestSuite(ts_utils))
    test_suit.addTest(doctest.DocTestSuite(database))
    test_suit.addTest(doctest.DocTestSuite(incident))
    test_suit.addTest(doctest.DocTestSuite(timeseries))
    test_suit.addTest(doctest.DocTestSuite(ts_plot_utils))
    test_suit.addTest(doctest.DocTestSuite(seismicsource))
    
    # set runner
    runner = unittest.TextTestRunner(verbosity=2).run(test_suit)

    assert not runner.failures