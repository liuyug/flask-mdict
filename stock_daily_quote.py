#!/usr/bin/env python3
# -*- encoding:utf-8 -*-

import sys
import platform
import argparse

from stock.service.sina import sinahq
from stock.service.ths.quote import thshq
from stock.service.tencent import tencenthq

tdx_enable = False
if sys.platform == 'win32' and platform.architecture()[0] == '32bit':
    tdx_enable = True
    from stock.service.tdx.quote import tdxhq


def main():
    argparser = argparse.ArgumentParser(description='Stock HQ')

    subparsers = argparser.add_subparsers(help='hq category', dest='category')

    parser = subparsers.add_parser('ths')
    thshq.add_arguments(parser)

    if tdx_enable:
        parser = subparsers.add_parser('tdx')
        tdxhq.add_arguments(parser)

    parser = subparsers.add_parser('sina')
    sinahq.add_arguments(parser)

    parser = subparsers.add_parser('tencent')
    tencenthq.add_arguments(parser)

    args = argparser.parse_args()

    if args.category == 'ths':
        thshq.exec_args(args)
    elif tdx_enable and args.category == 'tdx':
        tdxhq.exec_args(args)
    elif args.category == 'sina':
        sinahq.exec_args(args)
    elif args.category == 'tencent':
        tencenthq.exec_args(args)
    else:
        argparser.print_help()


if __name__ == '__main__':
    main()
