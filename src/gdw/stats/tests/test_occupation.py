# -*- coding: utf-8 -*-
"""
gdw.stats

Licensed under the GPL license, see LICENCE.txt for more details.
Copyright by Affinitic sprl
"""
from datetime import datetime
from unittest import TestCase
from mockito import when
from zope.component import getUtility
from affinitic.db import IDatabase
from gites.db.content import ReservationProprio, Hebergement, BlockingHistory
from gdw.stats.occupation import HebergementOccupation, HebergementsOccupation
from gdw.stats.testing import dbLayer, LocalHebergement


class TestHebergementsOccupationWithoutDB(TestCase):

    def testSpecifyDate(self):
        minDate = datetime(2010, 10, 1)
        maxDate = datetime(2010, 10, 10)
        hebergement1 = LocalHebergement(1)
        hebergement2 = LocalHebergement(2)
        occupation = HebergementsOccupation([hebergement1, hebergement2],
                                           minDate, maxDate)
        when(HebergementOccupation).isActif().thenReturn(True)
        when(HebergementOccupation).nombreJoursOccupes().thenReturn(10).thenReturn(0)
        self.assertEqual(occupation.taux, 0.5)

    def testBasic(self):
        minDate = datetime(2010, 10, 1)
        maxDate = datetime(2010, 10, 10)
        hebergement1 = LocalHebergement(1)
        hebergement2 = LocalHebergement(2)
        occupation = HebergementsOccupation([hebergement1, hebergement2],
                                           minDate, maxDate)
        when(HebergementOccupation).nombreJoursOccupes().thenReturn(1)
        when(HebergementOccupation).isActif().thenReturn(True)
        self.assertEqual(occupation.taux, 0.1)

    def testNoOccupationDays(self):
        minDate = datetime(2010, 10, 1)
        maxDate = datetime(2010, 10, 10)
        hebergement1 = LocalHebergement(1)
        hebergement2 = LocalHebergement(2)
        occupation = HebergementsOccupation([hebergement1, hebergement2],
                                           minDate, maxDate)
        when(HebergementOccupation).isActif().thenReturn(True)
        when(HebergementOccupation).nombreJoursOccupes().thenReturn(0)
        self.assertEqual(occupation.taux, 0)


class TestHebergementOccupationWithoutDB(TestCase):

    def testWrongDates(self):
        minDate = datetime(2010, 10, 11)
        maxDate = datetime(2010, 10, 1)
        hebergement = LocalHebergement(1)

        def createOccupation():
            HebergementOccupation(hebergement, minDate, maxDate)
        self.assertRaises(AssertionError, createOccupation)

    def testIsActif(self):
        minDate = datetime(2010, 10, 1)
        maxDate = datetime(2010, 10, 10)
        hebergement = LocalHebergement(1)
        occupation = HebergementOccupation(hebergement, minDate, maxDate)
        when(occupation).isActif().thenReturn(True)
        self.assertEqual(occupation.isActif(), True)
        self.assertEqual(occupation.isInactif(), False)

    def testBasicTaux(self):
        minDate = datetime(2010, 10, 1)
        maxDate = datetime(2010, 10, 10)
        hebergement = LocalHebergement(1)
        occupation = HebergementOccupation(hebergement, minDate, maxDate)
        when(occupation).nombreJoursOccupes().thenReturn(1)
        self.assertEqual(occupation.taux, 0.1)


def withDBSetup2(func):

    def decorator(f):

        def decorated(self):
            db = getUtility(IDatabase, name='postgres')
            session = db.session
            heb = Hebergement()
            heb.heb_pk = 1
            session.add(heb)
            session.flush()
            resPro = ReservationProprio()
            resPro.heb_fk = 1
            resPro.res_date = datetime(2010, 10, 1)
            resPro.res_type = 'loue'
            session.add(resPro)
            resPro = ReservationProprio()
            resPro.heb_fk = 1
            resPro.res_date = datetime(2010, 10, 5)
            resPro.res_type = 'loue'
            session.add(resPro)
            resPro = ReservationProprio()
            resPro.heb_fk = 1
            resPro.res_date = datetime(2009, 10, 1)
            resPro.res_type = 'indisp'
            session.add(resPro)
            resPro = ReservationProprio()
            resPro.heb_fk = 1
            resPro.res_date = datetime(2009, 10, 4)
            resPro.res_type = 'loue'
            session.add(resPro)
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


def withDBSetup1(func):

    def decorator(f):

        def decorated(self):
            db = getUtility(IDatabase, name='postgres')
            session = db.session
            heb = Hebergement()
            heb.heb_pk = 1
            session.add(heb)
            session.flush()
            resPro = ReservationProprio()
            resPro.heb_fk = 1
            resPro.res_date = datetime(2010, 10, 1)
            resPro.res_type = 'loue'
            session.add(resPro)
            resPro = ReservationProprio()
            resPro.heb_fk = 1
            resPro.res_date = datetime(2010, 10, 5)
            resPro.res_type = 'loue'
            session.add(resPro)
            resPro = ReservationProprio()
            resPro.heb_fk = 1
            resPro.res_date = datetime(2009, 10, 1)
            resPro.res_type = 'indisp'
            session.add(resPro)
            resPro = ReservationProprio()
            resPro.heb_fk = 1
            resPro.res_date = datetime(2009, 10, 4)
            resPro.res_type = 'loue'
            session.add(resPro)
            session.flush()
            session.commit()
            try:
                func(self)
            finally:
                db.refresh()
        return decorated(f)
    return decorator


class TestHebergementOccupationWithDB(TestCase):
    layer = dbLayer

    @withDBSetup1
    def testBasicTaux(self):
        minDate = datetime(2010, 10, 1)
        maxDate = datetime(2010, 10, 10)
        hebergement = LocalHebergement(1)
        occupation = HebergementOccupation(hebergement, minDate, maxDate)
        self.assertEqual(occupation.taux, 0.2)
        self.assertEqual(occupation.nombreJoursOccupes(), 2)

    @withDBSetup1
    def testIsActifIfEmpty(self):
        minDate = datetime(2010, 10, 1)
        maxDate = datetime(2010, 10, 11)
        hebergement = LocalHebergement(1)
        occupation = HebergementOccupation(hebergement, minDate, maxDate)
        self.assertEqual(occupation.isActif(), True)

    @withDBSetup2
    def testWithBlockingStatus(self):
        minDate = datetime(2010, 10, 1)
        maxDate = datetime(2010, 10, 11)
        hebergement = LocalHebergement(1)
        occupation = HebergementOccupation(hebergement, minDate, maxDate)
        self.assertEqual(occupation.isActif(), False)
        occupation = HebergementOccupation(hebergement, minDate, maxDate, maxInactifDays=4)
        self.assertEqual(occupation.isActif(), True)
        minDate = datetime(2010, 9, 30)
        maxDate = datetime(2010, 10, 11)
        occupation = HebergementOccupation(hebergement, minDate, maxDate, maxInactifDays=4)
        self.assertEqual(occupation.isActif(), False)
        self.assertEqual(occupation.isInactif(), True)


def withDBSetup3(func):

    def decorator(f):

        def decorated(self):
            db = getUtility(IDatabase, name='postgres')
            session = db.session
            heb = Hebergement()
            heb.heb_pk = 1
            session.add(heb)
            heb = Hebergement()
            heb.heb_pk = 2
            session.add(heb)
            session.flush()
            resPro = ReservationProprio()
            resPro.heb_fk = 1
            resPro.res_date = datetime(2010, 10, 1)
            resPro.res_type = 'loue'
            session.add(resPro)
            resPro = ReservationProprio()
            resPro.heb_fk = 1
            resPro.res_date = datetime(2010, 10, 5)
            resPro.res_type = 'loue'
            session.add(resPro)
            resPro = ReservationProprio()
            resPro.heb_fk = 2
            resPro.res_date = datetime(2010, 10, 5)
            resPro.res_type = 'loue'
            session.add(resPro)
            resPro = ReservationProprio()
            resPro.heb_fk = 1
            resPro.res_date = datetime(2009, 10, 1)
            resPro.res_type = 'indisp'
            session.add(resPro)
            resPro = ReservationProprio()
            resPro.heb_fk = 1
            resPro.res_date = datetime(2009, 10, 4)
            resPro.res_type = 'loue'
            session.add(resPro)
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
            blck = BlockingHistory()
            blck.heb_pk = 2
            blck.block_start = datetime(2010, 10, 10)
            blck.block_end = datetime(2010, 10, 10)
            session.add(blck)
            session.flush()
            session.commit()
            try:
                func(self)
            finally:
                db.refresh()
        return decorated(f)
    return decorator


class TestHebergementsOccupationWithDB(TestCase):
    layer = dbLayer

    @withDBSetup3
    def testHebCount(self):
        minDate = datetime(2010, 10, 1)
        maxDate = datetime(2010, 10, 9)
        db = getUtility(IDatabase, name='postgres')
        session = db.session
        hebs = session.query(Hebergement)
        occupations = HebergementsOccupation(hebs, minDate, maxDate)
        self.assertEqual(occupations.hebergementCount, 2)
        actifHebs = [heb for heb in occupations.hebergementsActif]
        self.assertEqual(len(actifHebs), 1)
        self.assertEqual(actifHebs[0].hebergement.heb_pk, 2)
        self.assertEqual(occupations.hebergementsInactifCount, 1)
        self.assertEqual(occupations.hebergementsActifCount, 1)

    @withDBSetup3
    def testAllActif(self):
        minDate = datetime(2008, 10, 1)
        maxDate = datetime(2008, 10, 9)
        db = getUtility(IDatabase, name='postgres')
        session = db.session
        hebs = session.query(Hebergement).all()
        session.close()
        occupations = HebergementsOccupation(hebs, minDate, maxDate)
        self.assertEqual(occupations.hebergementCount, 2)
        actifHebs = [heb for heb in occupations.hebergementsActif]
        self.assertEqual(len(actifHebs), 2)
        self.assertEqual(occupations.hebergementsActifCount, 2)
        self.assertEqual(occupations.hebergementsInactifCount, 0)

    @withDBSetup3
    def testNoneActif(self):
        minDate = datetime(2010, 10, 1)
        maxDate = datetime(2010, 10, 11)
        db = getUtility(IDatabase, name='postgres')
        session = db.session
        hebs = session.query(Hebergement).all()
        session.close()
        occupations = HebergementsOccupation(hebs, minDate, maxDate)
        self.assertEqual(occupations.hebergementCount, 2)
        actifHebs = [heb for heb in occupations.hebergementsActif]
        self.assertEqual(len(actifHebs), 0)
        self.assertEqual(occupations.hebergementsInactifCount, 2)

    @withDBSetup3
    def testNombreJourOccupe(self):
        minDate = datetime(2010, 10, 1)
        maxDate = datetime(2010, 10, 11)
        db = getUtility(IDatabase, name='postgres')
        session = db.session
        hebs = session.query(Hebergement).all()
        session.close()
        occupations = HebergementsOccupation(hebs, minDate, maxDate, maxInactifDays=10)
        self.assertEqual(occupations.nombreJoursOccupes, 3)
