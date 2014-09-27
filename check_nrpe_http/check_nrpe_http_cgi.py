#!/usr/bin/env python

# check_nrpe_http_cgi.py - run nrpe scripts as CGI
# Copyright James Powell 2014 / jamespo [at] gmail [dot] com

import subprocess
import os, os.path
import re
import sys
import json
import ConfigParser
import cgi
import cgitb    # DEBUG
cgitb.enable()  # DEBUG

NRPE_HTTP_CONF = '/etc/check_nrpe_http.conf'

def read_conf(conffile):
    '''read & return config file'''
    if os.path.isfile(NRPE_HTTP_CONF):
        parsedconf = ConfigParser.SafeConfigParser({ 'allowed_ip' : None,
                                                     'debug' : False,
                                                     'secure' : False })
        parsedconf.read(NRPE_HTTP_CONF)
        return parsedconf
    else:
        return None

def print_http_headers(debug):
    '''print http header'''
    if debug:
        print "Content-Type: text/html"  # DEBUG
    else:
        print "Content-Type: application/json"
    print "Cache-Control: no-cache, no-store, must-revalidate"
    print "Pragma: no-cache"
    print "Expires: 0"
    print

def print_results(results):
    print json.dumps(results)

def run_check(conf):
    '''get & verify cgi arguments then run the check'''
    form = cgi.FieldStorage()
    args  = form.getfirst("args", "")
    check  = form.getfirst("check", "")
    check_results = {}

    # verify check isn't dir traversal attempt, etc
    if not re.match('\w+\.?\w*$', check):
        print_results({ 'output' : 'check badly formed', 
                        'returncode' : 3 })
        sys.exit()

    plugin_dir = conf.get('main', 'plugin_dir')
    fullcheck = os.path.join(plugin_dir, check)

    # run the check
    try:
        check_results['output'] = subprocess.check_output([fullcheck, args]).rstrip()
        check_results['returncode'] = 0
    except subprocess.CalledProcessError as e:
        # non-zero returncode, ie - check failed
        check_results['output'] = e.output.rstrip()
        check_results['returncode'] = e.returncode
    except OSError as e:
        # check execution failed (eg binary not present), return unknown
        check_results['output'] = e[1]
        check_results['returncode']= 3

    check_results['command'] = check
    return check_results

    
def main():
    conf = read_conf(NRPE_HTTP_CONF)
    allowed_ip = conf.get('main', 'allowed_ip')
    print_http_headers(conf.getboolean('main','debug'))
    if conf is None:
        print_results({ 'output' : 'No conf file', 
                        'returncode' : 3 })
    elif conf.getboolean('main', 'secure') and (os.environ.get('HTTPS', 'off') != 'on'):
        # reject if required to run under HTTPS & it isn't
        print_results({ 'output' : 'Not called via HTTPS', 
                        'returncode' : 3 })
    elif (allowed_ip is not None) and (os.environ['REMOTE_ADDR'] not in
                                       allowed_ip.split(',')):
        # IP calling check not in permitted list
        print_results({ 'output' : 'Not allowed from %s' % os.environ['REMOTE_ADDR'], 
                        'returncode' : 3 })
    else:
        check_results = run_check(conf)
        print_results(check_results)

if __name__ == '__main__':
    main()
