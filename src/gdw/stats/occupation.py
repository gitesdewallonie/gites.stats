# -*- coding: utf-8 -*-
"""
gites.stats

Licensed under the GPL license, see LICENCE.txt for more details.
Copyright by Affinitic sprl
"""
from __future__ import division
from zope.component import getUtility
from affinitic.db import IDatabase
from gites.db.content import (ReservationProprio,
                              Hebergement)
from gdw.stats.utils import nbrOfDaysInRange
from gdw.stats.inactive import HebergementInactiveCalculation


class HebergementOccupation(object):

    def __init__(self, hebergement, startDate, endDate, maxInactifDays=1):
        assert startDate < endDate
        self.hebergement = hebergement
        self.startDate = startDate
        self.endDate = endDate
        self.maxInactifDays = maxInactifDays

    def nombreJoursOccupes(self):
        db = getUtility(IDatabase, name='postgres')
        session = db.session
        query = session.query(ReservationProprio).join('hebergement')
        query = query.filter(Hebergement.heb_pk == self.hebergement.heb_pk)
        query = query.filter(ReservationProprio.res_date <= self.endDate)
        query = query.filter(ReservationProprio.res_date >= self.startDate)
        query = query.filter(ReservationProprio.res_type == u'loue')
        count = query.count()
        session.close()
        return count

    @property
    def taux(self):
        return self.nombreJoursOccupes() / nbrOfDaysInRange(self.startDate, self.endDate)

    def hasBeenActive(self):
        db = getUtility(IDatabase, name='postgres')
        session = db.session
        query = session.query(ReservationProprio).join('hebergement')
        query = query.filter(Hebergement.heb_pk == self.hebergement.heb_pk)
        count = query.count()
        session.close()
        return (count > 0)

    def isActif(self):
        if not self.hasBeenActive():
            return False
        inactiveCalc = HebergementInactiveCalculation(self.hebergement.heb_pk, self.startDate, self.endDate)
        return len(inactiveCalc.inactiveDaysOverRange) < self.maxInactifDays

    def isInactif(self):
        return not self.isActif()


class HebergementsOccupation(object):

    def __init__(self, hebergements, startDate, endDate, maxInactifDays=1):
        assert startDate < endDate
        self.hebergements = hebergements
        self.startDate = startDate
        self.endDate = endDate
        self.maxInactifDays = maxInactifDays

    @property
    def hebergementCount(self):
        return self.hebergements.count()

    @property
    def hebergementsActif(self):
        for heb in self.hebergements:
            hebOccupation = HebergementOccupation(heb, self.startDate, self.endDate, self.maxInactifDays)
            if hebOccupation.isActif():
                yield hebOccupation

    @property
    def hebergementsActifCount(self):
        return len([heb for heb in self.hebergementsActif])

    @property
    def hebergementsInactifCount(self):
        return self.hebergementCount - len([heb for heb in self.hebergementsActif])

    @property
    def taux(self):
        taux = 0.0
        hebCount = 0
        for hebOccupation in self.hebergementsActif:
            taux += hebOccupation.taux
            hebCount += 1
        if hebCount == 0:
            return 0.0
        return taux / hebCount

    @property
    def nombreJoursOccupes(self):
        nbrJourOccupe = 0
        for hebOccupation in self.hebergementsActif:
            nbrJourOccupe += hebOccupation.nombreJoursOccupes()
        return nbrJourOccupe
