# check_c2c_tests.py - for nose

from check_c2c import c2c_util

def test_parse1():
    with open('check_c2c/tests/soc-upm.html') as f:
        departures = c2c_util.parse_page(f.read())
    assert [('21:31', 'On Time'), ('21:43', 'On Time'), ('22:01', 'On Time'), ('22:31', 'On Time'), ('23:01', 'On Time')] == departures

def test_parse2():
    with open('check_c2c/tests/bkg-fst.html') as f:
        departures = c2c_util.parse_page(f.read())
    assert [('23:47', '23:50'), ('00:13', 'On Time')] == departures

def test_find_delay1():
    assert c2c_util.find_delays('There are no direct services') == \
      (1, 'No trains found')
    
def test_nagios_codes():
    assert c2c_util.nag_code_to_status(0, 'Running') == 'OK: Running'

