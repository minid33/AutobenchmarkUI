import datetime
import json
import unittest

from .. import app, configure_app, round_date
from . import BaseMongoTest, GetData


class BaseAutobenchmarkTestCase(BaseMongoTest):
    """
    This is a base testing class for data driven UI work, handles making
    a new database on a local server, setting Flask into a testing
    configuration and finally erases the local DB when everything is done.
    """

    def setUp(self):
        BaseMongoTest.setUp(self)
        configure_app(self.cfg.cfgname)

        self.app = app.test_client()

        # Delete the entry time from the test data
        timeStrippedTestData = GetData(entrytime=None)

        #Make some sample data
        self.testjson = json.dumps(timeStrippedTestData)


class BaseJsonTests(BaseAutobenchmarkTestCase):

    def assertKnownGoodJSON(self, url, expected):
        """
        Gets JSON from a URL and asserts that the known data is equal.
        """
        self.app.put('/storeResultEntry/', data=self.testjson)
        result = self.app.get(url)
        actual = json.loads(result.data)['results']
        self.assertEqual(expected, actual)


class BasePageTests(BaseAutobenchmarkTestCase):

    def assertPageLoaded(self, url):
        """
        assert that a HTTP 200 status is recieved and that the length of
        """
        for i in range(5):
            self.app.put('/storeResultEntry/', data=self.testjson)
        r = self.app.get(url)
        self.assertGreater(len(r.data), 0)
        self.assertEqual(r.status, '200 OK')


    #def testIndexPageGETReturnsHTML(self):
    #    r = self.app.get('/')
    #    self.assertTrue(len(r.data) > 0)
    #    self.assertTrue(r.status, '200 OK')
    #
class StoreResultEntryTests(BaseAutobenchmarkTestCase):

    def getReturnedData(self):
        r = self.app.put('/storeResultEntry/', data=self.testjson)
        return json.loads(r.data)

    def testDataCanBeInserted(self):
        """
        This test assert that valid data can be entered
        """
        r = self.app.put('/storeResultEntry/', data=self.testjson)
        self.assertEquals(r.status, '200 OK')

    def testAggregatesInsertedIntoResults(self):
        self.assertIn('AggregateData', self.getReturnedData().keys())

    def testAggregatesCreateKeyForEachMetric(self):
        testmetrics = json.loads(self.testjson)['metrics']
        self.assertItemsEqual(testmetrics.keys(),
                              self.getReturnedData()['AggregateData'].keys())

    def testAggregatesCreateAggregatesForEachMetric(self):
        aggData = self.getReturnedData()['AggregateData']
        for key, value in aggData.items():
            self.assertItemsEqual(['mean', 'median', 'min', 'max', 'stddev'],
                                  aggData[key].keys())

    def testAggregatesCreateCorrectValuesForKnownGoodData(self):
        aggData = self.getReturnedData()['AggregateData']
        self.assertEqual(int(aggData['fps']['mean']), 32)
        self.assertEqual(aggData['frametime']['min'], 0.2)


class AdminTests(BaseAutobenchmarkTestCase):

    def testAdminPageServed(self):
        response = self.app.get('/admin')
        self.assertEqual(response.status, '200 OK')


class RoundDateTests(unittest.TestCase):

    def testRoundsToHour(self):
        d = datetime.datetime(2000, 1, 1, 1, 1, 1, 1)
        s = round_date(d)
        self.assertEqual(s, '2000-01-01T01:00:00')
