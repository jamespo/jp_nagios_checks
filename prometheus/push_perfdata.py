#!/usr/bin/env python

# push_perfdata.py - push performance data from icinga ido2db to prometheus

from __future__ import print_function
import sqlalchemy as sql
import re
import os
import time
import ConfigParser
from optparse import OptionParser

# ADD last_check column
# note timestamps in milliseconds

def readconf():
    config = ConfigParser.ConfigParser()
    config.read(['/etc/push_perfdata.conf', 
                 os.path.expanduser('~/.config/.push_perfdata.conf')])
    return config

def getoptions():
    parser = OptionParser()
    parser.add_option("-i", "--interval", dest="upd_interval", help="update interval (secs)", 
                      default="0")
    parser.add_option("-o", "--outputfile", dest="outputfile")
    (options, args) = parser.parse_args()
    options.upd_interval = int(options.upd_interval)
    return options

class PerfData:
    def __init__(self, db):
        self.db = db
        self.checks = {}

    def run(self):
        self.checks = {}
        host_sql = """select alias, perfdata from icinga_hosts ih, icinga_hoststatus ihs 
        where ih.host_object_id = ihs.host_object_id"""
        service_sql = """select ics.display_name, perfdata, ih.alias 
        from icinga_services ics, icinga_servicestatus iss, icinga_hosts ih
        where ics.service_object_id = iss.service_object_id and perfdata <> ''
        and ih.host_object_id = ics.host_object_id"""
        results = self.run_sql(host_sql)
        self.parse_hostchecks(results)
        results = self.run_sql(service_sql)
        self.parse_servicechecks(results)

    def __str__(self):
        allchecks_str = ''
        for label, checkvalue in self.checks.iteritems():
            allchecks_str += "%s=%s\n" % (label, checkvalue)
        return allchecks_str

    def run_sql(self, sqltxt):
        str_sql = sql.text(sqltxt)
        return self.db.execute(str_sql).fetchall()

    def parse_hostchecks(self, results):
        for alias, perfdata in results:
            for perflabel, perfvalue in self.split_perfdata(perfdata):
                label = self.cleanlabel("%s_%s_%s" % (alias, "hostcheck", perflabel))
                self.checks[label] = perfvalue

    def parse_servicechecks(self, results):
        for displayname, perfdata, alias in results:
            for perflabel, perfvalue in self.split_perfdata(perfdata):
                label = self.cleanlabel("%s_%s_%s_%s" % (alias, displayname, "servicecheck", perflabel))
                self.checks[label] = perfvalue

    def output(self, options):
        if options.outputfile:
            with open(options.outputfile, "w") as f:
                f.write(str(self))
        else:
            print(self)

    @staticmethod
    def cleanlabel(label):
        """
        :type label: str
        Fix label according to http://prometheus.io/docs/concepts/data_model/
        """
        label = re.sub("^[^a-zA-Z_:]", "_", label)
        # TODO: doesn't accept multiple substitutions, nasty
        label = re.sub("[^a-zA-Z0-9_:]+", "_", label)
        return label.lower()

    @staticmethod
    def split_perfdata(perf_str):
        """
        :type perf_str: str
        """
        fields = perf_str.split(";")
        split_re = re.compile('([\d\w_-]+)=(\d+\.?\d*)(\w*)')
        for field in fields:
            match = split_re.search(field)
            if match:
                # stick units on the end (if there) TODO: sanitize units (f/ex: make all time seconds)
                units = "_" + match.group(3) if match.group(3) else ''
                fieldname = match.group(1)   + units
                yield (fieldname, match.group(2))

def main():
    config = readconf()
    options = getoptions()
    db_conf_vals = tuple(config.get('Main', item) for item in 
                         ('username','password','host','db'))
    db = sql.create_engine('mysql://%s:%s@%s/%s' % db_conf_vals)
    pd = PerfData(db)
    
    pd.run()
    pd.output(options)
    if options.upd_interval > 0:
        while(True):
            time.sleep(options.upd_interval)
            pd.run()
            pd.output(options)

if __name__ == '__main__':
    main()
