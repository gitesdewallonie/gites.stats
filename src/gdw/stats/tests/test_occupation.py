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
from gites.db.content import ReservationProprio, Hebergement
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
        when(HebergementOccupation).nombreJoursOccupe().thenReturn(10).thenReturn(0)
        self.assertEqual(occupation.taux, 0.5)

    def testBasic(self):
        minDate = datetime(2010, 10, 1)
        maxDate = datetime(2010, 10, 10)
        hebergement1 = LocalHebergement(1)
        hebergement2 = LocalHebergement(2)
        occupation = HebergementsOccupation([hebergement1, hebergement2],
                                           minDate, maxDate)
        when(HebergementOccupation).nombreJoursOccupe().thenReturn(1)
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
        when(HebergementOccupation).nombreJoursOccupe().thenReturn(0)
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
        when(occupation).nombreJoursOccupe().thenReturn(1)
        self.assertEqual(occupation.taux, 0.1)


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
            func(self)
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
        self.assertEqual(occupation.nombreJoursOccupe(), 2)

    @withDBSetup1
    def testIsActifIfEmpty(self):
        minDate = datetime(2010, 10, 1)
        maxDate = datetime(2010, 10, 11)
        hebergement = LocalHebergement(1)
        occupation = HebergementOccupation(hebergement, minDate, maxDate)
        self.assertEqual(occupation.isActif(), True)
