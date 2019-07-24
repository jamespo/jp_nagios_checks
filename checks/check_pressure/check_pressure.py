#!/usr/bin/env python

from __future__ import print_function
from optparse import OptionParser
import re
import sys


class PressureCLI():

    def __init__(self):
        options = self.get_cli_args()
        self.checks = self.parse_cli(options)
        
    @staticmethod
    def get_cli_args():
        '''get cli args'''
        parser = OptionParser()
        parser.add_option("-w", dest="warning",
                          default='somecpu10>0.2,fullio10>0.2,fullmemory10>0.2',
                          help="warning thresholds")
        parser.add_option("-c", dest="critical",
                          default='somecpu10>0.5,fullio10>0.5,fullmemory10>0.5',
                          help="critical thresholds")
        (options, args) = parser.parse_args()
        return options

    @staticmethod
    def parse_cli(options):
        parsed_chks = {}
        for param in options.__dict__:   # param = warning or critical
            chklevel = {}
            parsed_chks[param] = chklevel
            checks = getattr(options, param).split(",")
            for check in checks:
                fieldsmatch = re.match('(....)(.+)(>|<)(.+)$', check)
                assert fieldsmatch is not None
                scope, subsys, op, threshold = fieldsmatch.groups()
                if chklevel.get(subsys):
                    chklevel[subsys].append((scope, op, threshold))
                else:
                    chklevel[subsys] = [(scope, op, threshold)]
        return parsed_chks

    
def output(rc, msg):
    '''format rc & output msg & quit'''
    rc2str = ('OK', 'WARNING', 'CRITICAL', 'UNKNOWN')
    print(rc2str[rc] + ': ' + msg)
    sys.exit(rc)


class Pressure():
    '''store and interrogate /proc/pressure'''

    def __init__(self):
        self.presstats = Pressure.read_pressure()

    @staticmethod
    def cleandata(lines):
        '''parse the pressure output'''
        parsedlines = {}
        for line in lines:
            stattype, stats = line.split(" ", 1)  # get some/full
            parsedlines[stattype] = {}
            for stat in stats.split(" "):
                # get key & value
                key, val = stat.split("=")
                parsedlines[stattype][key] = float(val)
        return parsedlines

    @staticmethod
    def read_pressure():
        '''read info under /proc/pressure'''
        presstats = {}
        for monitor in ('cpu', 'io', 'memory'):
            try:
                with open('/proc/pressure/%s' % monitor) as pres:
                    # cleanup line(s), split some/full if available & parse via cleandata
                    presstats[monitor] = Pressure.cleandata(pres.read().strip().split("\n"))
            except:
                return None
        return presstats



def main():
    '''get args, read pressure'''
    checks = PressureCLI().checks
    p = Pressure()
    print(checks)  # DEBUG
    print(p.presstats)  # DEBUG
    if p.presstats is None:
        output(3, "Can't open /proc/pressure/. Supported on 4.2+ kernels only")


if __name__ == '__main__':
    main()
