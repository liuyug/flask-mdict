#!/usr/bin/env python
# -*- encoding:utf-8 -*-


def percent_format(value):
    return value * 100


def zhangdiefu(record):
    new = float(record.get('NEW'))
    pre = float(record.get('PRE'))
    return (new - pre) / pre


def limit(record):
    new = float(record.get('NEW'))
    pre = float(record.get('PRE'))
    top = round(pre * 1.1, 2)
    bottom = round(pre * 0.9, 2)
    if new == top:
        return 0.10
    elif new == bottom:
        return -0.10
