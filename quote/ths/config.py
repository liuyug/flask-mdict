#!/usr/bin/env python
# -*- encoding:utf-8 -*-

import sys


if sys.platform == 'win32':
    ths_dir = 'C:\同花顺软件\同花顺'
else:
    ths_dir = ''


HQDATATYPE = (
    'MCODE',
    'ZQMC',
    'OPEN',
    'PRE',
    'NEW',
    'HIGH',
    'LOW',
    'BUYPRICE',
    'SELLPRICE',
    'VOL',
    'MONEY',
    'BUYCOUNT1',
    'BUYPRICE1',
    'BUYCOUNT2',
    'BUYPRICE2',
    'BUYCOUNT3',
    'BUYPRICE3',
    'BUYCOUNT4',
    'BUYPRICE4',
    'BUYCOUNT5',
    'BUYPRICE5',
    'SELLCOUNT1',
    'SELLPRICE1',
    'SELLCOUNT2',
    'SELLPRICE2',
    'SELLCOUNT3',
    'SELLPRICE3',
    'SELLCOUNT4',
    'SELLPRICE4',
    'SELLCOUNT5',
    'SELLPRICE5',
    'DATE',
    'TIME',
)
