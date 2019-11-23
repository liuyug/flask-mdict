#!/usr/bin/env python3
# -*- encoding:utf-8 -*-

import os
import argparse
import logging
import csv

import requests

from stock.base.stock import get_stock, get_plate
from stock.service.ths.finance import import_finance_data
from stock.service.ths.web.finance import download_finance_report, download_finance_data2
from stock.service.tdx.local.finance import load_finance_data

from stock.database import get_session
from stock.base.finance.model import ZYCWZB, YLNL, CHNL, CZNL, YYNL, \
    CWBBZY, ZCFZB, LRB, XJLLB

from stock.utils.network import download_file

logger = logging.getLogger(__name__)


def stock_main(parser):
    args = parser.parse_args()

    level = logging.WARNING - (args.verbose * 10)
    logging.basicConfig(format='[%(levelname)s] %(message)s', level=level)

    mcodes = []
    if args.by_plate:
        for code in args.mcode:
            plate = get_plate(code)
            if plate:
                mcodes = plate.stock_mcodes
    elif args.mcode:
        mcodes = [mcode.upper() for mcode in args.mcode]
    else:
        mcodes = [stock.mcode for stock in get_stock(market_code='SHSZA')]

    if args.download:
        download_finance_data2(mcodes, typ='xls', overwrite=args.overwrite)
        # download_finance_report(mcodes, typ='json', overwrite=args.overwrite)
    elif args.import_:
        import_finance_data(mcodes, typ='xls')
    elif args.tdx:
        load_finance_data(mcodes[0])
    elif args.download2:
        tables = [ZYCWZB, YLNL, CHNL, CZNL, YYNL, CWBBZY, ZCFZB, LRB, XJLLB]
        output_dir = os.path.join('build', 'finance')
        req = requests.session()
        for mcode in mcodes:
            print('\rCatch %s...' % mcode, end='')
            mcode_dir = os.path.join(output_dir, mcode)
            if not os.path.exists(mcode_dir):
                os.makedirs(mcode_dir)
            for table in tables:
                url = table.url_base % mcode[2:]
                dest = os.path.join(mcode_dir, '%s.csv' % table.__tablename__)
                if os.path.exists(dest):
                    print('skip %s...' % dest)
                    continue
                size = download_file(url, dest, req)
                if size < 1:
                    os.remove(dest)
    elif args.import2:
        session = get_session('finance')
        tables = [ZYCWZB, YLNL, CHNL, CZNL, YYNL, CWBBZY, ZCFZB, LRB, XJLLB]
        for table in tables:
            table.__table__.drop(session.get_bind(), checkfirst=True)
            table.__table__.create(session.get_bind(), checkfirst=True)
            session.commit()
        output_dir = os.path.join('build', 'finance')
        for mcode in mcodes:
            mcode_dir = os.path.join(output_dir, mcode)
            for table in tables:
                print(f'\rimport {mcode} - {table.__doc__}        ', end='')
                dest = os.path.join(mcode_dir, '%s.csv' % table.__tablename__)
                data = []
                with open(dest, encoding='gbk') as f:
                    reader = csv.DictReader(f)
                    for row in reader:
                        name = None
                        for k, v in row.items():
                            if k:
                                k = k.strip()
                            if not k:
                                continue
                            if k in ['报告日期', '报告期']:
                                name = v.strip()
                                if not name:
                                    break
                                continue
                            assert name, row
                            data.append({
                                'mcode': mcode,
                                'date': k,
                                'name': name,
                                'value': None if not v or not v.strip(' -\t') else float(v),
                            })
                session.bulk_insert_mappings(table, data)
                session.commit()
            print()
    else:
        parser.print_help()


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Stock finance report')
    parser.add_argument('-v', '--verbose', help='verbose help',
                        action='count', default=1)

    group = parser.add_argument_group('download finance report')
    group.add_argument(
        '--download',
        action='store_true',
        help='download report from THS site'
    )
    group.add_argument(
        '--overwrite',
        action='store_true',
        help='overwrite old report'
    )

    parser.add_argument(
        '--import',
        action='store_true',
        dest='import_',
        help='import local report data'
    )

    parser.add_argument(
        '--by-plate',
        action='store_true',
        help='input stock mcode as plate code',
    )
    parser.add_argument(
        '--tdx',
        action='store_true',
        help='tdx finance data',
    )

    parser.add_argument('--download2', action='store_true', help='download report')
    parser.add_argument('--import2', action='store_true', help='import report')

    parser.add_argument('mcode',
                        nargs='*', help='stock mcode or plate code')
    stock_main(parser)
