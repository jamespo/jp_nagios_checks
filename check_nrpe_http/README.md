check\_nrpe\_http
===============

Plugin for nagios that allow you to run checks over HTTP. Written in Python 2.x

## Why would you want this?

For the usual advantages of HTTP transport, easier traversal past firewalls (including proxy usage), HTTPS, authentication (for example, configure mutual SSL in Apache), webserver logging, etc.

You can even have a border host that you hit with check\_nrpe\_http in turn calling check_nrpe checks on hosts inside that network!

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
    secure: False
    plugin_dir: /usr/local/nagios4/libexec
    allowed_ip: 127.0.0.1

All plugins called by the CGI must be under <code>plugin_dir</code>, relative paths for your check will not be accepted (create a directory and symlink in your checks if necessary).

<code>secure</code> should be set to True or False (default False). If True the check will not run unless called on an HTTPS server.

<code>allowed_ip</code> is a comma-separated list of IP addresses, if this is set the remote IP calling the CGI must be one of these addresses.

secure & allowed_ip restrictions can & should be enforced in your webserver configuration - this just allows a second way to give some feature parity with check\_nrpe.

### Nagios Server

From the command line you call the client like so:

<code>./check\_nrpe\_http --url=http://localhost/jpcgi/check\_nrpe\_http\_cgi.py --check=check_procs --args "-w 100 -c 200"</code>

Usage: <code>check\_nrpe\_http</code> [options]

    Options:
     -h, --help            show this help message and exit
     -u URL, --url=URL     
     -c CHECK, --check=CHECK
     -t TIMEOUT, --timeout=TIMEOUT   timeout (seconds)
     -a ARGS, --args=ARGS




