# -*- coding: utf-8 -*-
"""
gdw.stats

Licensed under the GPL license, see LICENCE.txt for more details.
Copyright by Affinitic sprl
"""
import getopt
import sys
import time
from datetime import datetime
from zope.component import getUtility
from affinitic.db import IDatabase
from gites.db.content import Hebergement
from gdw.stats.occupation import HebergementsOccupation


def usage():
    print """
    Usage: gdwstats [-h | -s (STARTDATE) | -e (ENDDATE)]

    Options:

        -h / --help
            Print thiѕ help message

        -e endDate / --end=endDate
            End Date with format YYYY-MM-DD

        -s startDate / --start=startDate
            Start Date with format YYYY-MM-DD

"""


def getCommandLineConfig(usage):
    try:
        opts, args = getopt.getopt(sys.argv[1:], "hs:e:",
            ["help", "start=", "end="])
    except getopt.GetoptError, err:
        print str(err)
        usage()
        sys.exit(2)
    options = {}
    if len(opts) == 0:
        usage()
        sys.exit(2)
    for o, value in opts:
        if o in ("-h", "--help"):
            usage()
            sys.exit()
        elif o in ("-e", "--end"):
            options['end'] = datetime(*time.strptime(value, "%Y-%m-%d")[:6])
        elif o in ("-s", "--start"):
            options['start'] = datetime(*time.strptime(value, "%Y-%m-%d")[:6])
        else:
            assert False, "unhandled option"
    return options


def cmdline():
    options = getCommandLineConfig(usage)
    db = getUtility(IDatabase, name='postgres')
    session = db.session
    query = session.query(Hebergement)
    query = query.filter(Hebergement.heb_calendrier_proprio != 'non actif')
    hebs = query.all()
    session.close()
    hebsOccupation = HebergementsOccupation(hebs, options.get('start'), options.get('end'))
    print hebsOccupation.taux


def main():
    from gdw.stats.utils import parseZCML
    import gdw.stats
    parseZCML(gdw.stats)
    cmdline()

if __name__ == '__main__':
    main()
