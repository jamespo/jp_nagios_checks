qicinga
=======

short script to display Icinga status on the commandline

Usage
-----

Create a config file in either /etc/qicinga or ~/.config/.qicinga with contents as below

    [Main]
    icinga_url: https://icinga.example.com/icinga/
    username: myicingauser
    password: mypass

As this file contains your password ENSURE it is permissioned correctly (ie chmod 0600).
Additionally as this is just a reporting script it should be a read-only user.

Options:
    -h, --help   show this help message and exit
    -a, --all    show all statuses
	-s           short summary
	-c           colour output
	-b           no colour output
	-q           quiet - no output, no summary, just return code
	-x HOSTNAME  hostname - AUTOSHORT / AUTOLONG
			  

The colour output option works best on black background terminals.

Misc
----

This won't work with stock Nagios as it relies on Icinga's ability to output in JSON format.

A version for Icinga 2 which is under active development is available here: https://github.com/jamespo/qicinga2
