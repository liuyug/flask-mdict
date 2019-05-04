#!/usr/bin/env python3
# -*- encoding:utf-8 -*-

import argparse
import logging

from stock.base.stock import get_stock, get_plate
from stock.service.ths.finance import import_finance_report
from stock.service.ths.web.finance import download_finance_report, download_finance_data2
from stock.service.tdx.local.finance import load_finance_data


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
        import_finance_report(mcodes, typ='json')
    elif args.tdx:
        load_finance_data(mcodes[0])
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

    parser.add_argument('mcode',
                        nargs='*', help='stock mcode or plate code')
    stock_main(parser)
