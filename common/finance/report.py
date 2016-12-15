#!/usr/bin/env python
# -*- encoding:utf-8 -*-

import logging
import time
from collections import OrderedDict


from .plugin import Plugins, PluginDesc
from .formula import Formula, FormulaDesc
from .model_base import MainBase, CashBase, DebtBase, BenefitBase


logger = logging.getLogger(__name__)


def list_field():
    fields = OrderedDict()
    for model in [MainBase, DebtBase, BenefitBase, CashBase]:
        name = model.__name__[:-4]
        fields[name] = {}
        fields[name]['desc'] = model.__doc__
        fields[name]['fields'] = [
            field for field in model.get_columns().values() if field['name'] != 'date']
    fields['Plugin'] = {}
    fields['Plugin']['desc'] = PluginDesc
    fields['Plugin']['fields'] = [
        {'name': k, 'desc': v['desc'], 'unit': v['unit']} for k, v in Plugins.items()]
    fields['Formula'] = {}
    fields['Formula']['desc'] = FormulaDesc
    fields['Formula']['fields'] = [
        {'name': k, 'desc': v['desc'], 'unit': v['unit']} for k, v in Formula.items()]
    return fields


def get_value(stock, field):
    name = field.rpartition('-')[2]
    calcs = []
    if field != name:
        calcs = field.rpartition('-')[0].split('-')
    if name in Plugins:
        values = Plugins[name]['calc'](stock)
        desc = Plugins[name]['desc']
        unit = Plugins[name]['unit']
        chart = Plugins[name]['chart']
    else:
        values = {}
        desc = None
        unit = None
        chart = None
        find = False
        for model in [MainBase, DebtBase, CashBase, BenefitBase]:
            if name in model.get_columns():
                find = True
                break
        if find:
            records = getattr(stock, '%ss' % model.__name__[:-4])
            for record in records:
                date = record.date
                value = getattr(record, name)
                values[date] = value
            desc = model.get_columns()[name]['desc']
            unit = model.get_columns()[name]['unit']
            chart = model.get_columns()[name]['chart']

    if calcs:
        find = False
        for calc in calcs[::-1]:
            if calc not in Formula:
                continue
            calc_item = Formula[calc]
            values = calc_item['calc'](values)
            desc += calc_item['desc']
            find = True
        if find:
            unit = calc_item['unit']
            chart = calc_item['chart']
    return {'values': values, 'desc': desc, 'unit': unit, 'chart': chart}


def get_stock_values(stock, fields):
    data = []
    date_data = set()
    field_values = {}
    for field in fields:
        clock_s = time.clock()
        value = get_value(stock, field)
        logger.debug('Get %s %s: %s ... (%.2f second)' % (
            stock.mcode, stock.name, field,
            time.clock() - clock_s))
        field_values[field] = value
        date_data |= set(list(value['values'].keys()))
    info = '%s' % (stock.mcode)
    header = [info] + sorted(list(date_data), reverse=True)
    data.append(header)

    for field in fields:
        records = [None] * len(header)
        values = field_values[field]
        if values['unit']:
            records[0] = '%(desc)s (%(unit)s)' % values
        else:
            records[0] = '%(desc)s' % values
        for date, value in values['values'].items():
            idx = header.index(date)
            records[idx] = value
        data.append(records)
    return data


def get_field_values(field, stocks):
    data = []
    date_data = set()
    stock_values = {}
    for stock in stocks:
        clock_s = time.clock()
        value = get_value(stock, field)
        logger.debug('Get %s %s: %s ... (%.2f second)' % (
            stock.mcode, stock.name, field,
            time.clock() - clock_s))
        stock_values[stock.mcode] = value
        date_data |= set(list(value['values'].keys()))
    if value['unit']:
        info = '%(desc)s (%(unit)s)' % value
    else:
        info = '%(desc)s' % value
    header = [info, '', u'流通股本 (股)', u'流通股本/总股本 (%)'] + sorted(list(date_data), reverse=True)

    for stock in stocks:
        records = [None] * len(header)
        values = stock_values[stock.mcode]
        records[0] = stock.mcode
        records[1] = stock.name
        records[2] = stock.ltgb
        records[3] = stock.ltgb_percent()
        for date, value in values['values'].items():
            idx = header.index(date)
            records[idx] = value
        data.append(records)
    data = sorted(
        data,
        key=lambda x: [float('-inf') if v is None else v for v in x[4:8]],
        reverse=True)
    data.insert(0, header)
    return data
