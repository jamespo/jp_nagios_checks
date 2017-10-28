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
import socket
import sys
import pprint
import time
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


def get_page(ic_url, user, pw, hostname):
    '''reads icinga all status page and returns in json'''
    json_all_hosts_services = 'cgi-bin/status.cgi?host=%s&style=detail&jsonoutput' % hostname
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


def checktime(last_checktime):
    '''strip date from last check time if it's today'''
    # if check is not made yet will return N/A
    if ' ' not in last_checktime:
        return last_checktime
    # assumes date in MM-DD-YYYY
    (checkdate, checktime) = last_checktime.split(' ')
    if time.strftime("%m-%d-%Y") == checkdate:
        return checktime
    else:
        return last_checktime


def parse_checks(icinga_status, options):
    '''output from the passed datastructure'''
    rc, summ = parse_checks_individual(icinga_status, options)
    parse_checks_summary(summ, options)
    return rc


def parse_checks_individual(icinga_status, options):
    '''print results of individual checks'''
    rc = 0
    summ = defaultdict(lambda: 0)
    # print individual check status
    for svc in icinga_status['status']['service_status']:
        status = svc['status']
        summ[status] += 1
        if status != 'OK' or options.showall is True:
            if status != 'OK': rc = 1
            if options.colour: status = colmap[status] + status + colmap['NORM']
            if not options.quiet:
                rstr = "[%s]: %s - %s (%s)" % (status, svc['host_display_name'],
                                               svc['service_description'], svc['status_information'])
                if options.showtime:
                    rstr += " - %s" % checktime(svc['last_check'])
                print rstr
    return rc, summ


def parse_checks_summary(summ, options):
    '''print summary'''
    if not options.quiet:
        summary = ''
        # TODO: colourize if selected
        if not options.shortsumm:
            summary += 'SUMMARY:  '
        for stat in ['OK', 'WARNING', 'CRITICAL', 'UNKNOWN', 'PENDING']:
            prettystat = stat
            if options.colour:
                prettystat = colmap[stat] + str(prettystat) + colmap['NORM']
            if options.shortsumm:
                # color not supported yet
                summary += '%s:%s ' % (stat[0:2], summ[stat])
            else:
                summary += '%s: %s   ' % (prettystat, summ[stat])
        summary = summary.rstrip()
        sys.stdout.write(summary)
        if not options.shortsumm:
            print


def readconf():
    '''read config file'''
    config = ConfigParser.ConfigParser()
    config.read(['/etc/qicinga', os.path.expanduser('~/.config/.qicinga')])
    return (config.get('Main', 'icinga_url'), config.get('Main', 'username'),
            config.get('Main', 'password'),
            config.getboolean('Main', 'colour') if config.has_option('Main', 'colour') else False)


def get_options(colour):
    '''return CLI options'''
    parser = OptionParser()
    parser.add_option("-a", "--all", help="show all statuses",
                      action="store_true", dest="showall", default=False)
    parser.add_option("-s", help="short summary",
                      action="store_true", dest="shortsumm", default=False)
    parser.add_option("-t", help="show time of last check",
                      action="store_true", dest="showtime", default=False)
    parser.add_option("-c", help="colour output",
                      action="store_true", dest="colour", default=colour)
    parser.add_option("-b", help="no colour output",
                      action="store_false", dest="colour")
    parser.add_option("-q", help="quiet - no output, no summary, just return code",
                      action="store_true", dest="quiet", default=False)
    parser.add_option("-x", help="hostname - AUTOSHORT / AUTOLONG",
                      dest="hostname", default="all")
    (options, args) = parser.parse_args()
    if options.hostname == 'AUTOSHORT':
        options.hostname = socket.gethostname()
    elif options.hostname == 'AUTOLONG':
        options.hostname = socket.getfqdn()
    return options


def main():
    logger.setLevel(logging.INFO)
    (icinga_url, username, password, colour) = readconf()
    options = get_options(colour)
    data = get_page(icinga_url, username, password, options.hostname)
    icinga_status = read_json(data)
    logger.debug(pprint.pformat(icinga_status))
    rc = parse_checks(icinga_status, options)
    sys.exit(rc)


if __name__ == '__main__':
    main()
