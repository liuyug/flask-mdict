#!/usr/bin/env python3
# -*- encoding:utf-8 -*-

import sys
import logging

from . import functools

logger = logging.getLogger(__name__)


def do_policy(policies, record):
    states = []
    this = sys.modules[__name__]
    for p in policies:
        state = None
        if '_' in p:
            name = p.partition('_')[0]
            func = getattr(this, name)
            if func:
                state = func(p, record)
            else:
                logger.warn('Could not find policy "%s"' % p)
        else:
            func = getattr(this, p)
            if func:
                state = func(record)
            else:
                logger.warn('Could not find policy "%s"' % p)
        if state:
            states.append(state)
    return states


def get_policy_desc(policy):
    desc = []
    name = None
    num = None
    if '_' in policy:
        name = policy.partition('_')[0]
    if name == 'inc':
        num = policy.partition('_')[2]
        desc.append('涨幅')
        desc.append('%s%%' % num)
    elif name == 'dec':
        num = policy.partition('_')[2]
        desc.append('跌幅')
        desc.append('%s%%' % num)
    elif name == 'up':
        num = policy.partition('_')[2]
        desc.append('涨到')
        desc.append(num)
    elif name == 'down':
        num = policy.partition('_')[2]
        desc.append('跌到')
        desc.append(num)
    return ' '.join(desc)


def inc(name, record):
    num = float(name.partition('_')[2])
    if num == 10 and 0.10 == functools.limit(record):
        return name

    zdf = functools.zhangdiefu(record)
    if zdf * 100 >= num:
        return name


def dec(name, record):
    num = float(name.partition('_')[2])
    if num == 10 and -0.10 == functools.limit(record):
        return name
    zdf = functools.zhangdiefu(record)
    if zdf * 100 <= -num:
        return name


def up(name, record):
    new = float(record['NEW'])
    price = float(name.partition('_')[2])
    if new > price:
        return name


def down(name, record):
    new = float(record['NEW'])
    price = float(name.partition('_')[2])
    if new < price:
        return name
