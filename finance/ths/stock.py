#!/usr/bin/env python
# -*- encoding:utf-8 -*-

import os.path
import logging

from six.moves.configparser import ConfigParser

from .config import ths_dir


logger = logging.getLogger(__name__)


def create_market_from_local():
    def parse_codelist(codelist):
        codes = []
        for cl in codelist.split(','):
            if not cl:
                continue
            if '-' in cl:
                b, e = cl.split('-')
                length = len(b)
                for pos in range(0, length):
                    if b[pos] != e[pos]:
                        break
                    pos += 1
                assert(pos < length)
                h = b[:pos]
                b, e = int(b[pos:]), int(e[pos:])
                fmt = '%%s%%0%dd' % (length - pos)
                for x in range(b, e + 1):
                    codes.append(fmt % (h, x))
            else:
                codes.append(cl)
        return codes

    market_path = os.path.join(ths_dir, 'realtime', 'market.txt')
    if not os.path.exists(market_path):
        raise TypeError('could not find file: %s' % market_path)
    market_config = ConfigParser()
    market_config.read(market_path)

    market = []
    for i in range(market_config.getint('Market', 'Total')):
        market_num = market_config.get('Market', 'Market%s' % i)
        market = 'Market_%s' % market_num
        fullname = market_config.get(market, 'FullName').decode('gbk')
        for stocktype_num in market_config.get(market, 'StockType').split(';'):
            if not stocktype_num:
                continue
            stocktype_sec = 'Market_%s_%s' % (market_num, stocktype_num)
            typename = market_config.get(stocktype_sec, 'TypeName').decode('gbk')
            if market_config.has_option(stocktype_sec, 'CodeList'):
                codelist = parse_codelist(
                    market_config.get(stocktype_sec, 'CodeList'))
            else:
                codelist = []
            logging.debug(
                '[%s - %s][%s - %s]: %d' % (
                    market_num, fullname,
                    stocktype_num, typename,
                    len(codelist)
                )
            )
            market.append((stocktype_num, typename, codelist))
    return market


def create_stock_from_local():
    def parse_codelist(codelist):
        codes = []
        for cl in codelist.split(','):
            if not cl:
                continue
            if '-' in cl:
                b, e = cl.split('-')
                b, e = int(b), int(e)
                for x in range(b, e + 1):
                    codes.append('%06d' % x)
            else:
                codes.append(cl)
        return codes

    stock = {}
    market_path = os.path.join(ths_dir, 'realtime', 'market.txt')
    if not os.path.exists(market_path):
        raise TypeError('could not find file: %s' % market_path)
    market_config = ConfigParser()
    market_config.read(market_path)

    for i in range(market_config.getint('Market', 'Total')):
        market_num = market_config.get('Market', 'Market%s' % i)
        market = 'Market_%s' % market_num
        fullname = market_config.get(market, 'FullName').decode('gbk')
        stockname_file = 'stockname_%s_0.txt' % market_num
        logger.debug('%s - %s - %s' % (market, fullname, stockname_file))
        for stocktype_num in market_config.get(market, 'StockType').split(';'):
            if not stocktype_num:
                continue
            stocktype_sec = 'Market_%s_%s' % (market_num, stocktype_num)
            typename = market_config.get(stocktype_sec, 'TypeName').decode('gbk')
            stock_sec = 'name_%s_%s' % (market_num, stocktype_num)
            logger.debug('%s %s %s' % (stocktype_sec, typename, stock_sec))
            codes = []
            if market_config.has_option(stocktype_sec, 'CodeList'):
                codelist = parse_codelist(
                    market_config.get(stocktype_sec, 'CodeList'))
                stockname_path = os.path.join(
                    ths_dir, 'stockname', stockname_file)
                stock_config = ConfigParser()
                stock_config.read(stockname_path)
                for code in codelist:
                    try:
                        name = stock_config.get(stock_sec, code) or ''
                        name = name.decode('gbk')
                    except Exception:
                        logging.warn('Could not find stock code: %s' % code)
                    codes.append((code, name))
                print('Add %s: %d' % (typename, len(codelist)))
            stock[typename] = codes
    return stock
