#!/usr/bin/env python
# -*- encoding:utf-8 -*-

"""Calculate some items by finance data."""

from . import functools

PluginDesc = u'插件'


Plugins = {
    'yylr_lrze': {
        'desc': u'营业利润/利润总额',
        'unit': u'%',
        'type': 'plugin',
        'calc': functools.yylr_lrze,
        'chart': 'chart_line_ratio',
    },
    'tzsy_lrze': {
        'desc': u'投资收益/利润总额',
        'unit': u'%',
        'type': 'plugin',
        'calc': functools.tzsy_lrze,
        'chart': 'chart_line_ratio',
    },
    'yywlr_lrze': {
        'desc': u'营业外利润/利润总额',
        'unit': u'%',
        'type': 'plugin',
        'calc': functools.yywlr_lrze,
        'chart': 'chart_line_ratio',
    },
    'zzcsyl': {
        'desc': u'总资产收益率',
        'unit': u'%',
        'type': 'plugin',
        'calc': functools.zzcsyl,
        'chart': 'chart_line_ratio',
    },
    'zczzl': {
        'desc': u'资产周转率',
        'unit': u'',
        'type': 'plugin',
        'calc': functools.zczzl,
        'chart': 'chart_line_value',
    },
    'xsjll': {
        'desc': u'销售净利率',
        'unit': u'%',
        'type': 'plugin',
        'calc': functools.xsjll,
        'chart': 'chart_line_ratio',
    },
    'xsfyl': {
        'desc': u'销售费用率',
        'unit': u'%',
        'type': 'plugin',
        'calc': functools.xsfyl,
        'chart': 'chart_line_ratio',
    },
    'mghbzj': {
        'desc': u'每股货币资金',
        'unit': u'元',
        'type': 'plugin',
        'calc': functools.mghbzj,
        'chart': 'chart_line_value',
    },
    'mgjlr': {
        'desc': u'每股净利润',
        'unit': u'元',
        'type': 'plugin',
        'calc': functools.mgjlr,
        'chart': 'chart_line_value',
    },
    'mgjxjll': {
        'desc': u'每股净现金流量',
        'unit': u'元',
        'type': 'plugin',
        'calc': functools.mgjxjll,
        'chart': 'chart_line_value',
    },
}
