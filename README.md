jp_nagios_checks
================

Miscellaneous nagios checks


check_init_service
----------


Checks on a Red Hat / Centos / Ubuntu / Debian system whether services in init are running.

USAGE: check_init_service --services service1,service2


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


check_jar_sig_expire
----------


Checks whether the signature on a given JAR file has expired or is close to expiry.


check_pywhois
----------

Checks whether a domain name is close to expiry
