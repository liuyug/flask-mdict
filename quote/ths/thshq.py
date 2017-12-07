#!/usr/bin/env python
# -*- encoding:utf-8 -*-

import os.path
import glob
import json
import datetime
from collections import OrderedDict

from bs4 import BeautifulSoup
import six
from six.moves.configparser import ConfigParser, ParsingError

from common.utils import url_downloader
from .config import ths_dir, HQDATATYPE


class Datatype(object):
    _datatype = None

    def __init__(self, data=None, datafile=None):
        if data:
            self._datatype = data
        elif datafile:
            self._datatype = json.load(open(datafile), object_pairs_hook=OrderedDict)
        else:
            self._datatype = []

    def __getitem__(self, name):
        name = name.upper()
        for item in self._datatype:
            if name == item['id']:
                return item['name']
            elif name == item['name']:
                return item['id']
        return name

    def getName(self, name):
        name = name.upper()
        for item in self._datatype:
            if name == item['id']:
                return item['name']
        return name

    def getDesc(self, name):
        name = name.upper()
        for item in self._datatype:
            if name == item['id'] or name == item['name']:
                return item['desc']
        return name

    def getType(self, name):
        name = name.upper()
        for item in self._datatype:
            if name == item['id'] or name == item['name']:
                return item['type']
        return name

    def getDatatype(self, name=None):
        if not name:
            return self._datatype
        name = name.upper()
        for item in self._datatype:
            if name == item['id'] or name == item['name']:
                return item
        return name


class SystemConfig(object):
    _encoding = 'gbk'
    _datatype = None

    def __init__(self, ths_dir):
        if six.PY3:
            config = ConfigParser(strict=False)
        else:
            config = ConfigParser()
        self._datatype = []
        if not os.path.exists(ths_dir):
            print('Not exists THS directory: "%s"' % ths_dir)
            return
        cfg_path = glob.glob('%s/system/同花顺方案/hexin.ini' % ths_dir)
        try:
            for path in cfg_path:
                with open(path, 'rb') as f:
                    text = f.read()
                    config.readfp(six.StringIO(text.decode(self._encoding)))
        except ParsingError:
            pass
        for k, v in config.items(u'数据项目', raw=True):
            s2 = v[0].split(',')
            name = s2[1].upper()
            desc = '/'.join(s2[2:]).strip('/')
            dt = OrderedDict()
            dt['id'] = k
            dt['type'] = s2[0]
            dt['name'] = name
            dt['desc'] = desc
            self._datatype.append(dt)
        self._datatype.sort(key=lambda x: int(x['id']))

    def datatype(self):
        return Datatype(data=self._datatype)

    def printDatatype(self, encoding='utf8'):
        for dt in self._datatype:
            print(('%(id)s %(type)s %(name)s %(desc)s' % dt).encode(encoding))

    def writeDatatype(self, filename='datatype.json'):
        json.dump(self._datatype, open(filename, 'w'))


class UserConfig(object):
    _encoding = 'gbk'
    _config = None

    def __init__(self, ths_dir):
        self._config = ConfigParser()
        if not os.path.exists(ths_dir):
            print('Not exists THS directory: "%s"' % ths_dir)
            return
        cfg_path = glob.glob('%s/*/hexin.ini' % ths_dir)
        try:
            for path in cfg_path:
                with open(path, 'rb') as f:
                    text = f.read()
                    self._config.readfp(six.StringIO(text.decode(self._encoding)))
        except ParsingError:
            pass

    def _get_host(self, ths_host):
        return ths_host.partition(':')[0]

    def _get_port(self, ths_host):
        return int(ths_host.partition(';')[0].rpartition(':')[-1])

    def getHQHosts(self):
        hosts = []
        for name, host in self._config.items('HQ_Server_List_pass', raw=True):
            hosts.append(
                {
                    'desc': name,
                    'ipaddress': self._get_host(host),
                    'port': self._get_port(host),
                }
            )
        return hosts

    def getPrimaryHQHost(self):
        cur_host = self._config.get('NEW_HQ_SERVER', 'cur_server_pass')
        host = self._config.get('HQ_Server_List_pass', cur_host).partition(';')[0]
        return {
            'desc': cur_host,
            'ipaddress': self._get_host(host),
            'port': self._get_port(host),
        }

    def writeHQHost(self, filename='hqhost.json'):
        hosts = self.getHQHosts()
        host = self.getPrimaryHQHost()
        data = {
            'hosts': hosts,
            'default': host,
        }
        json.dump(data, open(filename, 'w'))


class ThsHq(object):
    _encoding = 'gbk'
    _datatype = None
    _market = {
        'SH': '17',
        'SZ': '33',
        '17': 'SH',
        '33': 'SZ',
    }
    _base_format = 'http://%s:%s/hexin'
    _base_url = None
    _hq_server = None

    def __init__(self, datatype=None):
        self._hq_server = ['', '']
        self._datatype = datatype or Datatype()

    def min_to_time(self, value):
        total_min = float(value)
        # idle 90min at noon
        if total_min > 121:
            total_min += 90
        # calcuate from 9 o'clock
        total_min += 30
        hour = 9 + total_min / 60
        minute = total_min % 60
        return '%02d:%02d:00' % (hour, minute)

    def get_hq_server(self):
        return self._hq_server

    def connect(self, ip=None, port=None):
        self._hq_server[0] = ip or self._hq_server[0]
        self._hq_server[1] = port or self._hq_server[1]
        self._base_url = self._base_format % tuple(self._hq_server)

    def disconnect(self):
        pass

    def getMarket(self):
        """ 1．市场信息 """
        data = {
            'method': 'market',
        }
        response = url_downloader(self._base_url, data=data)
        xml_data = response['data']
        soup = BeautifulSoup(xml_data, 'html5lib', from_encoding=self._encoding)
        # soup = BeautifulSoup(xml_data, 'lxml', from_encoding=self._encoding)
        market = {}
        for item in soup.find_all('item'):
            market[item['id']] = item.contents[0].string
        return market

    def getStock(self, markets=None):
        """ get all stock code by market """
        markets = markets or ['SH', 'SZ']
        data = {
            'method': 'market',
            'codelist': ';'.join([self._market[m.upper()] for m in markets]),
            'append': 'p',
        }
        response = url_downloader(self._base_url, data=data)
        xml_data = response['data']
        soup = BeautifulSoup(xml_data, 'html5lib', from_encoding=self._encoding)
        # soup = BeautifulSoup(xml_data, 'lxml', from_encoding=self._encoding)
        data = {}
        for item in soup.find_all('py'):
            if item.string:
                stock = item.string.split('|')
                market = self._market.get(stock[3])
                if market not in markets:
                    continue
                if stock[0] in data:
                    data[stock[0]]['abbr'] += (';' + stock[2])
                else:
                    data[stock[0]] = {
                        'code': stock[0],
                        'name': stock[1],
                        'abbr': stock[2],
                        'market': market,
                    }
        return sorted(data.values(), key=lambda x: x['code'])

    def getHQ(self, mcodes, datatypes=None):
        """ 2．行情数据 """
        if not datatypes:
            datatypes = HQDATATYPE
        datatypes = [d.upper() for d in datatypes]
        if 'MCODE' not in datatypes:
            datatypes.insert(0, 'MCODE')
        req_datatypes = []
        for d in datatypes:
            if d == 'MCODE':
                d = 'CODE'
            elif d == 'TIME':
                d = 'FROMOPEN'
            req_datatypes.append(d)

        codes = [m[2:] for m in mcodes]
        data = {
            'method': 'quote',
            'code': ';'.join(codes),
            'datatype': ','.join(req_datatypes),
            'datetime': '0(0-0)',
        }
        response = url_downloader(self._base_url, data=data)
        xml_data = response['data']
        soup = BeautifulSoup(xml_data, 'html5lib', from_encoding=self._encoding)
        # soup = BeautifulSoup(xml_data, 'lxml', from_encoding=self._encoding)
        # print(xml_data.decode(self._encoding))
        StockIndex = {}
        for index in soup.find_all('stockindex'):
            StockIndex[index['id']] = index['name']

        hq_list = []
        for DataResult in soup.find_all('dataresult'):
            dr = OrderedDict([[m.upper(), ''] for m in mcodes])
            codeindex = DataResult.find('codeindex')
            for record in DataResult.find_all('record'):
                stock_data = OrderedDict([[dt, None] for dt in datatypes])
                for item in record.find_all('item'):
                    value = item.contents[0].string
                    name = StockIndex.get(item['id']) or    \
                        self._datatype.getName(item['id']) or   \
                        item['id']
                    # desc = self._datatype.getDesc(name)
                    if name == 'CODE':
                        value = self._market.get(item['market']) + value
                        stock_data['MCODE'] = value
                    elif name == 'FROMOPEN':
                        stock_data['TIME'] = self.min_to_time(value)
                    elif name == 'DATE':
                        stock_data['DATE'] = datetime.date.today().isoformat()
                    elif name == 'ZQMC':
                        stock_data[name] = value
                    else:
                        stock_data[name] = None if value is None else abs(float(value))
                if codeindex:
                    stock_data['MCODE'] = self._market.get(codeindex['market']) \
                        + codeindex['code']
                if 'OPEN' in stock_data and not stock_data['OPEN'] and 'PRE' in stock_data:
                    stock_data['NEW'] = stock_data['PRE']
                dr[stock_data['MCODE']] = stock_data
            hq_list.append(dr)
        return hq_list

    def getQuoteSort(self):
        """ 3．排名数据 """
        raise NotImplementedError

    def getQuoteSelect(self):
        """ 4．选股请求 """
        raise NotImplementedError


def add_arguments(parser):
    parser.add_argument('--directory', dest='ths_dir', default=ths_dir, help='THS Software directory')

    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument('--make-config', action='store_true', help='Make a config file for Web Server')
    group.add_argument('--host', action='store_true', help='All THS HQ Hosts')
    group.add_argument('--datatype', action='store_true', help='All THS Functions.')
    group.add_argument('--market', action='store_true', help='catch market')
    group.add_argument('--stock', action='store_true', help='catch SH&SZ stock code')
    group.add_argument('--quote', action='store_true', help='HQ data with hq-datatype')
    parser.add_argument('--hq-datatype', required=False, help='HQ datatype')
    parser.add_argument('--output', required=False, help='output to csv file')
    parser.add_argument('mcode', nargs='*', help='Stock code, SH600000')


def exec_args(args):
    from rsttable import RstTable

    thscfg = UserConfig(args.ths_dir)
    syscfg = SystemConfig(args.ths_dir)
    host = thscfg.getPrimaryHQHost()
    ip = args.host or host['ipaddress']
    port = 80
    datatype = syscfg.datatype()

    if args.make_config:
        if not args.output:
            print('Please input config filename')
            return

        host = thscfg.getPrimaryHQHost()
        data = {
            'current_host': thscfg.getPrimaryHQHost(),
            'hosts': thscfg.getHQHosts(),
            'datatype': syscfg.datatype().getDatatype(),
        }
        json.dump(data, open(args.output, 'w'))
        return
    if args.host:
        hosts = thscfg.getHQHosts()
        host = thscfg.getPrimaryHQHost()
        hosts_table = [('%s ' % x + '%(desc)s %(ipaddress)s %(port)s' % hosts[x]).split(' ') for x in range(len(hosts))]
        print(RstTable(hosts_table, header=False).table())
        print((u'\nDefault host: %(desc)s %(ipaddress)s' % host))
        return
    if args.datatype:
        datatype = syscfg.datatype()
        data = [list(datatype.getDatatype()[0].keys())]
        data.extend([list(dt.values()) for dt in datatype.getDatatype()])
        table = RstTable(data)
        if args.output:
            table.csv(args.output)
        else:
            print(table.table())
        return

    thshq = ThsHq(datatype)
    thshq.connect(ip, port)
    if args.market:
        markets = thshq.getMarket()
        table = [[k, v] for k, v in markets.items()]
        print(RstTable(table, header=False).table())
        return
    if args.stock:
        stocks = thshq.getStock()
        if args.output:
            json.dump(stocks, open(args.output, 'w'))
        else:
            data = [stock.values() for stock in stocks]
            table = RstTable(data, header=False)
            print(table.table())
        return
    if args.quote:
        if args.hq_datatype:
            datatype = args.hq_datatype.split(',')
        else:
            datatype = HQDATATYPE
        hq_datas = thshq.getHQ(args.mcode, datatype)
        for hq_data in hq_datas:
            table = [list(list(hq_data.values())[0].keys())]
            for data in list(hq_data.values()):
                table.extend([list(data.values())])
            print(RstTable(table).table())
        return


def tester():
    import argparse

    parser = argparse.ArgumentParser(description='THS HQ Online')
    add_arguments(parser)
    args = parser.parse_args()
    exec_args(args)


if __name__ == '__main__':
    tester()
