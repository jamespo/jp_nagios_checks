push_perfdata.py - present icinga check performance data for input to prometheus

Dependencies

Python 2.6+

sqlalchemy
MySQL-python


Setup

Create /etc/push_perfdata.conf  (or ~/.config/.push_perfdata.conf) with ido2db details:

[Main]
username: blah
password: asdfq3
host: localhost
db: icinga

Set push_perfdata.py to run in cron every x minutes, outputting to a web-accessible directory for prometheus to read

*/5 * * * * icinga /usr/local/bin/push_perfdata.py -o /var/www/html/perfdata.txt

Configure prometheus to read this page
