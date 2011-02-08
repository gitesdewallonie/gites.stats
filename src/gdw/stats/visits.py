# -*- coding: utf-8 -*-
"""
gdw.stats

Licensed under the GPL license, see LICENCE.txt for more details.
Copyright by Affinitic sprl
"""
from sqlalchemy import func, select, and_
from gites.db.content import LogItem
from gdw.stats.utils import morning, evening


class VisitDayStat(object):

    visitCount = 0
    uniqueVisitCount = 0
    statDate = None

    def __init__(self, statDate, visitCount, uniqueVisitCount):
        self.statDate = statDate
        self.visitCount = visitCount
        self.uniqueVisitCount = uniqueVisitCount

    def date(self):
        return self.statDate.strftime('%d-%m-%Y')


class StatContainer(object):
    hebPk = None
    minDate = None
    maxDate = None
    group = 'day'

    def __init__(self, hebPk, minDate, maxDate, group='day'):
        self.hebPk = hebPk
        self.minDate = morning(minDate)
        self.maxDate = evening(maxDate)
        self.group = group

    @property
    def query(self):
        q = select([func.date_trunc(self.group, LogItem.log_date).label('day'),
                    func.count().label('visitCount'),
                    func.count(LogItem.log_host.distinct()).label('uniqueVisitCount')],
                   and_(LogItem.log_hebpk == self.hebPk,
                        LogItem.log_date.between(self.minDate,
                                                 self.maxDate)))
        q = q.group_by(func.date_trunc(self.group, LogItem.log_date))
        q = q.order_by(func.date_trunc(self.group, LogItem.log_date))
        return q

    def __iter__(self):
        self.totals()
        for item in self.query.execute():
            visitDay = VisitDayStat(item.day, item.visitCount, item.uniqueVisitCount)
            yield visitDay

    def average(self):
        subQuery = self.query.alias('visits')
        q = select([func.avg(subQuery.c.visitCount).label('averageVisitCount'),
                    func.avg(subQuery.c.uniqueVisitCount).label('averageUniqueVisitCount')],
                   from_obj=subQuery)
        return q.execute().first()

    def totals(self):
        subQuery = self.query.alias('visits')
        q = select([func.sum(subQuery.c.visitCount).label('totalVisitCount'),
                    func.sum(subQuery.c.uniqueVisitCount).label('totalUniqueVisitCount')],
                   from_obj=subQuery)
        return q.execute().first()
