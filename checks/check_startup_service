#!/usr/bin/env python3

# check_startup_service ; -*-Python-*-
# a simple nagios check to verify if init scripts are running
# python 3 enhanced version of check_init_service
# Copyright James Powell 2023 / jamespo [at] gmail [dot] com
# This program is distributed under the terms of the GNU General Public License v3

import sys, re, os
from optparse import OptionParser

class CheckInitService(object):
    def __init__(self, options):
        self.services = options.services.split(',')
        self.expected_services = set()
        self.rogue_services = set()
        self.matchregex = options.matchregex
        self.svccmd = options.svccmd

    @staticmethod
    def _findservice():
        '''return full path to service command'''
        for svc in ('/bin/systemctl', '/usr/sbin/service', '/sbin/service'):
            if os.path.isfile(svc):
                return svc
        return None

    @staticmethod
    def build_cmdline(svc_cmd, servicename):
        if svc_cmd == "/bin/systemctl":
            return "%s is-active %s" % (svc_cmd, servicename)
        else:
            return '/usr/bin/sudo -n ' + svc_cmd + ' ' + servicename + ' status 2>&1'

    def checkinits(self):
        '''check init scripts statuses'''
        if self.svccmd is None: 
            svc_cmd = self._findservice()
        else:
            svc_cmd = self.svccmd
        # loop round all the services
        for servicename in self.services:
            running_is_expected = True
            clean_servicename = servicename
            # check for negation (ie - service NOT running, ^ prefix)
            if servicename[0] == '^':
                clean_servicename = servicename[1:]
                running_is_expected = False
            cmdline = self.build_cmdline(svc_cmd, clean_servicename)
            initresults = [line.strip() for line in os.popen(cmdline).readlines()]
            # check for "running" regex in output
            for res in initresults:
                if re.search(self.matchregex, res) is not None and running_is_expected:
                    self.expected_services.add(servicename)
                    break
            # if running regex not found, check if negation applies
            if not servicename in self.expected_services:
                if running_is_expected:
                    self.rogue_services.add(servicename)
                else:
                    # not running and that's OK
                    self.expected_services.add(servicename)
        # if # of ok results == # of services checked, all ok
        if len(self.expected_services) == len(self.services):
            return 0
        else:
            return 1

def main():
    parser = OptionParser()
    parser.add_option("--services", dest="services", help="service1,service2")
    parser.add_option("--matchregex", dest="matchregex", default="(?:^active|is running|start/running)",
        help="regex to match running service status")
    parser.add_option("--svccmd", dest="svccmd", help="full path to command to run for check")
    (options, args) = parser.parse_args()
    if options.services is None:
        print("UNKNOWN: No services specified")
        sys.exit(2)
    ci = CheckInitService(options)
    rc = ci.checkinits()
    if rc == 0:
        rcstr = 'OK: all services as expected (' + ','.join(ci.expected_services) + ')'
    else:
        rcstr = 'CRITICAL: Rogue (' +  ','.join(ci.rogue_services) + ')'
        if len(ci.expected_services) > 0:
            rcstr += ' Expected (' + '.'.join(ci.expected_services) + ')'
    print(rcstr)
    sys.exit(rc)

if __name__ == '__main__':
    main()

