# -*- coding: utf-8 -*-
import doctest
import os
import glob
import unittest
from Globals import package_home
from plone.testing import layered
from gdw.stats.tests import GLOBALS
from gdw.stats.tests.base import STAT_FUNCTIONAL_TESTING


UNITTESTS = []

OPTIONFLAGS = (doctest.ELLIPSIS |
               doctest.REPORT_ONLY_FIRST_FAILURE |
               doctest.NORMALIZE_WHITESPACE)


def list_doctests():
    home = package_home(GLOBALS)
    return [filename for filename in
            glob.glob(os.path.sep.join([home, '*.txt']))
            if os.path.basename(filename) not in UNITTESTS]


def test_suite():
    filenames = list_doctests()
    suites = []
    for filename in filenames:
        suite = doctest.DocFileSuite(os.path.basename(filename),
                   optionflags=OPTIONFLAGS,
                   package='gdw.stats.tests')
        suites.append(layered(suite, layer=STAT_FUNCTIONAL_TESTING))
    return unittest.TestSuite(suites)
