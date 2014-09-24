#!/usr/bin/env python

# check_nrpe_http_cgi.py - run nrpe scripts as CGI

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
    if os.path.isfile(NRPE_HTTP_CONF):
        parsedconf = ConfigParser.SafeConfigParser()
        parsedconf.read(NRPE_HTTP_CONF)
        return parsedconf
    else:
        return None

def print_http_headers(debug):
    # header
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
    
def main():
    conf = read_conf(NRPE_HTTP_CONF)
    if conf is None:
        print_http_headers(False)
        print_results({ 'output' : 'No conf file', 
                        'returncode' : 3 })
        sys.exit()
    else:
        print_http_headers(conf.get('main','debug'))

        form = cgi.FieldStorage()
        args  = form.getfirst("args", "")
        check  = form.getfirst("check", "")

        # verify check isn't dir traversal attempt, etc
        if not re.match('\w+\.?\w*$', check):
            print_results({ 'output' : 'check badly formed', 
                            'returncode' : 3 })
            sys.exit()

        plugin_dir = conf.get('main', 'plugin_dir')
        fullcheck = os.path.join(plugin_dir, check)
        check_results = {}

        # run the check
        try:
            check_results['output'] = subprocess.check_output([fullcheck, args]).rstrip()
            check_results['returncode'] = 0
        except subprocess.CalledProcessError as e:
            # non-zero returncode, ie - check failed
            check_results['output'] = e.output
            check_results['returncode'] = e.returncode
        except OSError as e:
            # check execution failed (eg binary not present), return unknown
            check_results['output'] = e[1]
            check_results['returncode']= 3

        check_results['command'] = check
        print_results(check_results)

if __name__ == '__main__':
    main()
