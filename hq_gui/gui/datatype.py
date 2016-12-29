#!/usr/bin/env python3
# -*- encoding:utf-8 -*-

from collections import OrderedDict

from . import functools
from .utils import sizeof_cnfmt
from .policy import do_policy


DataType = OrderedDict((
    ('MCODE', {'desc': '代码', 'format': '%s', 'preformat': None}),
    ('ZQMC', {'desc': '名称', 'format': '%s', 'preformat': None}),
    ('OPEN', {'desc': '开盘', 'format': '%0.2f', 'preformat': None}),
    ('PRE', {'desc': '昨收', 'format': '%0.2f', 'preformat': None}),
    ('NEW', {'desc': '现价', 'format': '%0.2f', 'preformat': None}),
    ('HIGH', {'desc': '最高', 'format': '%0.2f', 'preformat': None}),
    ('LOW', {'desc': '最低', 'format': '%0.2f', 'preformat': None}),
    ('BUYPRICE', {'desc': '买价', 'format': '%0.2f', 'preformat': None}),
    ('SELLPRICE', {'desc': '卖价', 'format': '%0.2f', 'preformat': None}),
    ('VOL', {'desc': '总手', 'format': '%s', 'preformat': sizeof_cnfmt}),
    ('MONEY', {'desc': '金额', 'format': '%s', 'preformat': sizeof_cnfmt}),
    ('BUYCOUNT1', {'desc': '买一量', 'format': '%0.0f', 'preformat': None}),
    ('BUYPRICE1', {'desc': '买一价', 'format': '%0.2f', 'preformat': None}),
    ('BUYCOUNT2', {'desc': '买二量', 'format': '%0.0f', 'preformat': None}),
    ('BUYPRICE2', {'desc': '买二价', 'format': '%0.2f', 'preformat': None}),
    ('BUYCOUNT3', {'desc': '买三量', 'format': '%0.0f', 'preformat': None}),
    ('BUYPRICE3', {'desc': '买三价', 'format': '%0.2f', 'preformat': None}),
    ('BUYCOUNT4', {'desc': '买四量', 'format': '%0.0f', 'preformat': None}),
    ('BUYPRICE4', {'desc': '买四价', 'format': '%0.2f', 'preformat': None}),
    ('BUYCOUNT5', {'desc': '买五量', 'format': '%0.0f', 'preformat': None}),
    ('BUYPRICE5', {'desc': '买五价', 'format': '%0.2f', 'preformat': None}),
    ('SELLCOUNT1', {'desc': '卖一量', 'format': '%0.0f', 'preformat': None}),
    ('SELLPRICE1', {'desc': '卖一价', 'format': '%0.2f', 'preformat': None}),
    ('SELLCOUNT2', {'desc': '卖二量', 'format': '%0.0f', 'preformat': None}),
    ('SELLPRICE2', {'desc': '卖二价', 'format': '%0.2f', 'preformat': None}),
    ('SELLCOUNT3', {'desc': '卖三量', 'format': '%0.0f', 'preformat': None}),
    ('SELLPRICE3', {'desc': '卖三价', 'format': '%0.2f', 'preformat': None}),
    ('SELLCOUNT4', {'desc': '卖四量', 'format': '%0.0f', 'preformat': None}),
    ('SELLPRICE4', {'desc': '卖四价', 'format': '%0.2f', 'preformat': None}),
    ('SELLCOUNT5', {'desc': '卖五量', 'format': '%0.0f', 'preformat': None}),
    ('SELLPRICE5', {'desc': '卖五价', 'format': '%0.2f', 'preformat': None}),
    ('DATE', {'desc': '日期', 'format': '%s', 'preformat': None}),
    ('TIME', {'desc': '时间', 'format': '%s', 'preformat': None}),
))


UserDataType = {
    '_zhangdiefu': {
        'desc': '涨幅',
        'calc': functools.zhangdiefu,
        'preformat': functools.percent_format,
        'format': '%+0.2f %%',
    },
    '_policy': {
        'desc': '策略',
        'calc': do_policy,
        'preformat': None,
        'format': '%s',
    },
    '_cost': {
        'desc': '成本',
        'calc': None,
        'preformat': None,
        'format': '%s',
    },
    '_profit': {
        'desc': '每股盈亏',
        'calc': None,
        'preformat': None,
        'format': '%+0.2f',
    },
    '_profit_percent': {
        'desc': '盈亏比例 (%)',
        'calc': None,
        'preformat': functools.percent_format,
        'format': '%+0.2f',
    },
}
