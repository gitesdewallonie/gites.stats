# -*- coding: utf-8 -*-
"""
gdw.stats

Licensed under the GPL license, see LICENCE.txt for more details.
Copyright by Affinitic sprl
"""
from plone.app.testing import PloneSandboxLayer
from plone.app.testing import PLONE_FIXTURE
from plone.app.testing import PLONE_FUNCTIONAL_TESTING
from plone.app.testing import FunctionalTesting
from zope.configuration import xmlconfig
from z3c.sqlalchemy import createSAWrapper


class StatFixture(PloneSandboxLayer):
    defaultBases = (PLONE_FIXTURE,)

    def setUpZope(self, app, configurationContext):
        import gdw.stats
        xmlconfig.file('ftesting.zcml', gdw.stats,
                       context=configurationContext)
        connString = 'postgresql://test:test@localhost:5432/gites_wallons_test'
        createSAWrapper(connString,
                        forZope=True,
                        #echo=True,
                        name='gites_wallons',
                        model='GitesMappings')


STAT_FIXTURE = StatFixture()
STAT_FUNCTIONAL_TESTING = FunctionalTesting(
        bases=(PLONE_FUNCTIONAL_TESTING, STAT_FIXTURE,),
        name="Stat:Functional")
