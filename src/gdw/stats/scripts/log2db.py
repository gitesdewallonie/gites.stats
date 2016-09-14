# -*- coding: utf-8 -*-
"""
gdw.stats

Licensed under the GPL license, see LICENCE.txt for more details.
Copyright by Affinitic sprl
"""
import apachelog
import os.path
import re
import time
import urlparse

from datetime import datetime
from gites.db.content import LogItem, Hebergement
from gites.db import DeclarativeBase
from gdw.stats.scripts.config import (ROBOTS, FORMAT, SKIP_TYPES,
                                      VALID_HTTP_CODE, SKIP_HOSTS,
                                      getConfig)
from gdw.stats.utils import parseZCML
from affinitic.db import IDatabase
from affinitic.db.utils import initialize_declarative_mappers, initialize_defered_mappers
from zope.component import getUtility
from plone.memoize.forever import memoize
from sqlalchemy import select, func


def getMaxDate(website):
    return select([func.max(LogItem.log_date)],
                  LogItem.log_website == website).execute().fetchone()


@memoize
def getHebPkFromId(hebId):
    hebId = hebId.replace('%20', ' ')  # handle spaces in IDs (#6473)
    heb = select([Hebergement.heb_pk],
                   Hebergement.heb_id == hebId).execute().fetchone()
    if heb is None:
        heb = select([Hebergement.heb_pk],
                     Hebergement.heb_id.like('%%%s%%' % hebId)).execute().fetchall()
        if heb and len(heb) == 1:
            heb = heb[0]
        else:
            return None
    return heb.heb_pk


def main():
    import gdw.stats.scripts
    parseZCML(gdw.stats.scripts, 'scripts.zcml')
    db = getUtility(IDatabase, 'postgres')
    session = db.session
    initialize_declarative_mappers(DeclarativeBase, db.metadata)
    initialize_defered_mappers(db.metadata)
    p = apachelog.parser(FORMAT)
    logfilePath, website = getConfig()
    maxDate = getMaxDate(website).max_1
    if maxDate is None:
        maxDate = datetime(1970, 1, 1)
    cpt = 0
    for line in open(logfilePath):
        try:
            data = p.parse(line)
        except:
            continue
        if data is None:
            continue
        date = apachelog.parse_date(data['%t'])
        date = datetime(*time.strptime(date[0], '%Y%m%d%H%M%S')[:6])
        if date <= maxDate:
            continue
        code = data['%>s']
        if int(code) not in VALID_HTTP_CODE:
            continue
        path = re.match('(.*) (.*) (.*)', data['%r']).group(2)
        path = urlparse.urlparse(path)[2]
        # path : '/hebergement/logement/beauraing/hebid'
        if len(path.strip('/').split('/')) != 4:
            continue
        if path.lstrip('/').split('/')[0] != 'hebergement':
            continue
        if path.endswith('/view'):
            continue
        if path.endswith('/gallery'):
            continue
        hebid = path.rstrip('/').split('/')[-1]
        if os.path.splitext(hebid)[1] in SKIP_TYPES:
            continue
        if hebid.lower() in ['robots.txt',
                             '/misc_/ExternalEditor/edit_icon']:
            continue
        if 'manage_' in hebid.lower():
            continue
        if '/p_/' in path.lower():
            continue
        if '/misc_/' in path.lower():
            continue
        agent = data['%{User-Agent}i']
        stop = False
        agent_lower = agent.lower()
        for robot in ROBOTS:
            if robot in agent_lower:
                stop = True
                break
        if stop:
            continue
        host = data['%h']
        if host in SKIP_HOSTS:
            continue
        cpt += 1
        if cpt % 10000 == 0:
            session.flush()
            session.commit()
            print cpt
        heb_pk = getHebPkFromId(hebid)
        logline = LogItem()
        logline.log_date = date
        logline.log_path = path
        logline.log_hebid = hebid
        logline.log_hebpk = heb_pk
        logline.log_host = host
        logline.log_agent = agent
        logline.log_website = website
        session.add(logline)
        maxDate = date
    session.flush()
    session.commit()

if __name__ == '__main__':
    main()
