#!/usr/bin/env python
# -*- coding:utf-8 -*-

# check_c2c - nagios check for C2C trains
#
# (c) James Powell / jamespo [at] gmail /  2014
#
# Scrapes http://m.journeycheck.com/c2c/getDepartureBoards?fHome=false&from=STATION1&to=STATION2&savedRoute=&incidentsType=DEPARTURE_BOARD

# Possible errors: "There are no direct services to Upminster departing from Limehouse
# within the next hour.

import urllib2
from optparse import OptionParser
from bs4 import BeautifulSoup
import os

class c2c_util(object):
    @staticmethod
    def nag_code_to_status(code, msg):
        '''return display nagios status for code with msg appended'''
        code2stat = { 0 : 'OK',
                      1 : 'WARNING',
                      2 : 'CRITICAL',
                      3 : 'UNKNOWN'
                      }
        return '%s: %s' % (code2stat[code], msg)

    @staticmethod
    def parse_page(statushtml):
        departures = []
        soup = BeautifulSoup(statushtml)
        all_ul = soup.find_all('ul')
        for ul in all_ul:
            if ul.get('class') == [u'boards', u'rowAlternator1', u'clr'] or \
                ul.get('class') == [u'boards', u'rowAlternator2', u'clr']:
                if os.getenv('DEBUG'):
                    print ul.contents
                for span in ul.find_all('span'):
                    # get the time
                    if span['class'] == [u'boardsTimeVal']:
                        time = str(span.contents[0])
                # get if ontime
                is_ontime = str(ul.find_all('small')[1].string.lstrip())
                departures.append((time, is_ontime))
                #print departures # DEBUG
        return departures

    @staticmethod
    def find_delays(statushtml, min_trains):
        if 'There are no direct services' in statushtml:
            return (1, 'No trains found')
        # TODO: other non-results checks
        else:
            departures = c2c_util.parse_page(statushtml)
            num_trains = len(departures)
            num_ontime = len([train[1] for train in departures if train[1] == 'On Time'])
            if num_trains < min_trains:
                return (2, 'Only %s trains found (%s required)' % (num_trains, min_trains))
            elif num_trains == num_ontime:
                return (0, 'No delays (%s trains found)' % num_trains)
            else:
                return (2, '%s/%s trains delayed' % (num_trains - num_ontime, num_trains))

    @staticmethod
    def dl_status_page(from_stn, to_stn, min_trains):
        '''download tfl xml, parse and output status'''
        feedurl = 'http://m.journeycheck.com/c2c/getDepartureBoards?fHome=false&from=%s&to=%s&savedRoute=&incidentsType=DEPARTURE_BOARD' % (from_stn, to_stn)
        try:
            livefeed = urllib2.urlopen(feedurl)
            statushtml = livefeed.read()
            #print statushtml # DEBUG
            (status, statstr) = c2c_util.find_delays(statushtml, min_trains)
        #else:
        #        (status, statstr) = (0, 'All Lines OK')
        except urllib2.URLError:
            (status, statstr) = (3, 'Could not access %s' % feedurl)
        return (status, c2c_util.nag_code_to_status(status, statstr))

    @staticmethod
    def get_cli_options():
        parser = OptionParser()
        parser.add_option("-f", "--from", help="Departure Station Code (from)",
                          dest="from_stn", default = None)
        parser.add_option("-t", "--to", help="Destination Station Code (to)",
                          dest="to_stn", default = None)
        parser.add_option("-m", "--mintrains", help="Minimum # of trains",
                          dest="min_trains", default = "3")
        (options, args) = parser.parse_args()
        if options.from_stn is None or options.to_stn is None:
            return (None, None)
        else:
            return (options.from_stn, options.to_stn, int(options.min_trains))


class c2cfeed(object):
    def __init__(self, html):
        '''scrape html and store results in self'''
        return None

    def getanyproblems(self):
        '''return array of problems'''
        problems = []
        # TODO: get problems
        return problines

# start of main program
def main():
    (from_stn, to_stn, min_trains) = c2c_util.get_cli_options()
    (status, statstr) = c2c_util.dl_status_page(from_stn, to_stn, min_trains)
    print statstr
    exit(status)

if __name__ == "__main__":
    main()
