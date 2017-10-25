#!/usr/bin/env python
# -*- coding: utf-8 -*-

import ConfigParser
import decimal
import json
import os
import sys
import urllib2


TIMEOUT = 2
COLOR_GREEN = '#00FF00'
COLOR_RED = '#FF0000'
COLOR_WHITE = '#FFFFFF'

BASE_DIR = os.path.dirname(__file__)
CONFIG = ConfigParser.ConfigParser({'display_btc_price': True, }, allow_no_value=True)
CONFIG.read(BASE_DIR + '/conf.ini')

def get_config_decimal(section, option, default=None):
    try:
        return decimal.Decimal(CONFIG.get(section, option))
    except ConfigParser.NoOptionError:
        return default

def get_config_int(section, option, default=None):
    try:
        return CONFIG.getint(section, option)
    except ConfigParser.NoOptionError:
        return default

def get_config_boolean(section, option, default=None):
    try:
        return CONFIG.getboolean(section, option)
    except ConfigParser.NoOptionError:
        return default

def get_config(section, option, default=None):
    try:
        return CONFIG.get(section, option)
    except ConfigParser.NoOptionError:
        return default

class Ticker(object):
    def __init__(self):
        self.prices = {}
        market_pair = 'USDT-BTC'
        url = 'https://bittrex.com/api/v1.1/public/getticker?market={}'.format(market_pair)
        try:
            btc_ticker = json.loads(urllib2.urlopen(url, timeout=TIMEOUT).read(), parse_float=decimal.Decimal)
            self.btc_price = btc_ticker['result']['Last']
        except:
            self.btc_price = 0
        self.prices['USDT-BTC'] = self.btc_price

    def get_price(self, market_pair):
        if market_pair not in self.prices:
            try:
                ticker = json.loads(
                    urllib2.urlopen(
                        'https://bittrex.com/api/v1.1/public/getticker?market={}'.format(market_pair), 
                        timeout=2).read(),
                    parse_float=decimal.Decimal)
                price = ticker['result']['Last']
            except Exception as e:
                price = 0
            self.prices[market_pair] = price
        
        return self.prices[market_pair]


    def get_line(self, market_pair):
        price = self.get_price(market_pair)
        market, coin = market_pair.split('-')
        dollars = ''
        if market == 'USDT':
            dollars = '$'
        elif get_config_boolean(market_pair, 'display_dollars', False):
            dollars = '$'
            price = price * self.btc_price
        line = {'name' : 'cointicker', 'instance': market_pair+str(price)}
        color = COLOR_WHITE
        decimal_points = get_config_int(market_pair, 'decimal_points')
        precision = '.{}'.format(decimal_points) if decimal_points is not None else ''
        full_text = '{coin} {price:{precision}f}{dollars}'.format(coin=coin, price=price, precision=precision, dollars=dollars)
        limit = get_config_decimal(market_pair, 'limit')
        if limit is not None:
            if price > limit:
                color = COLOR_GREEN
            else:
                color = COLOR_RED
            full_text += ' > {0}{1}'.format(limit, dollars)
        line.update({'full_text': full_text, 'color': color})
        return line

def hook():
    ticker = Ticker()
    for market_pair in reversed(CONFIG.sections()):
        yield ticker.get_line(market_pair)


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
        try:
            for l in hook():
                j.insert(0, l)
        except Exception as e:
            j.insert(0, {'full_text': str(e), 'name' : 'cointicker', 'color': COLOR_RED, 'instance': 'ERROR'})
        # and echo back new encoded json
        print_line(prefix+json.dumps(j))