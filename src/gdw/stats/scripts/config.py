# -*- coding: utf-8 -*-
"""
gdw.stats

Licensed under the GPL license, see LICENCE.txt for more details.
Copyright by Affinitic sprl
"""
import getopt
import sys

FORMAT = r'%h %l %u %t \"%r\" %>s %b \"%{Referer}i\" \"%{User-Agent}i\"'
SKIP_HOSTS = []
VALID_HTTP_CODE = [200, 304]
SKIP_TYPES = ['.css', '.js', '.class', '.gif', '.jpg', '.jpeg', '.png', '.bmp',
              '.ico', '.swf', '.kss', '.xsl']
ROBOTS = [
'appie',
'architext',
'jeeves',
'bjaaland',
'ferret',
'googlebot',
'gulliver',
'harvest',
'htdig',
'linkwalker',
'lycos_',
'moget',
'muscatferret',
'myweb',
'nomad',
'scooter',
'slurp',
'voyager/',
'weblayers',
# Common robots (Not in robot file)
'antibot',
'digout4u',
'echo',
'fast-webcrawler',
'ia_archiver-web.archive.org', # Must be before ia_archiver to avoid confusion with alexa
'ia_archiver',
'jennybot',
'mercator',
'netcraft',
'msnbot',
'petersnews',
'unlost_web_crawler',
'voila',
'webbase',
'zyborg',   # Must be before wisenut
'wisenutbot']


def getConfig():
    try:
        opts, args = getopt.getopt(sys.argv[1:], "hf:", ["help",
                                                         "file="])
    except getopt.GetoptError, err:
        print str(err)
        usage()
        sys.exit(2)
    filepath = None
    for o, value in opts:
        if o in ("-h", "--help"):
            usage()
            sys.exit()
        elif o in ("-f", "--file"):
            filepath = value
        else:
            assert False, "unhandled option"
    if filepath is None:
        raise getopt.GetoptError('missing file option')
    return filepath


def usage():
    print """
    Usage: script [-h | -f (FILE)]

    Options:

        -h / --help
            Print thiѕ help message

        -f FILE / --file=FILE
            logfile to parse
"""
