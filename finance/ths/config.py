#!/usr/bin/env python
# -*- encoding:utf-8 -*-

import sys

from collections import OrderedDict


if sys.platform == 'win32':
    ths_dir = 'C:\同花顺软件\同花顺'
else:
    ths_dir = ''


xls_url_map = OrderedDict((
    ('Main', 'http://basic.10jqka.com.cn/%(stock)s/xls/mainreport.xls'),
    ('Debt', 'http://basic.10jqka.com.cn/%(stock)s/xls/debtreport.xls'),
    ('Benefit', 'http://basic.10jqka.com.cn/%(stock)s/xls/benefitreport.xls'),
    ('Cash', 'http://basic.10jqka.com.cn/%(stock)s/xls/cashreport.xls'),
))

json_url_map = OrderedDict((
    ('Main', 'http://basic.10jqka.com.cn/%(stock)s/flash/main.txt'),
    ('Debt', 'http://basic.10jqka.com.cn/%(stock)s/flash/debt.txt'),
    ('Benefit', 'http://basic.10jqka.com.cn/%(stock)s/flash/benefit.txt'),
    ('Cash', 'http://basic.10jqka.com.cn/%(stock)s/flash/cash.txt'),
))

#
# StockBlock.ini
# customized_stock.ini
#
market_id_desc = {
    88: '全球指数',
    178: '香港创业板',
    177: '香港主板',
    176: '香港指数',
    170: '美国股票交易所',
    20: '上证基金',
    48: '同花顺指数',
    186: '纳斯达克资本市场',
    185: '纳斯达克全球精选市场',
    146: '三板Ｂ股',
    145: '三板Ａ股',
    208: '板块指数',
    169: '纽约股票交易所',
    22: '上证风险警示',
    17: '上证Ａ股',
    16: '上证指数',
    19: '上证债券',
    18: '上证Ｂ股',
    37: '深证退市',
    36: '深证基金',
    35: '深证债券',
    34: '深证Ｂ股',
    33: '深证Ａ股',
    32: '深证指数',
}
