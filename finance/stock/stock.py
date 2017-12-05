#!/usr/bin/env python
# -*- encoding:utf-8 -*-

import os.path
import logging
import json

import xlsxwriter

from ..utils import url_downloader
from ..config import get_config
from ..database import get_session

from .model import Stock
from . import sse
from . import szse


logger = logging.getLogger(__name__)


def create_stock(stock_json='stock.json'):
    """
    SH: http://query.sse.com.cn/security/stock/downloadStockListFile.do?csrcCode=&stockCode=&areaName=&stockType=1
    SZ: http://www.szse.cn/szseWeb/ShowReport.szse?SHOWTYPE=xlsx&CATALOGID=1110&tab2PAGENUM=1&ENCODE=1&TABKEY=tab2
    通过同花顺行情获取股票数据: python hq_direct.py ths --stock-json stock.json
    """
    if os.path.exists(stock_json):
        stocks = json.loads(open(stock_json).read().decode('utf8'))
        os.remove(stock_json)
    else:
        config = get_config()
        stock_url = config.get('hq', 'url') + '/ths/code/'
        logger.info('fetch stock from "%s"' % stock_url)
        response = url_downloader(stock_url)
        if response['data'] is None:
            logger.warn(response['error'])
            return
        stocks = json.loads(response['data'].decode('utf8')).get('code')
    sh_count = 0
    sz_count = 0
    for stock in stocks:
        mcode = '%(market)s%(code)s' % stock
        stock['mcode'] = mcode
        if stock['code'].startswith('6'):
            market_code = 'SSE'
            sh_count += 1
        elif stock['code'].startswith('3'):
            market_code = 'SZSE_GEM'
            sz_count += 1
        elif stock['code'].startswith('002'):
            market_code = 'SZSE_SME'
            sz_count += 1
        else:
            market_code = 'SZSE_MAIN'
            sz_count += 1
        stock['market_code'] = market_code
        del stock['code']
        del stock['market']

        logger.debug('Add %(mcode)s: %(name)s' % stock)

    Stock.__table__.drop(get_session().get_bind(), checkfirst=True)
    Stock.__table__.create(get_session().get_bind(), checkfirst=True)
    get_session().commit()

    get_session().bulk_insert_mappings(Stock, stocks)
    get_session().commit()

    logger.info('SH: %d' % sh_count)
    logger.info('SZ: %d' % sz_count)
    logger.info('Total: %d' % (sh_count + sz_count))


def create_stock_info():
    logger.info('Add SH Company Information...')
    info_data = []
    for row in sse.get_stocks()[1:]:
        q_stock = get_session().query(Stock).filter_by(mcode=row[0])
        scalar = get_session().query(q_stock.exists()).scalar()
        if scalar:
            info_data.append({
                'mcode': row[0],
                'date': row[2],
                'zgb': row[3],
                'ltgb': row[4],
                'ltgb_percent': row[4] * 100.0 / row[3],
            })
        else:
            logger.warn('Could not find %s %s' % (row[0], row[1]))

    logger.info('Add SZ Company Information...')
    for row in szse.get_stocks()[1:]:
        q_stock = get_session().query(Stock).filter_by(mcode=row[0])
        scalar = get_session().query(q_stock.exists()).scalar()
        if scalar:
            info_data.append({
                'mcode': row[0],
                'date': row[2],
                'zgb': row[3],
                'ltgb': row[4],
                'ltgb_percent': row[4] * 100.0 / row[3],
            })
        else:
            logger.warn('Could not find %s %s' % (row[0], row[1]))
    get_session().bulk_update_mappings(Stock, info_data)
    get_session().commit()


def create_disclosure_report_pdf():
    pass


def get_stock(mcode=None):
    if mcode is None:
        return get_session().query(Stock).order_by(mcode).all()
    return get_session().query(Stock).filter_by(mcode=mcode.upper()).first()


def get_stock_by_abbr(abbr):
    if abbr == '*':
        stocks = get_session().query(Stock).all()
    abbr = abbr.replace('*', '%')
    if abbr[0] != '%':
        abbr = '%' + abbr
    if abbr[-1] != '%':
        abbr = abbr + '%'
    stocks = []
    stocks += get_session().query(Stock).filter(Stock.mcode.like(abbr)).all()
    stocks += get_session().query(Stock).filter(Stock.abbr.like(abbr)).all()
    return stocks


def make_stock_xls(xls_path=None):
    if not xls_path:
        config = get_config()
        base_dir = config.get('general', 'base_dir')
        xls_path = os.path.join(base_dir, 'stock.xlsx')

    logger.info('Output stock xlsx: %s' % xls_path)

    book = xlsxwriter.Workbook(xls_path)
    sheet = book.add_worksheet('Stock')
    stocks = get_session().query(Stock).all()
    nrow = 0
    for stock in stocks:
        sheet.write_row(nrow, 0, [
            stock.mcode, stock.name, stock.abbr,
            stock.market.code, stock.market.name,
            stock.plate.code, stock.plate.name])
        nrow += 1
    book.close()
