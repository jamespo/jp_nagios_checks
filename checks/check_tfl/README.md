check_tfl
=========

A nagios check for TFL's tube & overground service

USAGE
=====

check_tfl [-l lines]

With no arguments will check all lines (or with an argument of just all),
otherwise specify lines you are interested in, comma-separated.

Note to access the data feed http://cloud.tfl.gov.uk/TrackerNet/LineStatus
you should register at http://www.tfl.gov.uk/info-for/open-data-users/

CONFIGURATION IN NAGIOS
=======================

Create a commuting time period config as below:

    define timeperiod{
        timeperiod_name commute
        alias           Commuting Time
        monday          08:00-09:00,17:15-18:30
        tuesday         08:00-09:00,17:15-18:30
        wednesday       08:00-09:00,17:15-18:30
        thursday        08:00-09:00,17:15-18:30
        friday          08:00-09:00,17:15-18:30
        }

Define the command as below (presuming $USER8$ is set to the path you have
put check_tfl).

    define command {
        command_name    check_tfl
        command_line    $USER8$/check_init_service -l $ARG1$
        }

Define a service template using the command as below:

    define service {
        name            commute-service
        use             local-service
        check_period    commute
        register        0
        }

Then define the service (here for DLR)

    define service{
         use                             commute-service
         host_name                       cloud
         service_description             Commute Check
         check_command                   check_tfl!dlr
         max_check_attempts              1
         normal_check_interval           10
         retry_check_interval            5
         notification_interval           10
         }
