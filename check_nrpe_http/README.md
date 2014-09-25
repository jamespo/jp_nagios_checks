check\_nrpe\_http
===============

Plugin for nagios that allow you to run checks over HTTP. Written in Python 2.x

## Why would you want this

For the usual advantages of HTTP transport, easier traversal past firewalls (including proxy usage), HTTPS, authentication (for example, configure mutual SSL in Apache), webserver logging, etc.

## Setup

### Nagios Client

Configure <code>check\_nrpe\_http_cgi.py</code> to run as a CGI under your webserver, eg in Apache:

    ScriptAlias /jpcgi/ /opt/www/cgi-bin/
    <Directory "/opt/www/cgi-bin">
 	 AllowOverride None
 	 Options +ExecCGI -MultiViews
 	 Require all granted
    </Directory>

Install the conf file <code>/etc/check\_nrpe\_http.conf</code>, options:

    [main]
    debug: False
    secure: False
    plugin_dir: /usr/local/nagios4/libexec

### Nagios Server

From the command line you call the client like so:

<code>./check\_nrpe\_http --url=http://localhost/jpcgi/check\_nrpe\_http\_cgi.py --check=check_procs --args "-w 100 -c 200"</code>

