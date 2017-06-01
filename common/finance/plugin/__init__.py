#!/usr/bin/env python
# -*- encoding:utf-8 -*-

"""Calculate some items by finance data."""

from . import functools

PluginDesc = u'插件'


Plugins = {
    'zyywlr_lrze': {
        'desc': u'主营业务利润/利润总额',
        'unit': u'%',
        'type': 'plugin',
        'calc': functools.zyywlr_lrze,
        'chart': 'chart_line_ratio',
    },
    'qtywlr_lrze': {
        'desc': u'其它业务利润/利润总额',
        'unit': u'%',
        'type': 'plugin',
        'calc': functools.qtywlr_lrze,
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
        'desc': u'总资产净利率',
        'unit': u'%',
        'type': 'plugin',
        'calc': functools.zzcjll,
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
        'desc': u'营业净利率',
        'unit': u'%',
        'type': 'plugin',
        'calc': functools.yyjll,
        'chart': 'chart_line_ratio',
    },
    'xsfyl': {
        'desc': u'销售费用率',
        'unit': u'%',
        'type': 'plugin',
        'calc': functools.xsfyl,
        'chart': 'chart_line_ratio',
    },
}
