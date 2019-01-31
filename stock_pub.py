#!/usr/bin/env python
# -*- encoding:utf-8 -*-

import argparse

from mtable import MarkupTable

from stock.service import cninfo
from stock.service.ths import web as ths
from stock.utils import ElapsedTimer


def main(parser):
    args = parser.parse_args()
    if args.pub:
        for mcode in args.mcode:
            with ElapsedTimer(True):
                if False:
                    data, header = cninfo.get_pub(mcode)
                else:
                    data, header = ths.get_pub(mcode)
                table = MarkupTable()
                table.set_dict_data(data, header=header)
                print(table.to_rst())
    elif args.news:
        for mcode in args.mcode:
            with ElapsedTimer(True):
                data, header = ths.get_news(mcode)
                table = MarkupTable()
                table.set_dict_data(data, header=header)
                print(table.to_rst())
    elif args.research:
        for mcode in args.mcode:
            with ElapsedTimer(True):
                data, header = ths.get_research(mcode)
                table = MarkupTable()
                table.set_dict_data(data, header=header)
                print(table.to_rst())
    elif args.period:
        for mcode in args.mcode:
            with ElapsedTimer(True):
                table = MarkupTable()
                data, header = cninfo.get_period_report(mcode)
                table.set_dict_data(data, header=header)
                print(table.to_rst())


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Search current stock news')
    parser.add_argument('-v', '--verbose', help='verbose help',
                        action='count', default=1)

    parser.add_argument('--news', action='store_true', help='news')
    parser.add_argument('--pub', action='store_true', help='public announcement')
    parser.add_argument('--research', action='store_true', help='research announcement')
    parser.add_argument('--period', action='store_true', help='period report')
    parser.add_argument('mcode',
                        nargs='+', help='stock mcode, "*" will match many characters')

    main(parser)
