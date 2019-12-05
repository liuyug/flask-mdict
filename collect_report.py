#!/usr/bin/env python3
# -*- encoding:utf-8 -*-

import os
import argparse
import logging

from stock.base.stock import get_stock, get_plate
from stock.service.ths.web.finance import download_finance_report, download_finance_data2
from stock.service.tdx.local.finance import load_finance_data
from stock.service.netease.finance import netease_download, netease_import, netease_view
from stock.service.ths.finance import ths_download, ths_import, ths_view

from stock.base.finance.helper import list_field
from stock.database import get_session

logger = logging.getLogger(__name__)


def do_test(prefix):
    session = get_session('finance')
    data = list_field(session, prefix)
    for k, v in data.items():
        print(k, '{desc} {abbr} => {name}' % v)


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
        # download_finance_data2(mcodes, typ='xls', overwrite=args.overwrite)
        # download_finance_report(mcodes, typ='json', overwrite=args.overwrite)
        ths_download(mcodes)
    elif args.import_:
        # import_finance_data(mcodes, typ='xls')
        ths_import(mcodes)
    elif args.view:
        ths_view()
    elif args.tdx:
        load_finance_data(mcodes[0])
    elif args.download2:
        netease_download(mcodes)
    elif args.import2:
        netease_import(mcodes)
    elif args.view2:
        netease_view()
    elif args.test:
        do_test(mcodes)
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
        '--import', action='store_true', dest='import_',
        help='import local report data'
    )

    parser.add_argument(
        '--view', action='store_true',
        help='create view'
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

    parser.add_argument('--download2', action='store_true', help='netease download report')
    parser.add_argument('--import2', action='store_true', help='netease import report')
    parser.add_argument('--view2', action='store_true', help='netease create view')

    parser.add_argument('--test', action='store_true', help='test...')

    parser.add_argument('mcode',
                        nargs='*', help='stock mcode or plate code')
    stock_main(parser)
