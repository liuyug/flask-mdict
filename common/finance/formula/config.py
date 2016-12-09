#!/usr/bin/env python
# -*- encoding:utf-8 -*-

from . import functools

FormulaDesc = u'公式'


Formula = {
    'yoy': {
        'desc': u'同比增长率',
        'unit': u'%',
        'calc': functools.yoy,
        'chart': 'chart_line_ratio',
    },
    'mom': {
        'desc': u'环比增长率',
        'unit': u'%',
        'calc': functools.mom,
        'chart': 'chart_line_ratio',
    },
}


period_announcement_desc = [
    u'第一季度季报',
    u'半年报',
    u'第三季度季报',
    u'年报',
]

pe_desc = [
    u'市盈率LYR',
    u'市盈率TTM',
    u'动态市盈率',
]

pe_gb_desc = [u'上年股本', u'当前股本']
