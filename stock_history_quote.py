#!/usr/bin/env python3
# -*- encoding:utf-8 -*-

import argparse

from stock.service.ths.local import quote as ths
from stock.service.tdx.local import quote as tdx


def main():
    argparser = argparse.ArgumentParser(description='History HQ')
    subparsers = argparser.add_subparsers(help='hq category', dest='category')

    parser = subparsers.add_parser('ths')
    ths.add_arguments(parser)
    parser = subparsers.add_parser('tdx')
    tdx.add_arguments(parser)

    args = argparser.parse_args()

    if args.category == 'ths':
        ths.exec_args(args)
    elif args.category == 'tdx':
        tdx.exec_args(args)
    else:
        argparser.print_help()


if __name__ == '__main__':
    main()
