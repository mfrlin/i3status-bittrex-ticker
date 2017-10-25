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


TIMEOUT = 2
COLOR_GREEN = '#00FF00'
COLOR_RED = '#FF0000'
COLOR_WHITE = '#FFFFFF'
COINS = [('XRP', 0.20), ('ADX', 1.5), ('ANT', 4.2), ('TRST', 0.4)]

class Ticker(object):
    def __init__(self):
        url = 'https://bittrex.com/api/v1.1/public/getticker?market=USDT-BTC'
        try:
            btc_ticker = json.loads(urllib2.urlopen(url, timeout=TIMEOUT).read(), parse_float=decimal.Decimal)
            self.btc_price = btc_ticker['result']['Last']
        except:
            self.btc_price = 0

    def get_price(self, coin):
        try:
            ticker = json.loads(
                urllib2.urlopen(
                    'https://bittrex.com/api/v1.1/public/getticker?market=BTC-{}'.format(coin), 
                    timeout=2).read(),
                parse_float=decimal.Decimal)
            return self.btc_price * ticker['result']['Last']
        except Exception as e:
            return 0

def get_line(coin, price, limit):
    if price > limit:
        color = COLOR_GREEN
    else:
        color = COLOR_RED
    return {'full_text': '{} {:.3f}$ > {}$'.format(coin, price, limit), 'name' : 'cointicker', 'color': color, 'instance': coin}


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
        ticker = Ticker()
        for coin, limit in reversed(COINS):
            line = get_line(coin, ticker.get_price(coin), limit)
            j.insert(0, line)
        j.insert(0, {'full_text': 'BTC {:.1f}$'.format(ticker.btc_price), 'name' : 'cointicker', 'color': COLOR_WHITE, 'instance': 'BTC'})
        # and echo back new encoded json
        print_line(prefix+json.dumps(j))