jp_nagios_checks
================

Miscellaneous nagios checks

check\_meminfo
----------

Run custom checks against the values in /proc/meminfo

check\_pressure
----------

Monitor /proc/pressure on 4.2+ kernel linux systems

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

	--svccmd
		optional. specify the "service" command for your OS (eg on Centos 7
		this would be /bin/systemctl, on Centos 6 /sbin/service, otherwise
		it will try & guess)

INSTALLATION

Unless you are using systemctl (ie Systemd) you must have a sudo entry for the user running this check (eg nagios). Also ensure that you disable requiring a tty for this user in sudoers

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

