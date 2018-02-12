#!/usr/bin/env python
# -*- encoding:utf-8 -*-

import sys
import codecs
import argparse
import datetime

from mtable import MarkupTable

from stock.common import ths
from stock.common import cninfo


def main(parser):
    args = parser.parse_args()

    if args.pub:
        for mcode in args.mcode:
            data = cninfo.get_announcement(mcode)
            table = MarkupTable()
            table.set_dict_data(data, header=['date', 'type', 'size', 'title'])
            print(table.to_rst())
    elif args.news:
        for mcode in args.mcode:
            data = ths.get_news(mcode, 'news')
            table = MarkupTable()
            table.set_dict_data(data, header=['date', 'title'])
            print(table.to_rst())
    elif args.period:
        for mcode in args.mcode:
            data = cninfo.get_pdf_report(mcode)
            table = MarkupTable()
            table.set_data(data)
            print(table.to_rst())


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Search current stock news')
    parser.add_argument('-v', '--verbose', help='verbose help',
                        action='count', default=1)

    parser.add_argument('--news', action='store_true', help='news')
    parser.add_argument('--pub', action='store_true', help='public announcement')
    parser.add_argument('--period', action='store_true', help='period report')
    parser.add_argument('mcode',
                        nargs='+', help='stock mcode, "*" will match many characters')

    main(parser)
