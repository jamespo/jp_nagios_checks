jp_nagios_checks
================

Miscellaneous nagios checks

check\_meminfo
----------

Run custom checks against the values in /proc/meminfo

USAGE: 

     check_meminfo -w Buffers/MemTotal<0.7 -c Buffers/MemTotal<0.9

This will warn if your buffer memory usage > 0.7 of total memory & go critical if it's > 0.9


check\_pressure
----------

Monitor /proc/pressure on 4.2+ kernel linux systems

	Usage: check_pressure.py [options]

	Options:
	-h, --help   show this help message and exit
	-w WARNING   warning thresholds [default:
				"somecpu10>0.2,fullio10>0.2,fullmemory10>0.2"]
	-c CRITICAL  critical thresholds [default:
				"somecpu10>0.5,fullio10>0.5,fullmemory10>0.5"]



check\_init\_service
----------


Checks on a Red Hat / Centos / Ubuntu / Debian system whether services in init are running.

	USAGE: check_init_service --services service1,service2


	PARAMETERS:

		--services
			comma separated list of services to check, at least one required

		--matchregex
			optional regular expression to match against service svcname status
			output. Defaults to (?:is running|start/running)

		--svccmd
			optional. specify the "service" command for your OS (eg on Centos 7
			this would be /bin/systemctl, on Centos 6 /sbin/service, otherwise
			it will try & guess)

INSTALLATION

Unless you are using systemctl (ie Systemd) you must have a sudo entry for the user running this check (eg nagios). Also ensure that you disable requiring a tty for this user in sudoers

	Defaults:nagios !requiretty
	nagios ALL = NOPASSWD: /sbin/service * status

NOTE: python 2 only - see check_startup_service for enhanced python 3 version


check\_startup\_service
----------

Same as check_init_service but for python 3 and can also check if services are NOT running (eg for DR) by prefixing them with ^

     check_startup_service --services=postfix,^httpd


check\_jar\_sig\_expire
----------


Checks whether the signature on a given JAR file has expired or is close to expiry.


check_pywhois
----------

Checks whether a domain name is close to expiry


check_c2c
--------

Deprecated as format on webserver changed - see check_darwin


check_multi_url
--------

Graduated to its own repo! https://github.com/jamespo/check_multi_url


check_darwin
---------

Checks if National Rail trains are running on schedule.

Usage: check_darwin -f [fromstationcode] -t [tostationcode]

eg for Southend Central to Limehouse

check_darwin -f SOC -t LHS

Requires registration for National Rail LDBWS
https://lite.realtime.nationalrail.co.uk/OpenLDBWS/


check\_nrpe\_http
---------

An alternative transport for remote nagios checks than NRPE - HTTP to
get through firewalls etc.

Install check\_nrpe\_http\_cgi.py as a cgi script on your client server and
use check\_nrpe\_http on your Nagios / Icinga server to call the check.


check\_last\_lines
---------

Check the last n lines of a file (typically a logfile) for a line that matches
a regex. If it matches, exit with CRITICAL. Use this for detecting fatal errors.

Usage: check_last_lines -f FILENAME -n NUMLINES -m MATCHREGEX


check\_mysql\_dbs
----------

Check integrity of your mysql databases.

