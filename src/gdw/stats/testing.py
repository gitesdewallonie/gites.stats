# -*- coding: utf-8 -*-
"""
gdw.stats

Licensed under the GPL license, see LICENCE.txt for more details.
Copyright by Affinitic sprl
"""
import os
import re
from sqlalchemy.orm import clear_mappers
from zope.component import getUtilitiesFor
from zope.app.testing.functional import ZCMLLayer as _ZCMLLayer
from affinitic.db.pg import PGDB
from affinitic.db.interfaces import IDatabase
from sqlalchemy.engine import default
from sqlalchemy import orm


class LocalHebergement(object):
    """
    A fake hebergement
    """

    def __init__(self, heb_pk):
        self.heb_pk = heb_pk


class GitesSQLiteDB(PGDB):
    db = 'gites_wallons_test'
    persistentSession = True
    #verbose = True

    @property
    def url(self):
        return 'postgresql://test:test@localhost:5432/gites_wallons_test'


class ZCMLLayer(_ZCMLLayer):

    def __init__(self, *args, **kwargs):
        kwargs['allow_teardown'] = True
        _ZCMLLayer.__init__(self, *args, **kwargs)

    def setUp(self):
        _ZCMLLayer.setUp(self)
        for name, utility in getUtilitiesFor(IDatabase):
            utility.setMappers()

    def tearDown(self):
        _ZCMLLayer.tearDown(self)
        clear_mappers()

testingZCMLPath = os.path.join(os.path.dirname(__file__), 'testing.zcml')
dbLayer = ZCMLLayer(testingZCMLPath,
                    'gdw.stats',
                    'StatsGDW')


def eq_(a, b, msg=None):
    """Assert a == b, with repr messaging on failure."""
    assert a == b, msg or "%r != %r" % (a, b)


class AssertsCompiledSQL(object):

    def assert_compile(self, clause, result, params=None, checkparams=None, dialect=None, use_default_dialect=False):
        if use_default_dialect:
            dialect = default.DefaultDialect()

        if dialect is None:
            dialect = getattr(self, '__dialect__', None)

        kw = {}
        if params is not None:
            kw['column_keys'] = params.keys()
        if isinstance(clause, orm.Query):
            context = clause._compile_context()
            context.statement.use_labels = True
            clause = context.statement

        c = clause.compile(dialect=dialect, **kw)
        cc = re.sub(r'[\n\t]', '', str(c))

        eq_(cc, result, "%r != %r on dialect %r" % (cc, result, dialect))

        if checkparams is not None:
            eq_(c.construct_params(params), checkparams)
