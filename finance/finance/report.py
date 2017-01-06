#!/usr/bin/env python
# -*- encoding:utf-8 -*-

import logging

from ..database import get_session
from ..ths import get_report_from_json, download_finance_data
from ..stock import Stock

from .helper import get_report_field_by_desc, get_field_abbr
from .model import Main, Cash, Debt, Benefit


logger = logging.getLogger(__name__)


def download_finance_report(mcodes=None, typ='json'):
    for stock in get_session().query(Stock):
        if mcodes and stock.mcode not in mcodes:
            continue
        download_finance_data(stock.mcode, typ=typ)


def create_finance(mcodes=None, typ='json'):
    if mcodes is None:
        for report_class in [Main, Cash, Benefit, Debt]:
            report_class.__table__.drop(get_session().get_bind(), checkfirst=True)
            report_class.__table__.create(get_session().get_bind(), checkfirst=True)
        get_session().commit()
    for stock in get_session().query(Stock):
        if mcodes:
            if stock.mcode in mcodes:
                stock.Mains.delete()
                stock.Cashs.delete()
                stock.Debts.delete()
                stock.Benefits.delete()
                get_session().commit()
            else:
                continue

        logger.info('Add [%s %s]' % (stock.mcode, stock.name))
        report_data = get_report_from_json(stock.mcode)
        for report, data in report_data.items():
            fields = []
            miss_fields = []
            header = data[0]
            # check header
            for desc in header:
                unit = None
                if isinstance(desc, list):
                    desc, unit = desc
                field = get_report_field_by_desc(report, desc)
                if field:
                    if unit and field[4] != unit:
                        logger.warn('Unit Issue: %s (%s <> %s)' % (
                            desc, unit, field[4]))
                        raise ValueError()
                    else:
                        unit = unit or field[4]
                    fields.append((field[0], unit))
                else:
                    miss_fields.append((desc, unit))
            if miss_fields:
                for desc in miss_fields:
                    logger.error('[%s] %s: %s' % (
                        report, get_field_abbr(desc).lower(), desc, unit))
                raise ValueError('Do not find some fields in "%s"' % report)
            # add database
            report_class = eval(report)

            stock_data = []
            for row_data in data[1:]:
                data_dict = {}
                data_dict['stock_mcode'] = stock.mcode
                for x in range(len(fields)):
                    field, unit = fields[x]
                    if field == 'date':
                        value = row_data[x]
                    elif row_data[x]:
                        value = float(row_data[x])
                    else:
                        value = float('nan')
                    data_dict[field] = value
                stock_data.append(data_dict)
            get_session().bulk_insert_mappings(report_class, stock_data)
        get_session().commit()
