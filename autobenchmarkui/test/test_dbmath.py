import unittest

from ..dbmath import mean, median, standard_deviation


class TestMapReduceAverages(unittest.TestCase):
    def setUp(self):
        self.testIntergerData = [1, 2, 3, 4, 5]
        self.testFloatData = [1.1, 2.2, 3.3, 4.4, 5.5]

    def testKnownGoodMeanWithIntergers(self):
        self.assertEqual(mean(self.testIntergerData), 3)

    def testKnownGoodMeanWithFloats(self):
        self.assertEqual(mean(self.testFloatData), 3.3)

    def testKnownGoodMedianWithIntegers(self):
        self.assertEqual(median(self.testIntergerData), 3)

    def testKnownGoodMedianWithFloats(self):
        self.assertEqual(median(self.testFloatData), 3.3)

    def testKnownGoodStandardDeviationWithInts(self):
        self.assertEqual(standard_deviation(self.testIntergerData), 2)

    def testKnownGoodStandardDeviationWithFloats(self):
        self.assertEqual(standard_deviation(self.testFloatData), 2.42)