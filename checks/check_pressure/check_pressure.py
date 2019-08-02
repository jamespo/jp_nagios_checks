#!/usr/bin/env python

from __future__ import print_function
from collections import defaultdict
from operator import gt, lt
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
                          help="warning thresholds [default: \"%default\"]")
        parser.add_option("-c", dest="critical",
                          default='somecpu10>0.5,fullio10>0.5,fullmemory10>0.5',
                          help="critical thresholds [default: \"%default\"]")
        (options, args) = parser.parse_args()
        return options

    @staticmethod
    def parse_cli(options):
        '''parse the warning & critical thresholds'''
        parsed_chks = {}
        for param in ('warning', 'critical'):
            chklevel = {}
            parsed_chks[param] = chklevel
            checks = getattr(options, param).split(",")
            for check in checks:
                fieldsmatch = re.match('(full|some)(cpu|io|memory)(\d+)(>|<)(.+)$', check)
                assert fieldsmatch is not None
                scope, subsys, period, op, threshold = fieldsmatch.groups()
                threshold = float(threshold)
                fields = (scope, 'avg' + period, op, threshold)
                if chklevel.get(subsys):
                    chklevel[subsys].append(fields)  # exists, append
                else:
                    chklevel[subsys] = [fields]
        return parsed_chks

    @staticmethod
    def check2str(check, subsys):
        '''convert check params back to string for output'''
        scope, period, op, threshold = check
        return "%s-%s-%s%s%s" % (subsys, *check)


def output(rc, msg):
    '''format rc & output msg & quit'''
    rc2str = ('OK', 'WARNING', 'CRITICAL', 'UNKNOWN')
    print(rc2str[rc] + ': ' + msg)
    sys.exit(rc)


def check_results(res):
    if len(res) == 0:
        output(0, 'All under threshold')
    else:
        for sevnum, severity in ((2, 'critical'), (1, 'warning')):
            if res.get(severity):
                output(sevnum, ",".join(res[severity]))
    output(3, '')


class Pressure():
    '''store and interrogate /proc/pressure'''

    def __init__(self):
        self.presstats = Pressure.read_pressure()

    @staticmethod
    def cleandata(lines):
        '''parse the pressure output'''
        parsedlines = {}
        for line in lines.strip().split("\n"):
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
                    # parse pressure file with cleandata
                    presstats[monitor] = Pressure.cleandata(pres.read())
            except:
                return None
        return presstats

    def run_checks(self, checks):
        '''run all the checks against stats'''
        result = defaultdict(list)
        for param in ('critical', 'warning'):
            for subsys in checks[param].keys():
                for chk in checks[param][subsys]:
                    chk_res = self.run_check(chk, subsys)
                    if chk_res is not None:
                        # if check failed add to list
                        result[param].append(chk_res)
        return result

    def run_check(self, check, subsys):
        '''run an individual check'''
        scope, period, op, threshold = check
        comp2op = {'>': gt, '<': lt}
        if not comp2op[op](threshold, self.presstats[subsys][scope][period]):
            # check failed
            return PressureCLI.check2str(check, subsys)
        else:
            return None


def main():
    '''get args, read pressure'''
    pc = PressureCLI()
    p = Pressure()
    res = p.run_checks(pc.checks)
    # print(pc.checks)  # DEBUG
    # print(p.presstats)  # DEBUG
    # print(res)  # DEBUG
    if p.presstats is None:
        output(3, "Can't open /proc/pressure/. Supported on 4.2+ kernels only")
    else:
        check_results(res)


if __name__ == '__main__':
    main()
