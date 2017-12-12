#!/usr/bin/env python3
# -*- encoding:utf-8 -*-

import sys
import codecs
import argparse

import six

from stock.history.ths import quote as ths
from stock.history.tdx import quote as tdx


def main():
    argparser = argparse.ArgumentParser(description='History HQ')
    argparser.add_argument('--encoding', default='utf8', help='terminal character encoding')

    subparsers = argparser.add_subparsers(help='hq category', dest='category')

    parser = subparsers.add_parser('ths')
    ths.add_arguments(parser)
    parser = subparsers.add_parser('tdx')
    tdx.add_arguments(parser)

    args = argparser.parse_args()

    if six.PY2:
        sys.stdout = codecs.getwriter(args.encoding)(sys.stdout)

    if args.category == 'ths':
        ths.exec_args(args)
    elif args.category == 'tdx':
        tdx.exec_args(args)
    else:
        argparser.print_help()


if __name__ == '__main__':
    main()
