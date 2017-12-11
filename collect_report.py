#!/usr/bin/env python
# -*- encoding:utf-8 -*-

import argparse
import logging

from stock.finance.stock import get_stock, get_plate
from stock.finance.finance.report import import_finance_report, download_finance_report


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
        mcodes = args.mcode
    else:
        mcodes = [stock.mcode for stock in get_stock()]

    if args.download:
        download_finance_report(mcodes, typ='json')
    elif args.download_overwrite:
        download_finance_report(mcodes, typ='json', overwrite=True)
    elif args.import_:
        import_finance_report(mcodes, typ='json')
    else:
        parser.print_help()


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Stock finance report')
    parser.add_argument('-v', '--verbose', help='verbose help',
                        action='count', default=1)

    parser.add_argument(
        '--download',
        action='store_true',
        help='download report from THS site'
    )
    parser.add_argument(
        '--download-overwrite',
        action='store_true',
        help='download from THS site and overwrite old report'
    )

    parser.add_argument(
        '--import',
        action='store_true',
        dest='import_',
        help='import from downloaded report into database'
    )

    parser.add_argument(
        '--by-plate',
        action='store_true',
        help='input stock mcode as plate code',
    )

    parser.add_argument('mcode',
                        nargs='*', help='stock mcode or plate code')
    stock_main(parser)
