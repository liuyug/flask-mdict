#!/usr/bin/env python
# -*- encoding:utf-8 -*-


def string_to_bool(text):
    return text.lower() in ['true', 'on', 'yes', '1']


def sizeof_fmt(num, suffix='B'):
    if num != num:
        return ''
    for unit in ['', 'Ki', 'Mi', 'Gi', 'Ti', 'Pi', 'Ei', 'Zi']:
        if abs(num) < 1024.0:
            return "%3.2f%s%s" % (num, unit, suffix)
        num /= 1024.0
    return "%.2f%s%s" % (num, 'Yi', suffix)


def sizeof_cnfmt(num, suffix=''):
    if num != num:
        return ''
    for unit in [u'', u'万', u'亿', u'万亿']:
        if abs(num) < 10000.0:
            return u'%3.2f %s%s' % (num, unit, suffix)
        num /= 10000.0
    return u'%.2f %s%s' % (num, u'亿亿', suffix)
