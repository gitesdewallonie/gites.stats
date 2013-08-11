# -*- coding: utf-8 -*-
"""
gdw.stats

Licensed under the GPL license, see LICENCE.txt for more details.
Copyright by Affinitic sprl
"""
from datetime import datetime
from sqlalchemy.sql import tuple_
from dateutil.rrule import rrule, DAILY


def nbrOfDaysInRange(startDate, endDate):
    assert startDate < endDate
    return (endDate - startDate).days + 1


def daysInRange(startDate, endDate):
    return set(rrule(DAILY, dtstart=startDate,
                     until=endDate, cache=True))


def overlaps(a_pair, b_pair):
    return tuple_(*a_pair).op('OVERLAPS')(tuple_(*b_pair))


from zope.configuration import xmlconfig


def parseZCML(package, filename='configure.zcml'):
    context = xmlconfig._getContext()
    xmlconfig.include(context, filename, package)
    context.execute_actions()


def morning(startDate):
    return datetime(startDate.year, startDate.month, startDate.day, 0, 0, 0)


def evening(endDate):
    return datetime(endDate.year, endDate.month, endDate.day, 23, 59, 59)
