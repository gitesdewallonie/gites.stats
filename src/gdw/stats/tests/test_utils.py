# -*- coding: utf-8 -*-
"""
gdw.stats

Licensed under the GPL license, see LICENCE.txt for more details.
Copyright by Affinitic sprl
"""
from unittest import TestCase
from datetime import datetime
from gdw.stats.utils import nbrOfDaysInRange


class TestUtils(TestCase):

    def testNombreJours(self):
        minDate = datetime(2010, 10, 1)
        maxDate = datetime(2010, 10, 11)
        self.assertEqual(nbrOfDaysInRange(minDate, maxDate), 11)

    def testWrongDates(self):
        minDate = datetime(2010, 10, 11)
        maxDate = datetime(2010, 10, 1)
        self.assertRaises(AssertionError, nbrOfDaysInRange, minDate, maxDate)
