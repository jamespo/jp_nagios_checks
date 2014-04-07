#!/usr/bin/env python
# -*- coding:utf-8 -*-


import os,sys
os.symlink('check_tfl', 'check_tfl.py')
sys.dont_write_bytecode = True
from check_tfl import tflfeed
import urllib2
import atexit

@atexit.register
def rm_symlink():
    os.unlink('check_tfl.py')

def test_static():
    # run module against file on disk
    tfl = tflfeed('LineStatus')
    print tfl.getdescr('Central')
    print tfl.getstatusid('Central')
    print tfl.getanyproblems()


def test_live():
    # run module against live URL
    # Important: you must register with TFL to use this URL!
    print 'Live Status:'
    livefeed = urllib2.urlopen('http://cloud.tfl.gov.uk/TrackerNet/LineStatus')
    livetfl = tflfeed(livefeed)
    print livetfl.getanyproblems()

if __name__ == "__main__":
    test_static()
    test_live()

