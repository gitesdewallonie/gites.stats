# -*- coding: utf-8 -*-
"""
gdw.stats

Licensed under the GPL license, see LICENCE.txt for more details.
Copyright by Affinitic sprl
"""
from unittest import TestCase
from datetime import datetime
from sqlalchemy.dialects.postgresql import base as postgresql
from zope.component import getUtility
from affinitic.db import IDatabase
from gdw.stats.inactive import HebergementInactiveCalculation
from gdw.stats.testing import dbLayer, AssertsCompiledSQL
from gdw.stats.utils import daysInRange, nbrOfDaysInRange
from gites.db.content import BlockingHistory, Hebergement


def withDBNoOverlap(func):

    def decorator(f):

        def decorated(self):
            db = getUtility(IDatabase, name='postgres')
            session = db.session
            heb = Hebergement()
            heb.heb_pk = 1
            session.add(heb)
            session.flush()
            blck = BlockingHistory()
            blck.heb_pk = 1
            blck.block_start = datetime(2010, 1, 1)
            blck.block_end = datetime(2010, 2, 3)
            session.add(blck)
            session.flush()
            session.commit()
            try:
                func(self)
            finally:
                db.refresh()
        return decorated(f)
    return decorator


def withDBBlocked(func):

    def decorator(f):

        def decorated(self):
            db = getUtility(IDatabase, name='postgres')
            session = db.session
            heb = Hebergement()
            heb.heb_pk = 1
            session.add(heb)
            session.flush()
            blck = BlockingHistory()
            blck.heb_pk = 1
            blck.block_start = datetime(2010, 1, 1)
            session.add(blck)
            session.flush()
            session.commit()
            try:
                func(self)
            finally:
                db.refresh()
        return decorated(f)
    return decorator


def withDBSimpleOverlap(func):

    def decorator(f):

        def decorated(self):
            db = getUtility(IDatabase, name='postgres')
            session = db.session
            heb = Hebergement()
            heb.heb_pk = 1
            session.add(heb)
            session.flush()
            blck = BlockingHistory()
            blck.heb_pk = 1
            blck.block_start = datetime(2010, 1, 1)
            blck.block_end = datetime(2010, 10, 3)
            session.add(blck)
            blck = BlockingHistory()
            blck.heb_pk = 1
            blck.block_start = datetime(2010, 1, 1)
            blck.block_end = datetime(2010, 2, 3)
            session.add(blck)
            session.flush()
            session.commit()
            try:
                func(self)
            finally:
                db.refresh()
        return decorated(f)
    return decorator


class TestInactiveHebCalculation(TestCase, AssertsCompiledSQL):
    layer = dbLayer
    __dialect__ = postgresql.dialect()

    def testRangeDays(self):
        minDate = datetime(2010, 10, 1)
        maxDate = datetime(2010, 10, 11)
        inactiveCalc = HebergementInactiveCalculation(1, minDate, maxDate)
        daysRange = inactiveCalc._rangeDays
        self.assertEqual(len(daysRange), 11)

    def testLoopOverHebergement(self):
        # fixed db connection queue limit problem
        for i in range(100):
            minDate = datetime(2010, 10, 1)
            maxDate = datetime(2010, 10, 11)
            inactiveCalc = HebergementInactiveCalculation(1, minDate, maxDate)
            inactiveCalc._inactiveDaysQuery()

    def testEmptyInactiveDaysQuery(self):
        minDate = datetime(2010, 10, 1)
        maxDate = datetime(2010, 10, 11)
        inactiveCalc = HebergementInactiveCalculation(1, minDate, maxDate)
        query = inactiveCalc._inactiveDaysQuery()
        results = query.all()
        self.assertEqual(results, [])
        query.session.close()

    @withDBNoOverlap
    def testWithNoOverlap(self):
        minDate = datetime(2010, 10, 1)
        maxDate = datetime(2010, 10, 11)
        inactiveCalc = HebergementInactiveCalculation(1, minDate, maxDate)
        query = inactiveCalc._inactiveDaysQuery()
        results = query.all()
        query.session.close()
        self.assertEqual(len(results), 0)
        self.assertEqual(inactiveCalc.inactiveDaysOverRange, set())

    @withDBSimpleOverlap
    def testWithLeftOverlap(self):
        minDate = datetime(2010, 10, 1)
        maxDate = datetime(2010, 10, 11)
        inactiveCalc = HebergementInactiveCalculation(1, minDate, maxDate)
        query = inactiveCalc._inactiveDaysQuery()
        results = query.all()
        query.session.close()
        self.assertEqual(len(results), 1)
        self.assertEqual(inactiveCalc.inactiveDaysOverRange,
                         set([datetime(2010, 10, 3, 0, 0),
                              datetime(2010, 10, 2, 0, 0),
                              datetime(2010, 10, 1, 0, 0)]))

    @withDBSimpleOverlap
    def testWithOuterOverlap(self):
        minDate = datetime(2009, 1, 1)
        maxDate = datetime(2011, 1, 1)
        inactiveCalc = HebergementInactiveCalculation(1, minDate, maxDate)
        query = inactiveCalc._inactiveDaysQuery()
        results = query.all()
        query.session.close()
        self.assertEqual(len(results), 2)
        inactiveDays = inactiveCalc.inactiveDaysOverRange
        self.assertEqual(inactiveDays.difference(
                         daysInRange(datetime(2010, 1, 1),
                                     datetime(2010, 10, 3))), set())
        self.assertEqual(len(inactiveDays), nbrOfDaysInRange(datetime(2010, 1, 1),
                                                             datetime(2010, 10, 3)))

    @withDBSimpleOverlap
    def testWithRightOverlap(self):
        minDate = datetime(2010, 10, 2)
        maxDate = datetime(2010, 10, 20)
        inactiveCalc = HebergementInactiveCalculation(1, minDate, maxDate)
        query = inactiveCalc._inactiveDaysQuery()
        results = query.all()
        query.session.close()
        self.assertEqual(len(results), 1)
        self.assertEqual(inactiveCalc.inactiveDaysOverRange,
                         set([datetime(2010, 10, 3, 0, 0),
                              datetime(2010, 10, 2, 0, 0)]))

    def testInactiveDaysQuery(self):
        minDate = datetime(2010, 10, 1)
        maxDate = datetime(2010, 10, 11)
        inactiveCalc = HebergementInactiveCalculation(1, minDate, maxDate)
        query = inactiveCalc._inactiveDaysQuery()
        QUERYSTR = """SELECT blockinghistory.heb_pk AS blockinghistory_heb_pk, blockinghistory.block_start AS blockinghistory_block_start, blockinghistory.block_end AS blockinghistory_block_end FROM blockinghistory WHERE blockinghistory.heb_pk = %(heb_pk_1)s AND ((blockinghistory.block_start, blockinghistory.block_end) OVERLAPS (%(param_1)s, %(param_2)s))"""
        QUERY_PARAM = {u'heb_pk_1': 1,
                       u'param_1': datetime(2010, 10, 1, 0, 0),
                       u'param_2': datetime(2010, 10, 11, 0, 0)}
        self.assert_compile(query, QUERYSTR, checkparams=QUERY_PARAM)
        self.assertEqual(len(query.all()), 0)
