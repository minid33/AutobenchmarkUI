import datetime
import unittest

from .. import dbmodel

from . import BaseMongoTest, GetData, GetSampleCursor, D_BENCHNAME


sometime = datetime.datetime.now()

#noinspection PyUnusedLocal
class FakeCollection(object):

    def distinct(self, keyname):
        return ['fakedata']

    def find(self, *args, **kwargs):
        return [{u'_id': None, u'entrytime': sometime}]


class TestDBModelFunctions(unittest.TestCase):
    def setUp(self):
        self.coll = lambda: [None, {'benchresults': FakeCollection()}]

    def testUniqueCollectionValues(self):
        self.assertEqual(
            ['fakedata'],
            dbmodel.get_unique_values_for_key('notused', self.coll)
        )

    def testGetLastEntryTime(self):
        actual = dbmodel.get_last_entry_time(self.coll)
        self.assertEqual(sometime, actual)


class TestAggregateFilters(unittest.TestCase):
    """
    This class of unit tests, tests adding filters to an existing aggregate
    filter
    """

    def setUp(self):
        self.sampleFilter = [
            {'$match': {'machinename': 'winxp', 'branch': 'MAIN'}},
            {'$project': {'testcasename': 1, 'machinename': 1,
                          'buildnumber': 1, 'metrics.fps': 1, 'entrytime': 1}},
            {'$limit': 450}
        ]

    def testTimeDeltaFilterDoesNotFilterWithoutValue(self):
        modifiedFilter = dbmodel.append_timedelta_filter(self.sampleFilter,
                                               0)

        self.assertNotIn('entrytime', modifiedFilter[0]['$match'])

    def testKnownGoodTimeDeltaFilter(self):
        modifiedFilter = dbmodel.append_timedelta_filter(self.sampleFilter,
                                               1)

        nowMinusOneDay = datetime.datetime.now() - datetime.timedelta(days=1)
        self.assertEqual(modifiedFilter[0]['$match']['entrytime']['$gte'],
                         nowMinusOneDay)
						 

class TestFormatCursorToGraphJSON(unittest.TestCase):

    def test_FormatCursorToGraphJSON(self):
        cursor = GetSampleCursor()
        result = dbmodel.format_cursor_to_scatterjson(cursor, 'fps', 'min')
        expected = {
            'ExplosionBenchmark': [
                {
                    'changelist': 1,
                    'branch': 'somebranch',
                    'value': 11,
                    'key': '21',
                    'id': '101'},
                {
                    'changelist': 2,
                    'branch': 'somebranch',
                    'value': 12,
                    'key': '22',
                    'id': '102'},
                {
                    'changelist': 3,
                    'branch': 'somebranch',
                    'value': 13,
                    'key': '23',
                    'id': '103'}
            ]
        }
        self.assertEqual(result, expected)


class TestDropBenchmark(BaseMongoTest):

    def testDrop(self):
        self.insertTestData(1)
        self.assertEqual(self.dbcount(self.benchresult), 3)
        dbmodel.drop_benchmark(D_BENCHNAME, self.db.benchresults)
        # Three insertions total, but only one of them use D_BENCHMARK
        self.assertEqual(self.dbcount(self.benchresult), 2)


class TestDbInserts(BaseMongoTest):
    """
    Test that data can be inserted into the collection and database.
    """

    def testEmptyOrNullRaises(self):
        """
        Test that empty insertions and null insertions raise errors in mongokit
        """
        with self.assertRaises(KeyError):
            dbmodel.insert_benchmark_result({}, self.benchresult)
        with self.assertRaises(AttributeError):
            dbmodel.insert_benchmark_result(None, self.benchresult)

    def testMissingKeysRaises(self):
        d = GetData()
        d.pop('metrics')
        with self.assertRaises(KeyError):
            dbmodel.insert_benchmark_result(d, self.benchresult)

    def testResultsPosted(self):
        """
        This tests that results are passed into the database
        """
        dbmodel.insert_benchmark_result(GetData(), self.benchresult)
        for row in self.benchresult.fetch():
            row = dict(row)
            del row['_id']
            del row['entrytime']
            self.maxDiff = None
            result = dict(GetData())
            del result['entrytime']
            self.assertDictEqual(result, row)

    def testInsertMultipleResults(self):
        """
        Asserts when multiple results are inserted that the correct number of
        data entries are inserted
        """
        preInsertCursorLen = self.dbcount(self.benchresult)
        times = 100
        for i in range(times):
            dbmodel.insert_benchmark_result(GetData(), self.benchresult)
        postInserCursorLen = self.dbcount(self.benchresult)
        self.assertEquals(preInsertCursorLen + times, postInserCursorLen)

    def testEntrytime(self):
        """
        This test tests the time inserted into the database is the time that we
        expect

        Note: because the jenkins host for unit testing is retardedly slow,
        this has a boundary of 20 seconds.
        """
        self.insertTestData(1)

        for result in self.benchresult.fetch():
            delta = datetime.datetime.now() - result['entrytime']
            deltaseconds = datetime.timedelta.total_seconds(delta)
            self.assertTrue(int(deltaseconds) in range(0, 20))
