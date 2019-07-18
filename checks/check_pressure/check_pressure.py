#!/usr/bin/env python

from __future__ import print_function

def get_cli_args():
    '''get cli args'''
    return None

def read_pressure():
    '''read info under /proc/pressure'''
    presstats = {}
    for monitor in ('cpu', 'io', 'memory'):
        try:
            with open('/proc/pressure/%s' % monitor) as pres:
                presstats[monitor] = pres.read()
        except:
            return None
    return presstats


def main():
    '''get args, read pressure'''
    args = get_cli_args()
    presstats = read_pressure()
    if presstats is None:
        print("Can't open /proc/pressure/. Supported on 4.2+ kernels only")



if __name__ == '__main__':
    main()
