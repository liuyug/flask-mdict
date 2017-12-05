#!/usr/bin/env python
# -*- encoding:utf-8 -*-

import os.path
import datetime
from collections import OrderedDict

from ctypes import create_string_buffer, \
    byref, c_char_p, c_byte, c_short

import six
from six.moves.configparser import ConfigParser
from .config import HQDATATYPE, tdx_dir

from .tdxhqapi import TdxHq_Connect, TdxHq_Disconnect,  \
    TdxHq_GetSecurityCount, TdxHq_GetSecurityList, TdxHq_GetSecurityBars,   \
    TdxHq_GetIndexBars, TdxHq_GetMinuteTimeData,    \
    TdxHq_GetHistoryMinuteTimeData, TdxHq_GetTransactionData,   \
    TdxHq_GetHistoryTransactionData, TdxHq_GetSecurityQuotes,   \
    TdxHq_GetCompanyInfoCategory, TdxHq_GetCompanyInfoContent,  \
    TdxHq_GetXDXRInfo, TdxHq_GetFinanceInfo


class TdxHq(object):
    """ HQ data delay about 30 second """
    _encoding = 'gbk'
    _market = {
        'SZ': 0,
        'SH': 1,
        0: 'SZ',
        1: 'SH',
        '0': 'SZ',
        '1': 'SH',

    }
    _k_category = {
        '5min': 0,
        '15min': 1,
        '30min': 2,
        '60min': 3,
        'day': 4,
        'week': 5,
        'month': 6,
        '1min': 7,
        '1min2': 8,
        'day2': 9,
        'quarter': 10,
        'year': 11,
    }
    _result = None
    _err = None
    _is_connected = False
    _hq_server = None

    def __init__(self):
        self._result = create_string_buffer(1024 * 1024)
        self._err = create_string_buffer(256)
        self._hq_server = ['', '']

    def __del__(self):
        self.disconnect()

    def to_byte(self, buff):
        return buff.encode(self._encoding)

    def to_string(self, buff):
        return buff.decode(self._encoding)

    def to_table(self, buff):
        return [row.split('\t') for row in self.to_string(buff).split('\n')]

    def format_time(self, time_stamp):
        time = time_stamp[:-6] + ':'
        if int(time_stamp[-6:-4]) < 60:
            time += '%s:' % time_stamp[-6:-4]
            time += '%06.3f' % (
                int(time_stamp[-4:]) * 60 / 10000.0
            )
        else:
            time += '%02d:' % (
                int(time_stamp[-6:]) * 60 / 1000000
            )
            time += '%06.3f' % (
                (int(time_stamp[-6:]) * 60 % 1000000) * 60 / 1000000.0
            )
        return time

    def is_connected(self):
        return self._is_connected

    def get_result(self):
        return self.to_table(self._result.value)

    def get_error(self):
        return self.to_string(self._err.value)

    def get_hq_server(self):
        return self._hq_server

    def connect(self, ip=None, port=None):
        """ 连接通达信行情服务器, 在券商通达信软件登录界面“通讯设置”按钮内查得"""
        self._hq_server[0] = ip or self._hq_server[0]
        self._hq_server[1] = port or self._hq_server[1]

        ip = self.to_byte(self._hq_server[0])
        port = self._hq_server[1]
        self._is_connected = TdxHq_Connect(ip, port, self._result, self._err)
        return self._is_connected

    def disconnect(self):
        """ 断开同服务器的连接 """
        TdxHq_Disconnect()
        self._is_connected = False

    def getSecurityCount(self, market):
        """ 获取市场内所有证券的数量 """
        count = c_short()
        market = self._market.get(market.upper())
        TdxHq_GetSecurityCount(market, byref(count), self._err)
        return count.value

    def getSecurityList(self, market, start, count):
        """ 获取市场内某个范围内的1000支股票的股票代码 """
        count = c_short(count)
        market = self._market.get(market.upper())
        return TdxHq_GetSecurityList(
            market, start, byref(count), self._result, self._err)

    def getSecurityBars(self, category, market, code, start, count):
        """ 获取证券指定范围的的K线数据 """
        category = self._k_category.get(category.lower(), 'day')
        market = self._market.get(market.upper())
        count = c_short(count)
        code = self.to_byte(code)
        return TdxHq_GetSecurityBars(
            category, market, code, start, byref(count),
            self._result, self._err)

    def getIndexBars(self, category, market, code, start, count):
        """ 获取指数的指定范围内K线数据 """
        category = self._k_category.get(category.lower(), 'day')
        market = self._market.get(market.upper())
        count = c_short(count)
        code = self.to_byte(code)
        return TdxHq_GetIndexBars(
            category, market, code, start, byref(count),
            self._result, self._err)

    def getMinuteTimeData(self, market, code):
        """ 获取分时数据 """
        market = self._market.get(market.upper())
        code = self.to_byte(code)
        return TdxHq_GetMinuteTimeData(market, code, self._result, self._err)

    def getHistoryMinuteTimeData(self, market, code, date):
        """ 获取历史分时数据 """
        market = self._market.get(market.upper())
        code = self.to_byte(code)
        return TdxHq_GetHistoryMinuteTimeData(
            market, code, date, self._result, self._err)

    def getTransactionData(self, market, code, start, count):
        """ 获取分时成交某个范围内的数据 """
        market = self._market.get(market.upper())
        code = self.to_byte(code)
        count = c_short(count)
        return TdxHq_GetTransactionData(
            market, code, start, count, self._result, self._err)

    def getHistoryTransactionData(self, market, code, start, count, date):
        """ 获取历史分时成交某个范围内的数据 """
        market = self._market.get(market.upper())
        code = self.to_byte(code)
        count = c_short(count)
        return TdxHq_GetHistoryTransactionData(
            market, code, start, count, date, self._result, self._err)

    def getSecurityQuotes(self, markets, codes, count):
        """ 批量获取多个证券的五档报价数据 """
        markets_ = (c_byte * count)()
        codes_ = (c_char_p * count)()
        for x in range(count):
            markets_[x] = self._market.get(markets[x].upper())
            codes_[x] = self.to_byte(codes[x])
        count = c_short(count)
        return TdxHq_GetSecurityQuotes(
            markets_, codes_, count, self._result, self._err)

    def get_hq_data(self, mcodes, datatypes=None):
        datatypes = datatypes or list(HQDATATYPE.keys())
        if 'ZQMC' not in datatypes:
            datatypes.insert(0, 'ZQMC')
        if 'MCODE' not in datatypes:
            datatypes.insert(0, 'MCODE')

        markets = [m[:2] for m in mcodes]
        codes = [m[2:] for m in mcodes]
        data = OrderedDict()
        ret = self.getSecurityQuotes(markets, codes, len(mcodes))
        if not ret:
            self.disconnect()
            return data
        result = self.get_result()
        for row in result[1:]:
            mcode = self._market.get(row[0]) + row[1]
            stock_data = OrderedDict()
            print(row)
            for dt in datatypes:
                dt = dt.upper()
                idx = HQDATATYPE.get(dt)
                if idx is None:
                    stock_data[dt] = None
                elif dt == 'MCODE':
                    stock_data['MCODE'] = mcode
                elif dt == 'DATE':
                    stock_data['DATE'] = datetime.date.today().isoformat()
                elif dt == 'TIME':
                    stock_data['TIME'] = self.format_time(row[idx])
                elif dt == 'ZQMC':
                    stock_data[dt] = row[idx]
                else:
                    stock_data[dt] = None if row[idx] == '0.000000' else float(row[idx])
            data[mcode] = stock_data
        return data

    def getCompanyInfoCategory(self, market, code):
        """ 获取F10资料的分类 """
        market = self._market.get(market.upper())
        code = self.to_byte(code)
        return TdxHq_GetCompanyInfoCategory(
            market, code, self._result, self._err)

    def getCompanyInfoContent(self, market, code, filename, start, length):
        """ 获取F10资料的某一分类的内容 """
        market = self._market.get(market.upper())
        code = self.to_byte(code)
        filename = self.to_byte(filename)
        return TdxHq_GetCompanyInfoContent(
            market, code, filename, start, length, self._result, self._err)

    def getXDXRInfo(self, market, code):
        """ 获取除权除息信息 """
        market = self._market.get(market.upper())
        code = self.to_byte(code)
        return TdxHq_GetXDXRInfo(market, code, self._result, self._err)

    def getFinanceInfo(self, market, code):
        """ 获取财务信息 """
        market = self._market.get(market.upper())
        code = self.to_byte(code)
        return TdxHq_GetFinanceInfo(market, code, self._result, self._err)


class TdxConfig(object):
    _encoding = 'gbk'
    _hqhost = None

    def __init__(self, tdx_dir='C:\\new_tdx'):
        cfg_path = os.path.join(tdx_dir, 'connect.cfg')
        if not os.path.exists(cfg_path):
            raise OSError('could not find file: %s' % cfg_path)
        config = ConfigParser()
        with open(cfg_path, 'rb') as f:
            text = f.read()
            config.readfp(six.StringIO(text.decode(self._encoding)))
        self._hqhost = dict(config.items('HQHOST'))

    def getHQHosts(self):
        hosts = []
        for x in range(1, int(self._hqhost['hostnum']) + 1):
            hosts.append(
                {
                    'desc': self._hqhost.get('hostname%02d' % x),
                    'ipaddress': self._hqhost.get('ipaddress%02d' % x),
                    'port': int(self._hqhost.get('port%02d' % x)),
                }
            )
        return hosts

    def getPrimaryHQHost(self):
        x = int(self._hqhost.get('primaryhost', '0'))
        return {
            'desc': self._hqhost.get('hostname%02d' % x),
            'ipaddress': self._hqhost.get('ipaddress%02d' % x),
            'port': int(self._hqhost.get('port%02d' % x)),
        }


def test(mcodes):
    tdxcfg = TdxConfig()
    host = tdxcfg.getPrimaryHQHost()
    ip = host['ipaddress']
    port = host['port']

    tdxhq = TdxHq()
    print(tdxhq.connect(ip, port))

    print('Test function: getSecurityCount and getSecurityList')
    try:
        print('SZ Security Count: %s' % tdxhq.getSecurityCount('sz'))
        print('SH Security Count: %s' % tdxhq.getSecurityCount('sh'))
        # Invalid? The connection will be disconnect...
        tdxhq.getSecurityList('SZ', 0, 0)
    except Exception as err:
        print(err)
        print('connect again...')
        print(tdxhq.connect(ip, port))

    markets = [mcode[:2] for mcode in mcodes]
    codes = [mcode[2:] for mcode in mcodes]

    # print(tdxhq.getSecurityBars('1min', 'sh', '600036', 0, 10))
    # print(tdxhq.getIndexBars('day', 'sh', '000001', 0, 10))
    # print(tdxhq.getMinuteTimeData('sz', '000002'))
    # print(tdxhq.getHistoryMinuteTimeData('sz', '000002', 20150525))
    # print(tdxhq.getTransactionData('sz', '000002', 0, 10))
    # print(tdxhq.getHistoryTransactionData('sz', '000002', 0, 10, 20150525))
    print(tdxhq.getSecurityQuotes(markets, codes, len(codes)))
    # c = tdxhq.getCompanyInfoCategory('sh', '600036')
    # print(c)
    # print(tdxhq.getCompanyInfoContent('sh', '600036', c[1][1], int(c[1][2]), int(c[1][3])))
    # print(tdxhq.getXDXRInfo('sz', '000002'))
    # print(tdxhq.getFinanceInfo('sz', '000002'))


def add_arguments(parser):
    group = parser.add_mutually_exclusive_group(required=True)
    parser.add_argument('--directory', dest='tdx_dir', default=tdx_dir, help='THS Software directory')
    group.add_argument('--host', action='store_true', help='HQ Hosts')
    group.add_argument('--finance', action='store_true', help='Finance Info')
    group.add_argument('--quote', action='store_true', help='five level price of buy/sell')
    group.add_argument('--xdxr', action='store_true', help='XD/XR Info')
    group.add_argument('--company', type=int, help='Company information')
    group.add_argument('--test', action='store_true', help='Test tdxhq function.')
    parser.add_argument('mcode', nargs='*', help='stock code with market. such as SZ000002')
    return parser


def exec_args(args):
    from rsttable import RstTable

    if args.test:
        test(args.mcode)
        return

    tdxcfg = TdxConfig(args.tdx_dir)
    hosts = tdxcfg.getHQHosts()
    host = tdxcfg.getPrimaryHQHost()
    if args.host:
        hosts_table = [('%s ' % x + '%(desc)s %(ipaddress)s %(port)s' % hosts[x]).split(' ') for x in range(len(hosts))]
        print(RstTable(hosts_table, header=False).table())
        print((u'\nDefault host: %(desc)s %(ipaddress)s' % host))
        return

    ip = host['ipaddress']
    port = host['port']

    tdxhq = TdxHq()
    tdxhq.connect(ip, port)
    data = tdxhq.get_result()
    print('connect to %(ipaddress)s:%(port)s' % host)
    print(RstTable(data).table())

    if args.finance:
        for code in args.mcode:
            tdxhq.getFinanceInfo(code[:2], code[2:])
            data = tdxhq.get_result()
            print(RstTable(data).table())
    elif args.xdxr:
        for code in args.mcode:
            tdxhq.getXDXRInfo(code[:2], code[2:])
            data = tdxhq.get_result()
            print(RstTable(data).table())
    elif args.company is not None:
        x = args.company
        for code in args.mcode:
            tdxhq.getCompanyInfoCategory(code[:2], code[2:])
            category = tdxhq.get_result()
            if x < 1:
                cdata = [[str(c), category[c][0]] for c in range(len(category))]
                print(RstTable(cdata).table())
                break
            tdxhq.getCompanyInfoContent(
                code[:2], code[2:],
                category[x][1], int(category[x][2]), int(category[x][3]),
            )
            data = tdxhq.get_result()
            print(data)
    elif args.quote:
        markets = [code[:2] for code in args.mcode]
        codes = [code[2:] for code in args.mcode]
        tdxhq.getSecurityQuotes(markets, codes, len(codes))
        data = tdxhq.get_result()
        print(RstTable(data).table())


def main():
    import argparse

    parser = argparse.ArgumentParser(description='Stock search with tdxhq.dll.')
    parser = add_arguments(parser)
    args = parser.parse_args()
    exec_args(args)


if __name__ == '__main__':
    main()
