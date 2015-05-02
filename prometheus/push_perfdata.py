#!/usr/bin/env python

# push_perfdata.py - push performance data from icinga ido2db to prometheus

from __future__ import print_function
import sqlalchemy as sql
import re
import os
import ConfigParser

# ADD last_check column
# note timestamps in milliseconds

def readconf():
    config = ConfigParser.ConfigParser()
    config.read(['/etc/push_perfdata.conf', 
                 os.path.expanduser('~/.config/.push_perfdata.conf')])
    return config

def cleanlabel(label):
    """
    :type label: str
    Fix label according to http://prometheus.io/docs/concepts/data_model/
    """
    label = re.sub("^[^a-zA-Z_:]", "_", label)
    # TODO: doesn't accept multiple substitutions, nasty
    label = re.sub("[^a-zA-Z0-9_:]+", "_", label)
    return label.lower()
    
def split_perfdata(perf_str):
    """
    :type perf_str: str
    """
    fields = perf_str.split(";")
    split_re = re.compile('([\d\w_-]+)=(\d+\.?\d*)(\w*)')
    for field in fields:
        match = split_re.search(field)
        if match:
            units = "_" + match.group(3) if match.group(3) else ''
            fieldname = match.group(1)   + units
            yield (fieldname, match.group(2))


def main():
    host_sql = """select alias, perfdata from icinga_hosts ih, icinga_hoststatus ihs 
    where ih.host_object_id = ihs.host_object_id"""
    service_sql = """select ics.display_name, perfdata, ih.alias 
    from icinga_services ics, icinga_servicestatus iss, icinga_hosts ih
    where ics.service_object_id = iss.service_object_id and perfdata <> ''
    and ih.host_object_id = ics.host_object_id"""
    config = readconf()
    db_conf_vals = tuple(config.get('Main', item) for item in 
                          ('username','password','host','db'))
    db = sql.create_engine('mysql://%s:%s@%s/%s' % db_conf_vals)

    str_sql = sql.text(host_sql)
    results = db.execute(str_sql).fetchall()
    hosts = {}
    for alias, perfdata in results:
        label = cleanlabel("%s_%s" % (alias, "hostcheck"))
        hosts[label] = tuple(split_perfdata(perfdata))
    print(hosts)

    str_sql = sql.text(service_sql)
    results = db.execute(str_sql).fetchall()
    services = {}
    for displayname, perfdata, alias in results:
        for perflabel, perfvalue in split_perfdata(perfdata):
            label = cleanlabel("%s_%s_%s_%s" % (alias, displayname, perflabel, "servicecheck"))
            services[label] = perfvalue
    print(services)

if __name__ == '__main__':
    main()
