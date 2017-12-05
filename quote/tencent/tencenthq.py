#!/usr/bin/env python
# -*- encoding:utf-8 -*-

# stock data:
# http://qt.gtimg.cn/q=sh600000,sz000002

from collections import OrderedDict

from common.utils import url_downloader

BASE_URL = 'http://qt.gtimg.cn/q=%s'

HQDATATYPE = OrderedDict((
    ('MCODE', 0),
    ('ZQMC', 1),
    ('OPEN', 5),
    ('PRE', 4),
    ('NEW', 3),
    ('HIGH', 33),
    ('LOW', 34),
    ('BUYPRICE', 9),
    ('SELLPRICE', 19),
    ('VOL', 36),
    ('MONEY', 37),
    ('BUYCOUNT1', 10),
    ('BUYPRICE1', 9),
    ('BUYCOUNT2', 12),
    ('BUYPRICE2', 11),
    ('BUYCOUNT3', 14),
    ('BUYPRICE3', 13),
    ('BUYCOUNT4', 16),
    ('BUYPRICE4', 15),
    ('BUYCOUNT5', 18),
    ('BUYPRICE5', 17),
    ('SELLCOUNT1', 20),
    ('SELLPRICE1', 19),
    ('SELLCOUNT2', 22),
    ('SELLPRICE2', 21),
    ('SELLCOUNT3', 24),
    ('SELLPRICE3', 23),
    ('SELLCOUNT4', 26),
    ('SELLPRICE4', 25),
    ('SELLCOUNT5', 28),
    ('SELLPRICE5', 27),
    ('DATE', 30),
    ('TIME', 30),
))


def get_market(market):
    if market == '51':
        return 'SZ'
    elif market == '1':
        return 'SH'


def get_hq_data(mcodes, datatypes=None):
    """ Tencent HQ data """
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
        data_list = line.partition('=')[2][1:-2].split('~')
        stock_data = OrderedDict()

        for dt in datatypes:
            dt = dt.upper()
            idx = HQDATATYPE.get(dt)
            if idx is None:
                stock_data[dt] = None
            elif dt == 'MCODE':
                stock_data['MCODE'] = get_market(data_list[0]) + data_list[2]
            elif dt == 'DATE':
                date = data_list[idx][:-6]
                stock_data['DATE'] = '%s-%s-%s' % (date[:4], date[4:6], date[6:])
            elif dt == 'TIME':
                time = data_list[idx][-6:]
                stock_data['TIME'] = '%s:%s:%s' % (time[:2], time[2:4], time[4:])
            elif dt == 'ZQMC':
                stock_data[dt] = data_list[idx]
            else:
                stock_data[dt] = None if data_list[idx] == '0.00' else float(data_list[idx])
        data[stock_data['MCODE']] = stock_data
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
