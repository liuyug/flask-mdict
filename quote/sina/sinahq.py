#!/usr/bin/env python
# -*- encoding:utf-8 -*-

# stock data:
# http://hq.sinajs.cn/list=sh601003,sh601001

from collections import OrderedDict

from common.utils import url_downloader

BASE_URL = 'http://hq.sinajs.cn/list=%s'

HQDATATYPE = OrderedDict((
    ('MCODE', -1),
    ('ZQMC', 0),
    ('OPEN', 1),
    ('PRE', 2),
    ('NEW', 3),
    ('HIGH', 4),
    ('LOW', 5),
    ('BUYPRICE', 6),
    ('SELLPRICE', 7),
    ('VOL', 8),
    ('MONEY', 9),
    ('BUYCOUNT1', 10),
    ('BUYPRICE1', 11),
    ('BUYCOUNT2', 12),
    ('BUYPRICE2', 13),
    ('BUYCOUNT3', 14),
    ('BUYPRICE3', 15),
    ('BUYCOUNT4', 16),
    ('BUYPRICE4', 17),
    ('BUYCOUNT5', 18),
    ('BUYPRICE5', 19),
    ('SELLCOUNT1', 20),
    ('SELLPRICE1', 21),
    ('SELLCOUNT2', 22),
    ('SELLPRICE2', 23),
    ('SELLCOUNT3', 24),
    ('SELLPRICE3', 25),
    ('SELLCOUNT4', 26),
    ('SELLPRICE4', 27),
    ('SELLCOUNT5', 28),
    ('SELLPRICE5', 29),
    ('DATE', 30),
    ('TIME', 31),
))


def get_kchart_urls(mcode):
    return {
        'm1': 'http://image.sinajs.cn/newchart/min/n/%s.gif' % mcode.lower(),
        'd1': 'http://image.sinajs.cn/newchart/daily/n/%s.gif' % mcode.lower(),
        'd7': 'http://image.sinajs.cn/newchart/weekly/n/%s.gif' % mcode.lower(),
        'd30': 'http://image.sinajs.cn/newchart/monthly/n/%s.gif' % mcode.lower(),
    }


def get_hq_data(mcodes, datatypes=None):
    """ HQ data delay about 10 second """
    datatypes = datatypes or list(HQDATATYPE.keys())
    if 'ZQMC' not in datatypes:
        datatypes.insert(0, 'ZQMC')
    if 'MCODE' not in datatypes:
        datatypes.insert(0, 'MCODE')

    encoding = 'gbk'
    url = BASE_URL % ','.join(mcodes).lower()
    response = url_downloader(url)
    if not response['data']:
        return []
    data = OrderedDict()
    for line in response['data'].decode(encoding).split('\n'):
        line.strip()
        if not line:
            continue
        pos = line.index('=')
        mcode = line[pos - 8: pos].upper()
        data_list = line[pos + 2: -2].split(',')
        stock_data = OrderedDict()

        for dt in datatypes:
            dt = dt.upper()
            idx = HQDATATYPE.get(dt)
            if idx is None:
                stock_data[dt] = None
            elif dt == 'MCODE':
                stock_data['MCODE'] = mcode
            elif dt in ['ZQMC', 'DATE', 'TIME']:
                stock_data[dt] = data_list[idx]
            else:
                stock_data[dt] = None if data_list[idx] == '0.000' else float(data_list[idx])
        data[mcode] = stock_data
    return data


def add_arguments(parser):
    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument('--quote', action='store_true', help='five level price of buy/sell')
    parser.add_argument('mcode', nargs='+', help='stock code with market. such as SZ000002')


def exec_args(args):
    from rsttable import RstTable

    hq_data = get_hq_data(args.mcode)
    table = [list(list(hq_data.values())[0].keys())]
    for data in list(hq_data.values()):
        table.extend([list(data.values())])
    print(RstTable(table).table())
