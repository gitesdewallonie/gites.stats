# -*- coding: utf-8 -*-
"""
gdw.stats

Licensed under the GPL license, see LICENCE.txt for more details.
Copyright by Affinitic sprl
"""
from dateutil.rrule import rrule, DAILY
from zope.component import getUtility
from affinitic.db import IDatabase
from gites.db.content import BlockingHistory
from gdw.stats.utils import overlaps, daysInRange


class HebergementInactiveCalculation(object):

    def __init__(self, hebId, startDate, endDate):
        self.hebId = hebId
        self.startDate = startDate
        self.endDate = endDate

    def _inactiveDaysQuery(self):
        session = getUtility(IDatabase, name='postgres').session
        query = session.query(BlockingHistory)
        query = query.filter(BlockingHistory.heb_pk == self.hebId)
        query = query.filter(overlaps((BlockingHistory.block_start,
                                       BlockingHistory.block_end),
                                      (self.startDate, self.endDate)))
        return query

    @property
    def _rangeDays(self):
        return daysInRange(self.startDate, self.endDate)

    @property
    def inactiveDaysOverRange(self):
        inactiveDays = set()
        query = self._inactiveDaysQuery()
        for block in query.all():
            blockedDays = rrule(DAILY, dtstart=block.block_start,
                                until=block.block_end)
            intersect = self._rangeDays.intersection(blockedDays)
            inactiveDays.update(intersect)
        query.session.close()
        return inactiveDays
