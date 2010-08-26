# -*- coding: utf-8 -*-
"""
gdw.stats

Licensed under the GPL license, see LICENCE.txt for more details.
Copyright by Affinitic sprl
"""
from sqlalchemy.ext.compiler import compiles
from sqlalchemy.sql import ClauseElement
from sqlalchemy.sql.expression import _literal_as_binds, _CompareMixin
from sqlalchemy.types import NullType
from dateutil.rrule import rrule, DAILY


def nbrOfDaysInRange(startDate, endDate):
    assert startDate < endDate
    return (endDate - startDate).days + 1


def daysInRange(startDate, endDate):
    return set(rrule(DAILY, dtstart=startDate,
                     until=endDate, cache=True))


class TupleClause(ClauseElement, _CompareMixin):

    def __init__(self, *columns):
        self.columns = [_literal_as_binds(col) for col in columns]
        self.type = NullType()


@compiles(TupleClause)
def compile_tupleclause(element, compiler, **kw):
    return "(%s)" % ", ".join(compiler.process(col) for col in
element.columns)


def overlaps(a_pair, b_pair):
    return TupleClause(*a_pair).op('OVERLAPS')(TupleClause(*b_pair))


from zope.configuration import xmlconfig


def parseZCML(package, filename='configure.zcml'):
    context = xmlconfig._getContext()
    xmlconfig.include(context, filename, package)
    context.execute_actions()
