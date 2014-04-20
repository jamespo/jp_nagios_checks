#!/usr/bin/env python

# qicinga - quick icinga commandline status display
# (C) James Powell jamespo [at] gmail [dot] com 2013
# This software is licensed under the same terms as Python itself

import urllib2
import ConfigParser
import io
import os.path
from optparse import OptionParser
from collections import defaultdict
import logging
import sys
import pprint
try:
    import simplejson as json
except ImportError:
    import json

logging.basicConfig()
logger = logging.getLogger()

colmap = {      # shell escape codes
    'NORM'      : '\033[0m',
    'CRITICAL'  : '\033[31;1m',
    'WARNING'   : '\033[33;1m',
    'OK'        : '\033[32;1m',
    'UNKNOWN'   : '\033[35;1m',
    'PENDING'   : '\033[36;1m'
}

def get_page(ic_url, user, pw):
    '''reads icinga all status page and returns in json'''
    json_all_hosts_services = 'cgi-bin/status.cgi?host=all&style=detail&jsonoutput'
    url = ic_url + json_all_hosts_services
    logger.debug('url: ' + url)
    # authenticate
    passman = urllib2.HTTPPasswordMgrWithDefaultRealm()
    passman.add_password(None, url, user, pw)
    urllib2.install_opener(urllib2.build_opener(urllib2.HTTPBasicAuthHandler(passman)))
    req = urllib2.urlopen(url)
    data = req.read()
    return data

def read_json(icinga_json):
    '''parse json into data structure'''
    icinga_status = json.loads(icinga_json)
    return icinga_status

def parse_checks(icinga_status, options):
    '''output from the passed datastructure'''
    rc = 0
    summ = defaultdict(lambda: 0)
    for svc in icinga_status['status']['service_status']:
        status = svc['status']
        summ[status] += 1
        if status != 'OK' or options.showall is True:
            if status != 'OK': rc = 1
            if options.colour: status = colmap[status] + status + colmap['NORM']
            if not options.quiet:
                print "[%s]: %s - %s (%s)" % (status, svc['host_display_name'],
                                              svc['service_description'], svc['status_information'])
    if not options.quiet:
        # TODO: colourize if selected
        sys.stdout.write('SUMMARY:  ')
        for stat in ['OK', 'WARNING', 'CRITICAL', 'UNKNOWN', 'PENDING']:
            prettystat = stat
            if options.colour:
                prettystat = colmap[stat] + str(stat) + colmap['NORM']
            sys.stdout.write('%s: %s   ' % (prettystat, summ[stat]))
        print
    return rc

def readconf():
    config = ConfigParser.ConfigParser()
    config.read(['/etc/qicinga', os.path.expanduser('~/.config/.qicinga')])
    return (config.get('Main', 'icinga_url'), config.get('Main', 'username'),
            config.get('Main', 'password'), 
            config.getboolean('Main', 'colour') if config.has_option('Main', 'colour') else False)

def main():
    logger.setLevel(logging.INFO)
    (icinga_url, username, password, colour) = readconf()
    parser = OptionParser()
    parser.add_option("-a", "--all", help="show all statuses",
                      action="store_true", dest="showall", default=False)
    parser.add_option("-c", help="colour output",
                      action="store_true", dest="colour", default=colour)
    parser.add_option("-b", help="no colour output",
                      action="store_false", dest="colour")
    parser.add_option("-q", help="quiet - no output, no summary, just return code",
                      action="store_true", dest="quiet", default=False)
    (options, args) = parser.parse_args()
    data = get_page(icinga_url, username, password)
    icinga_status = read_json(data)
    logger.debug(pprint.pformat(icinga_status))
    rc = parse_checks(icinga_status, options)
    sys.exit(rc)

if __name__ == '__main__':
    main()
