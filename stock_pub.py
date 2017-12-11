#!/usr/bin/env python
# -*- encoding:utf-8 -*-

import sys
import codecs
import argparse
import datetime

import six
from rsttable import RstTable

from stock.common import ths
from stock.common import cninfo


def main(parser):
    args = parser.parse_args()

    if six.PY2:
        sys.stdout = codecs.getwriter(args.encoding)(sys.stdout)

    today = datetime.date.today()
    if args.day <= 0:
        delta = datetime.timedelta.max
    else:
        delta = datetime.timedelta(days=args.day)
    if args.news or args.pub:
        for mcode in args.mcode:
            data = ths.get_news(mcode)
            if args.news:
                for item in data['mine']:
                    news_date = datetime.datetime.strptime(item['date'], '%Y-%m-%d').date()
                    if (today - news_date) < delta:
                        print('[%(date)s] %(title)s' % item)
            elif args.pub:
                for item in data['pub']:
                    news_date = datetime.datetime.strptime(item['date'], '%Y-%m-%d').date()
                    if (today - news_date) < delta:
                        print('[%(date)s] %(title)s' % item)
    elif args.period:
        for mcode in args.mcode:
            data = cninfo.get_pdf_report(mcode)
            table = RstTable(data)
            print(table.table())


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Search current stock news')
    parser.add_argument('-v', '--verbose', help='verbose help',
                        action='count', default=1)
    parser.add_argument('--encoding', default='utf-8', help='Output terminal encoding. default: utf-8')

    parser.add_argument('--day', type=int, default=0, help='news/public announcement before days')

    parser.add_argument('--news', action='store_true', help='news')
    parser.add_argument('--pub', action='store_true', help='public announcement')
    parser.add_argument('--period', action='store_true', help='period report')
    parser.add_argument('mcode',
                        nargs='+', help='stock mcode, "*" will match many characters')

    main(parser)
