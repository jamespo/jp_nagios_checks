jp_nagios_checks
================

Miscellaneous nagios checks


check\_init\_service
----------


Checks on a Red Hat / Centos / Ubuntu / Debian system whether services in init are running.

USAGE: check\_init\_service --services service1,service2


PARAMETERS:

	--services
		comma separated list of services to check, at least one required
		
	--matchregex
		optional regular expression to match against service svcname status
		output. Defaults to (?:is running|start/running)

INSTALLATION

You must have a sudo entry for the user running this check (eg nagios). Also ensure that you disable requiring a tty for this user in sudoers

    Defaults:nagios !requiretty
    nagios ALL = NOPASSWD: /sbin/service * status


check\_jar\_sig\_expire
----------


Checks whether the signature on a given JAR file has expired or is close to expiry.


check_pywhois
----------

Checks whether a domain name is close to expiry


check_c2c
--------

Checks if C2C trains are running on schedule.

Usage: check_c2c.py -f [fromstationcode] -t [tostationcode]

eg for Southend Central to Limehouse

check_c2c.py -f SOC -t LHS
