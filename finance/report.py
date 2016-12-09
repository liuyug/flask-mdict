#!/usr/bin/env python
# -*- encoding:utf-8 -*-
import sys
import os.path

common_path = os.path.abspath(os.path.join(
    os.path.dirname(__file__), '..', 'common'))

sys.path.append(common_path)

from .stock import get_market, get_plate, get_stock
from .finance.model import Main, Debt, Benefit, Cash


from common.finance.report import *


def list_market():
    markets = get_market()
    return [[m.code, m.name] for m in markets]


def list_plate():
    plates = get_plate()
    return [[p.code, p.name] for p in plates]


def list_stock():
    stocks = get_stock()
    return [[s.mcode, s.name, s.abbr, s.date, s.zgb, s.ltgb] for s in stocks]


def get_chart_type(field):
    name = field.partition('-')[0]
    if name in Plugins:
        return Plugins[field]['chart']
    if name in Formula:
        return Formula.get(name)['chart']
    for model in [Main, Debt, Benefit, Cash]:
        if name in model.get_columns():
            return model.get_columns()[field]['chart']
