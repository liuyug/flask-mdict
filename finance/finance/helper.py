#!/usr/bin/env python
# -*- encoding:utf-8 -*-

from ..pinyin import pyabbr

from . import config


def fix_field_name(name):
    name = name.partition('|')[0]
    name = name.partition('(')[0]
    if name == u'资产总计':
        name = u'总资产'
    return name


def get_field_abbr(name):
    name = fix_field_name(name)
    return pyabbr(name).upper()


def get_report_field_by_desc(report, desc):
    desc = fix_field_name(desc)
    report_field = eval('config.%s_field' % report)
    for field in report_field:
        if field[2] == desc:
            return field
