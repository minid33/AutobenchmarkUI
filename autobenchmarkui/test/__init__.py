import atexit
import datetime
import os
import subprocess
import tempfile
import unittest

from .. import config, dbmodel

D_BENCHNAME = u'map'
D_MACHINE = u'winxp-highspec'
D_BUILDNO = 123456


def _isouni(dt):
    return unicode(dt.isoformat())


def GetData(machinename=D_MACHINE, benchmarkname=D_BENCHNAME, build=D_BUILDNO,
            entrytime=datetime.datetime.now):
    """Gets test data that would be posted to the DB.

    :param entrytime: If None, do not include entrytime.
      If callable, call it to get entrytime.
      Otherwise, just use it.
    """
    if callable(entrytime):
        entrytime = entrytime()
    dt = datetime.datetime
    data = {
        u'branch': u'MAIN',
        u'buildnumber': build,
        u'machinename': machinename,
        u'metrics': {
            u'fps': [
                [_isouni(dt(2012, 8, 9, 17, 27, 12, 868000)), 10.1],
                [_isouni(dt(2012, 8, 9, 17, 27, 12, 892000)), 18.7],
                [_isouni(dt(2012, 8, 9, 17, 27, 12, 913000)), 45.3],
                [_isouni(dt(2012, 8, 9, 17, 27, 12, 934000)), 54.3]],
            u'frametime': [
                [_isouni(dt(2012, 8, 9, 17, 27, 12, 686000)), 4.5],
                [_isouni(dt(2012, 8, 9, 17, 27, 12, 710000)), 7.1],
                [_isouni(dt(2012, 8, 9, 17, 27, 12, 727000)), 0.2],
                [_isouni(dt(2012, 8, 9, 17, 27, 12, 742000)), 5.7]],
            u'malloc': [
                [_isouni(dt(2012, 8, 9, 17, 27, 12, 686000)), 1910968320.0],
                [_isouni(dt(2012, 8, 9, 17, 27, 12, 710000)), 2181651899.2],
                [_isouni(dt(2012, 8, 9, 17, 27, 12, 727000)), 1521689151.2],
                [_isouni(dt(2012, 8, 9, 17, 27, 12, 742000)), 198216912.0]]},
        u"testcasename": benchmarkname,
    }
    if entrytime is not None:
        data[u'entrytime'] = entrytime

    return data


def GetSampleCursor():
    return [
        {
            "AggregateData": {
                "fps": {
                    "min": 11
                }
            },
            "branch": 'somebranch',
            "buildnumber": 1,
            "metrics": {},
            "testcasename": "ExplosionBenchmark",
            "entrytime": '21',
            "_id": 101,
        },
        {
            "AggregateData": {
                "fps": {
                    "min": 12
                }
            },
            "branch": 'somebranch',
            "buildnumber": 2,
            "metrics": {},
            "testcasename": "ExplosionBenchmark",
            "entrytime": '22',
            "_id": 102,
        },
        {
            "AggregateData": {
                "fps": {
                    "min": 13
                }
            },
            "branch": 'somebranch',
            "buildnumber": 3,
            "metrics": {},
            "testcasename": "ExplosionBenchmark",
            "entrytime": '23',
            "_id": 103,
        }]


def StartLocalMongo():
    if hasattr(StartLocalMongo, '_started'):
        return
    mongodir = tempfile.mkdtemp('mongo')
    mongod = os.path.join(
        os.path.dirname(__file__), '..', '..',
        'bin', 'win_x64', '2.4.8', 'mongod.exe')
    args = [mongod, '--dbpath',
            mongodir,
            '--port', str(config.TestingConfig.MONGO_PORT),
            '--nojournal']
    mongoproc = subprocess.Popen(args, stderr=subprocess.STDOUT)
    atexit.register(mongoproc.kill)
    StartLocalMongo._started = True


class BaseMongoTest(unittest.TestCase):

    def dbcount(self, coll):
        return len(list(coll.find()))

    def assertCollEmpty(self, coll):
        self.assertEqual(self.dbcount(coll), 0)

    def setUp(self):
        StartLocalMongo()
        self.cfg = config.TestingConfig
        (self.connection, self.db, self.benchresult) = dbmodel.create_mongo_objs_getter_from_config(self.cfg)()
        self.configcollection = self.db.configuration

        #make sure the db is clean before the test is run
        self.db.drop_collection('benchresults')
        self.db.drop_collection('configuration')
        self.assertCollEmpty(self.benchresult)
        self.assertCollEmpty(self.configcollection)

        # Add default configuration data
        self.branch = 'BRANCH'
        self.configcollection.save({'currentbranch': self.branch})

    def insertTestData(self, numTimes):
        """
        Inserts test data into the test database.

        :param numTimes: The number of times to insert the 3 rows of test
            data (3 would insert 9 rows total).
        """
        for build in range(numTimes):
            dbmodel.insert_benchmark_result(
                GetData(
                    machinename=u'spam', benchmarkname=u'eggs', build=build),
                self.benchresult)
            dbmodel.insert_benchmark_result(
                GetData(benchmarkname=u'eggs', build=build),
                self.benchresult)
            dbmodel.insert_benchmark_result(
                GetData(machinename=u'spam', build=build),
                self.benchresult)
