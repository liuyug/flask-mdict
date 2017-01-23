#!/usr/bin/env python3
# -*- encoding:utf-8 -*-

import sys
import codecs
import argparse

import six

from server.hq.sina import sinahq
from server.hq.ths import thshq
from server.hq.leverfun import leverfunhq
from server.hq.tencent import tencenthq

if sys.platform == 'win32':
    from server.hq.tdx import tdxhq


def main():
    argparser = argparse.ArgumentParser(description='Stock HQ')
    argparser.add_argument('--encoding', default='utf8', help='terminal character encoding')

    subparsers = argparser.add_subparsers(help='hq category', dest='category')

    parser = subparsers.add_parser('ths')
    thshq.add_arguments(parser)

    if sys.platform == 'win32':
        parser = subparsers.add_parser('tdx')
        tdxhq.add_arguments(parser)

    parser = subparsers.add_parser('sina')
    sinahq.add_arguments(parser)

    parser = subparsers.add_parser('leverfun')
    leverfunhq.add_arguments(parser)

    parser = subparsers.add_parser('tencent')
    tencenthq.add_arguments(parser)

    args = argparser.parse_args()

    if six.PY2:
        sys.stdout = codecs.getwriter(args.encoding)(sys.stdout)

    if args.category == 'ths':
        thshq.exec_args(args)
    elif sys.platform == 'win32' and args.category == 'tdx':
        tdxhq.exec_args(args)
    elif args.category == 'sina':
        sinahq.exec_args(args)
    elif args.category == 'leverfun':
        leverfunhq.exec_args(args)
    elif args.category == 'tencent':
        tencenthq.exec_args(args)


if __name__ == '__main__':
    main()
