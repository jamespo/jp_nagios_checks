#!/usr/bin/env python

# check_nrpe_http_cgi.py - run nrpe scripts as CGI
# Copyright James Powell 2014 / jamespo [at] gmail [dot] com

import subprocess
import os, os.path
import re
import sys
import json
import ConfigParser
import shlex
import cgi
import cgitb    # DEBUG
cgitb.enable()  # DEBUG

NRPE_HTTP_CONF = '/etc/check_nrpe_http.conf'

def read_conf(conffile):
    '''read & return config file'''
    if os.path.isfile(NRPE_HTTP_CONF):
        parsedconf = ConfigParser.SafeConfigParser({ 'allowed_ip' : None,
                                                     'format' : 'json',
                                                     'secure' : False })
        parsedconf.read(NRPE_HTTP_CONF)
        return parsedconf
    else:
        return None

def print_http_headers(output_format = 'json'):
    '''print http header'''
    if output_format == 'debug':
        print "Content-Type: text/html"  # DEBUG
    elif output_format == 'json':
        print "Content-Type: application/json"
    elif output_format in ('text', 'prometheus'):
        print "Content-Type: text/plain"
    print "Cache-Control: no-cache, no-store, must-revalidate"
    print "Pragma: no-cache"
    print "Expires: 0"
    print

def output_plain(results):
    reslist = ("%s %s" % (k,v) for k,v in results.iteritems())
    return "\n".join(reslist)

def output_prometheus(results):
    '''just performance stats for input to prometheus.io'''
    performance = results['output'].split('|')[-1].strip() # get perf data string out
    statlines = (a.strip() for a in performance.split(','))
    statdict = dict(map((lambda y: y.split('=')), statlines))
    return output_plain(statdict)

def print_results(output_format, results):
    print_http_headers(output_format)
    if output_format == 'json':
        print json.dumps(results)
    elif output_format == 'text':
        print output_plain(results)
    elif output_format == 'prometheus':
        print output_prometheus(results)

def run_check(conf):
    '''get & verify cgi arguments then run the check'''
    form = cgi.FieldStorage()
    args  = shlex.split(form.getfirst("args", ""))
    check  = form.getfirst("check", "")
    check_results = {}

    # verify check isn't dir traversal attempt, etc
    if not re.match('\w+\.?\w*$', check):
        return({ 'output' : 'check badly formed', 
                 'returncode' : 3 })

    plugin_dir = conf.get('main', 'plugin_dir')
    fullcheck = os.path.join(plugin_dir, check)
    fullargs = [fullcheck] + args
    
    # run the check
    try:
        check_results['output'] = subprocess.check_output(fullargs).rstrip()
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
    output_format = conf.get('main', 'format') # one of json,debug,text
    if conf is None:
        print_results(output_format, { 'output' : 'No conf file', 
                    'returncode' : 3 })
    elif conf.getboolean('main', 'secure') and (os.environ.get('HTTPS', 'off') != 'on'):
        # reject if required to run under HTTPS & it isn't
        print_results(output_format, { 'output' : 'Not called via HTTPS', 
                        'returncode' : 3 })
    elif (allowed_ip is not None) and (os.environ['REMOTE_ADDR'] not in
                                       allowed_ip.split(',')):
        # IP calling check not in permitted list
        print_results(output_format, { 'output' : 'Not allowed from %s' % os.environ['REMOTE_ADDR'], 
                        'returncode' : 3 })
    else:
        # all good
        check_results = run_check(conf)
        print_results(output_format, check_results)

if __name__ == '__main__':
    main()
