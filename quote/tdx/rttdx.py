#!/usr/bin/env python
# -*- encoding:utf-8 -*-

import logging
from datetime import date
import sys

if sys.platform != 'win32':
    print('TdxHq only support Windows!!!')

from .tdxhq import TdxHq, TdxConfig


def get_kchart_urls(mcode):
    return {
        'm1': '',
        'd1': '',
        'd7': '',
        'd30': '',
    }


def get_host(tdx_cfg_path):
    tdxcfg = TdxConfig(tdx_cfg_path)
    host = tdxcfg.getPrimaryHQHost()
    return host['ipaddress'], host['port']


def get_realtime_data(mcodes, ip, port):
    tdxhq = TdxHq()
    data = tdxhq.connect(ip, port)

    markets = [mcode[:2] for mcode in mcodes]
    codes = [mcode[2:] for mcode in mcodes]
    logging.debug('fetch %s data from tdxhq...' % ','.join(mcodes))

    all_data = tdxhq.getSecurityQuotes(markets, codes, len(mcodes))

    data = {}
    for data_list in all_data:
        data_dict = {}
        data_dict['MCODE'] = tdxhq.market.get(int(data_list[0])) + data_list[1]
        data_dict['NAME'] = data_list[1]
        data_dict['OPEN'] = float(data_list[5])
        data_dict['PRE'] = float(data_list[4])
        data_dict['NEW'] = float(data_list[3])
        data_dict['HIGH'] = float(data_list[6])
        data_dict['LOW'] = float(data_list[7])
        data_dict['BUYPRICE'] = float(data_list[17])
        data_dict['SELLPRICE'] = float(data_list[18])
        data_dict['VOL'] = int(data_list[10])
        data_dict['MONEY'] = float(data_list[12])
        data_dict['BUYCOUNT1'] = int(data_list[19])
        data_dict['BUYPRICE1'] = float(data_list[17])
        data_dict['BUYCOUNT2'] = int(data_list[23])
        data_dict['BUYPRICE2'] = float(data_list[21])
        data_dict['BUYCOUNT3'] = int(data_list[27])
        data_dict['BUYPRICE3'] = float(data_list[25])
        data_dict['BUYCOUNT4'] = int(data_list[31])
        data_dict['BUYPRICE4'] = float(data_list[29])
        data_dict['BUYCOUNT5'] = int(data_list[35])
        data_dict['BUYPRICE5'] = float(data_list[33])
        data_dict['SELLCOUNT1'] = int(data_list[20])
        data_dict['SELLPRICE1'] = float(data_list[18])
        data_dict['SELLCOUNT2'] = int(data_list[24])
        data_dict['SELLPRICE2'] = float(data_list[22])
        data_dict['SELLCOUNT3'] = int(data_list[28])
        data_dict['SELLPRICE3'] = float(data_list[26])
        data_dict['SELLCOUNT4'] = int(data_list[32])
        data_dict['SELLPRICE4'] = float(data_list[30])
        data_dict['SELLCOUNT5'] = int(data_list[36])
        data_dict['SELLPRICE5'] = float(data_list[34])
        data_dict['DATE'] = date.today()
        data_dict['TIME'] = data_list[8]
        data[mcode] = data_dict
    return data
