#!/usr/bin/env python
# -*- encoding:utf-8 -*-

# 10 level data:
# https://app.leverfun.com/timelyInfo/timelyOrderForm?stockCode=600000

# Note
# invalid now.

import logging
from collections import OrderedDict
import json

from common.utils import url_downloader

logger = logging.getLogger(__name__)

BASE_URL = 'https://app.leverfun.com/timelyInfo/timelyOrderForm?stockCode=%s'

HQDATATYPE = OrderedDict((
    ('MCODE', None),
    ('ZQMC', None),
    ('OPEN', None),
    ('PRE', 'preClose'),
    ('NEW', 'match'),
    ('HIGH', None),
    ('LOW', None),
    ('BUYPRICE', None),
    ('SELLPRICE', None),
    ('VOL', None),
    ('MONEY', None),
    ('BUYCOUNT1', 'buyPankou'),
    ('BUYPRICE1', 'buyPankou'),
    ('BUYCOUNT2', 'buyPankou'),
    ('BUYPRICE2', 'buyPankou'),
    ('BUYCOUNT3', 'buyPankou'),
    ('BUYPRICE3', 'buyPankou'),
    ('BUYCOUNT4', 'buyPankou'),
    ('BUYPRICE4', 'buyPankou'),
    ('BUYCOUNT5', 'buyPankou'),
    ('BUYPRICE5', 'buyPankou'),
    ('BUYCOUNT6', 'buyPankou'),
    ('BUYPRICE6', 'buyPankou'),
    ('BUYCOUNT7', 'buyPankou'),
    ('BUYPRICE7', 'buyPankou'),
    ('BUYCOUNT8', 'buyPankou'),
    ('BUYPRICE8', 'buyPankou'),
    ('BUYCOUNT9', 'buyPankou'),
    ('BUYPRICE9', 'buyPankou'),
    ('BUYCOUNT10', 'buyPankou'),
    ('BUYPRICE10', 'buyPankou'),
    ('SELLCOUNT1', 'sellPankou'),
    ('SELLPRICE1', 'sellPankou'),
    ('SELLCOUNT2', 'sellPankou'),
    ('SELLPRICE2', 'sellPankou'),
    ('SELLCOUNT3', 'sellPankou'),
    ('SELLPRICE3', 'sellPankou'),
    ('SELLCOUNT4', 'sellPankou'),
    ('SELLPRICE4', 'sellPankou'),
    ('SELLCOUNT5', 'sellPankou'),
    ('SELLPRICE5', 'sellPankou'),
    ('SELLCOUNT6', 'sellPankou'),
    ('SELLPRICE6', 'sellPankou'),
    ('SELLCOUNT7', 'sellPankou'),
    ('SELLPRICE7', 'sellPankou'),
    ('SELLCOUNT8', 'sellPankou'),
    ('SELLPRICE8', 'sellPankou'),
    ('SELLCOUNT9', 'sellPankou'),
    ('SELLPRICE9', 'sellPankou'),
    ('SELLCOUNT10', 'sellPankou'),
    ('SELLPRICE10', 'sellPankou'),
    ('DATE', None),
    ('TIME', None),
))


def get_hq_data(mcodes, datatypes=None):
    """ HQ 10 level data """
    datatypes = datatypes or list(HQDATATYPE.keys())
    if 'ZQMC' not in datatypes:
        datatypes.insert(0, 'ZQMC')
    if 'MCODE' not in datatypes:
        datatypes.insert(0, 'MCODE')

    data = OrderedDict()
    for m in mcodes:
        code = m[2:]
        url = BASE_URL % code
        response = url_downloader(url)
        if response['data'] is None:
            return []
        res_data = json.loads(response['data'].decode())
        if not res_data['success']:
            logger.warn('%(code)s: %(message)s' % res_data)
        hq_data = res_data['data']
        print(hq_data)
        stock_data = OrderedDict()
        for dt in datatypes:
            k = HQDATATYPE.get(dt)
            if dt == 'MCODE':
                stock_data['MCODE'] = m.upper()
            if k is None:
                stock_data[dt] = None
            elif k == 'buyPankou':
                idx = int(dt[8:]) - 1
                if dt[3:8] == 'PRICE':
                    stock_data[dt] = hq_data[k][idx]['price'] or None
                else:
                    stock_data[dt] = hq_data[k][idx]['volume']
            elif k == 'sellPankou':
                idx = int(dt[9:]) - 1
                if dt[4:9] == 'PRICE':
                    stock_data[dt] = hq_data[k][idx]['price'] or None
                else:
                    stock_data[dt] = hq_data[k][idx]['volume']
            else:
                stock_data[dt] = hq_data[k]
        data[stock_data['MCODE']] = stock_data
    return data


def add_arguments(parser):
    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument('--quote', action='store_true', help='10 level price of buy/sell')
    parser.add_argument('mcode', nargs='+', help='stock code with market. such as SZ000002')


def exec_args(args):
    from rsttable import RstTable

    hq_data = get_hq_data(args.mcode)
    table = [list(list(hq_data.values())[0].keys())]
    for data in list(hq_data.values()):
        table.extend([list(data.values())])
    print(RstTable(table).table())
