#!/usr/bin/env python
# -*- encoding:utf-8 -*-

import os.path
import logging

import xlsxwriter

from ..config import get_config
from ..database import get_session, get_all_tables
from ..ths import create_plate_from_site, create_plate_from_local

from .model import Stock, Plate


logger = logging.getLogger(__name__)


# many to many stock plate
def create_plate():
    plates_data = create_plate_from_site()

    Plate.__table__.drop(get_session().get_bind(), checkfirst=True)
    Plate.__table__.create(get_session().get_bind())
    get_session().commit()

    stock_plates = {}
    for plates in plates_data.values():
        for plate in plates:
            stock_mcodes = []
            for stock_code in plate['stock']:
                if stock_code.startswith('6'):
                    mcode = 'SH%s' % stock_code
                elif stock_code.startswith('0'):
                    mcode = 'SZ%s' % stock_code
                elif stock_code.startswith('3'):
                    mcode = 'SZ%s' % stock_code
                else:
                    raise ValueError(stock_code)

                q_stock = get_session().query(Stock).filter_by(mcode=mcode)
                scalar = get_session().query(q_stock.exists()).scalar()
                if scalar:
                    stock_mcodes.append(mcode)
                    if mcode in stock_plates:
                        stock_plates[mcode]['plate_codes'] = '%s;%s' % (
                            stock_plates[mcode]['plate_codes'], plate['code'])
                    else:
                        stock_plates[mcode] = {
                            'mcode': mcode,
                            'plate_codes': plate['code'],
                        }
                else:
                    logger.warn('Could not find %s' % (mcode))
            plate['stock_mcodes'] = stock_mcodes
            logger.info('Add plate: <%(code)s: %(name)s>' % plate)

        logger.info('Add plate into database...')
        get_session().bulk_insert_mappings(Plate, plates)
        get_session().commit()
    logger.info('Update stock database...')
    get_session().bulk_update_mappings(Stock, stock_plates.values())
    get_session().commit()


def create_plate_2(frm='ths_site'):
    if frm == 'ths_site':
        plates_data = create_plate_from_site()
    elif frm == 'ths_local':
        plates_data = create_plate_from_local()
    else:
        raise ValueError('Error frm: %s' % frm)
    plates = []
    stock_plates = []
    for code, name, codelist in plates_data:
        plates.append({
            'code': code,
            'name': name,
        })
        for stock_code in codelist:
            if stock_code.startswith('6'):
                mcode = 'SH%s' % stock_code
            elif stock_code.startswith('0'):
                mcode = 'SZ%s' % stock_code
            elif stock_code.startswith('3'):
                mcode = 'SZ%s' % stock_code
            else:
                raise ValueError(stock_code)
            q_stock = get_session().query(Stock).filter_by(mcode=mcode)
            scalar = get_session().query(q_stock.exists()).scalar()
            if scalar:
                stock_plates.append({
                    'mcode': mcode,
                    'plate_code': code
                })
            else:
                logger.warn('Could not find %s in plate %s %s' % (mcode, code, name))

        logger.info('Add plate: <%s: %s>' % (code, name))

    Plate.__table__.drop(get_session().get_bind(), checkfirst=True)
    Plate.__table__.create(get_session().get_bind())
    get_session().commit()

    get_session().bulk_insert_mappings(Plate, plates)
    get_session().bulk_update_mappings(Stock, stock_plates)
    get_session().commit()


def get_plate(code=None):
    tables = get_all_tables()
    if 'plate' not in tables:
        return []
    if code is None:
        return get_session().query(Plate).order_by(Plate.code).all()
    return get_session().query(Plate).filter_by(code=code).first()


def make_plate_xls(xls_path=None):
    if not xls_path:
        config = get_config()
        base_dir = config['general'].get('base_dir')
        xls_path = os.path.join(base_dir, 'plate.xlsx')

    logger.info('Outut plate xlsx %s' % xls_path)
    book = xlsxwriter.Workbook(xls_path)
    sheet = book.add_worksheet('Plate')
    plates = get_session().query(Plate).all()
    nrow = 0
    for plate in plates:
        sheet.write_row(nrow, 0, [plate.code, plate.name])
        sheet.write_row(nrow, 2, [stock.mcode for stock in plate.stocks])
        nrow += 1
    book.close()
