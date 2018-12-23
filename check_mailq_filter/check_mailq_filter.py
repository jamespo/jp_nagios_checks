#!/usr/bin/env python3

# check_mailq_filter (c) jamespo[at]gmail[dot]com
# checks postfix mailq with inclusive or exclusive regex filters

# Filter is based on first line of queue entry, eg
# 1CCBE6000F1    27748 Tue Dec 18 03:54:08  notification@facebookmail.com

import os
import re
import sys
from subprocess import Popen, PIPE
from optparse import OptionParser


def getopts():
    '''get CLI args'''
    parser = OptionParser()
    parser.add_option("-w", dest="warn", help="warning threshold",
                      type="int", default=5)
    parser.add_option("-c", dest="crit", help="critical threshold",
                      type="int", default=15)
    parser.add_option("-i", "--incregex", dest="incregex",
                      help="regex to include in count")
    parser.add_option("-x", "--excregex", dest="excregex",
                      help="regex to exclude in count")
    (opts, args) = parser.parse_args()
    return opts


def run_mailq(exe=None):
    '''run the mailq cmd and return output & rc'''
    if exe is None:
        exe = ['/usr/bin/mailq']
    p = Popen(exe, stdout=PIPE, stderr=PIPE)
    (stdout, stderr) = p.communicate()
    stdout, stderr = stdout.decode("utf-8"), stderr.decode("utf-8")
    if os.getenv("DEBUG") is not None:
        print(stdout, stderr)  # DEBUG
    rc = p.returncode
    return stdout, stderr, rc


def check_mailq(stdout, stderr, rc, incregex, excregex):
    '''check the output from mailq - returns # of mails in queue'''
    if 'Mail queue is empty' in stdout:
        return 0, 0, 0
    total_mails, excluded_from_q, included_in_q = 0, 0, 0
    lineregex = re.compile('[A-F0-9]{11} +[0-9]+')
    for line in stdout.split("\n"):
        if re.match(lineregex, line):
            total_mails += 1
            if excregex and re.search(excregex, line):
                excluded_from_q += 1
            elif incregex and re.search(incregex, line):
                included_in_q += 1
            else:
                included_in_q += 1
    return total_mails, excluded_from_q, included_in_q


def status(total_mails, excluded_from_q, included_in_q, opts):
    '''return monitoring message & rc from status'''
    status_str = "%s mails included (%s excluded, %s total)" \
        % (included_in_q, excluded_from_q, total_mails)
    if included_in_q >= opts.crit:
        status_str = "CRITICAL: %s" % status_str
        rc = 1
    elif included_in_q >= opts.warn:
        status_str = "WARNING: %s" % status_str
        rc = 2
    else:
        status_str = "OK: %s" % status_str
        rc = 0
    return status_str, rc


def compregex(regex):
    '''compile regex'''
    if regex is not None:
        return re.compile(regex)
    return None


def main():
    '''get args, run mailq, filter output & check status'''
    opts = getopts()
    incregex, excregex = compregex(opts.incregex), compregex(opts.excregex)
    mailq_output = run_mailq()
    mail_nos = check_mailq(*mailq_output, incregex, excregex)
    status_str, rc = status(*mail_nos, opts)
    print(status_str)
    sys.exit(rc)


if __name__ == '__main__':
    main()
