# -*- coding: utf-8 -*-
from zope.component import getUtility
from affinitic.db import IDatabase
from gites.db.content import Hebergement
from gdw.stats.cmdline import getCommandLineConfig, usage
from gdw.stats.visits import StatContainer


def cmdline():
    options = getCommandLineConfig(usage)
    db = getUtility(IDatabase, name='postgres')
    session = db.session
    query = session.query(Hebergement)
    hebs = query.order_by(Hebergement.heb_pro_fk).all()
    fileId = 'hebstat.txt'
    fd = file(fileId, 'w')
    fd.write('heb_pk|pro_pk|heb_nom|pro_nom|mois|visites_uniques|visites|\n')
    for heb in hebs:
        stat = StatContainer(heb.heb_pk, options.get('start'), options.get('end'), 'month')
        for monthVisitReport in stat:
            month = monthVisitReport.statDate.strftime('%Y-%m')
            uniqueVisits = monthVisitReport.uniqueVisitCount
            visits = monthVisitReport.visitCount
            fd.write('%s|%s|%s|%s|%s|%s|%s|\n' % (heb.heb_pk, heb.heb_pro_fk, heb.heb_nom.encode('utf-8'), heb.proprio.pro_nom1.encode('utf-8'), month, uniqueVisits, visits))
    fd.close()
    session.close()


def main():
    from gdw.stats.utils import parseZCML
    import gdw.stats
    parseZCML(gdw.stats, 'cmdline.zcml')
    cmdline()

if __name__ == '__main__':
    main()
