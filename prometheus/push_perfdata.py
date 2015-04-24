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

def split_perfdata(perf_str):
    """
    :type perf_str: str
    """
    fields = perf_str.split(";")
    split_re = re.compile('([\d\w_-]+)=([\d.\w%]+)')
    for field in fields:
        match = split_re.search(field)
        if match:
            yield (match.group(1), match.group(2))


def main():
    host_sql = "select alias, perfdata from icinga_hosts ih, icinga_hoststatus ihs where ih.host_object_id = ihs.host_object_id"
    service_sql = "select display_name, perfdata from icinga_services ics, icinga_servicestatus iss where ics.service_object_id = iss.service_object_id and perfdata <> ''"
    config = readconf()
    db_conf_vals = tuple( config.get('Main', item) for item in 
                          ('username','password','host','db'))
    db = sql.create_engine('mysql://%s:%s@%s/%s' % db_conf_vals)

    str_sql = sql.text(host_sql  )
    results = db.execute(str_sql).fetchall()
    for res in results:
        print(tuple(split_perfdata(res[1])))

    str_sql = sql.text(service_sql)
    results = db.execute(str_sql).fetchall()
    for res in results:
        print(tuple(split_perfdata(res[1])))

if __name__ == '__main__':
    main()
