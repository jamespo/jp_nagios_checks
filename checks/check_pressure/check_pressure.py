#!/usr/bin/env python

from __future__ import print_function
from optparse import OptionParser
import sys

def get_cli_args():
    '''get cli args'''
    parser = OptionParser()
    parser.add_option("-w", dest="warning",  default='cpu10>0.2,fullio10>0.2,fullmemory10>0.2',
        help="warning thresholds")
    parser.add_option("-c", dest="critical", default='cpu10>0.5,fullio10>0.5,fullmemory10>0.5',
        help="critical thresholds")
    (options, args) = parser.parse_args()
    return options

def output(rc, msg):
    '''format rc & output msg & quit'''
    rc2str = ('OK', 'WARNING', 'CRITICAL', 'UNKNOWN')
    print(rc2str[rc] + ': ' + msg)
    sys.exit(rc)

def cleandata(line):
    '''parse the pressure output'''
    return line  # TODO

def read_pressure():
    '''read info under /proc/pressure'''
    presstats = {}
    for monitor in ('cpu', 'io', 'memory'):
        try:
            with open('/proc/pressure/%s' % monitor) as pres:
                line = pres.read().strip()
                presstats[monitor] = cleandata(line)
        except:
            return None
    return presstats


def main():
    '''get args, read pressure'''
    args = get_cli_args()
    presstats = read_pressure()
    print(presstats)  # DEBUG
    if presstats is None:
        output(3, "Can't open /proc/pressure/. Supported on 4.2+ kernels only")



if __name__ == '__main__':
    main()
