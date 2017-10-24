#!/usr/bin/env python
# -*- coding: utf-8 -*-

# This script is a simple wrapper which prefixes each i3status line with custom
# information. It is a python reimplementation of:
# http://code.stapelberg.de/git/i3status/tree/contrib/wrapper.pl
#
# To use it, ensure your ~/.i3status.conf contains this line:
#     output_format = "i3bar"
# in the 'general' section.
# Then, in your ~/.i3/config, use:
#     status_command i3status | ./i3status_wrapper.py
# In the 'bar' section.

import decimal
import json
import sys
import urllib2


COINS = ['XRP', 'ADX', 'ANT', 'TRST']

def get_price(coin):
    try:
        ticker = json.loads(
            urllib2.urlopen(
                'https://bittrex.com/api/v1.1/public/getticker?market=BTC-{}'.format(coin), 
                timeout=2).read(),
            parse_float=decimal.Decimal)
        return ticker['result']['Last']
    except Exception as e:
        return '0'


def print_line(message):
    """ Non-buffered printing to stdout. """
    sys.stdout.write(message + '\n')
    sys.stdout.flush()

def read_line():
    """ Interrupted respecting reader for stdin. """
    # try reading a line, removing any extra whitespace
    try:
        line = sys.stdin.readline().strip()
        # i3status sends EOF, or an empty line
        if not line:
            sys.exit(3)
        return line
    # exit on ctrl-c
    except KeyboardInterrupt:
        sys.exit()

if __name__ == '__main__':
    # Skip the first line which contains the version header.
    print_line(read_line())

    # The second line contains the start of the infinite array.
    print_line(read_line())

    while True:
        line, prefix = read_line(), ''
        # ignore comma at start of lines
        if line.startswith(','):
            line, prefix = line[1:], ','

        j = json.loads(line)
        # insert information into the start of the json, but could be anywhere
        for coin in reversed(COINS):
            j.insert(0, {'full_text': '{} {}'.format(coin, get_price(coin)), 'name' : 'cointicker', 'color': '#00FF00', 'instance': coin})
        # and echo back new encoded json
        print_line(prefix+json.dumps(j))