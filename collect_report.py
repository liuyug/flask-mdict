#!/usr/bin/env python
# -*- encoding:utf-8 -*-

import argparse
import logging

from finance.stock import get_stock, get_plate
from finance.finance.report import create_finance, download_finance_report


logger = logging.getLogger(__name__)


def stock_main(parser):
    args = parser.parse_args()

    level = logging.WARNING - (args.verbose * 10)
    logging.basicConfig(format='[%(levelname)s] %(message)s', level=level)

    mcodes = []
    if args.by_plate:
        for code in args.code:
            plate = get_plate(code)
            if plate:
                mcodes = [stock.mcode for stock in plate.stocks]
    elif args.code:
        mcodes = args.code
    else:
        mcodes = [stock.mcode for stock in get_stock()]

    if args.download:
        download_finance_report(mcodes, typ='json')
    elif args.update_db:
        create_finance(mcodes, typ='json')
    else:
        parser.print_help()


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Stock finance report')
    parser.add_argument('-v', '--verbose', help='verbose help',
                        action='count', default=1)

    parser.add_argument(
        '--download',
        action='store_true',
        help='download report'
    )

    parser.add_argument(
        '--update-db',
        action='store_true',
        help='collect finance report and update database'
    )

    parser.add_argument(
        '--by-plate',
        action='store_true',
        help='use THS plate code',
    )

    parser.add_argument('code',
                        nargs='*', help='stock mcode or plate code')
    stock_main(parser)
