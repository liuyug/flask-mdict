#!/usr/bin/env python3
# -*- encoding:utf-8 -*-

import sys
import platform
import argparse


if sys.platform == 'win32' and platform.architecture()[0] == '32bit':
    from stock.service.tdx.quote.tdx_dll import tdxhq
else:
    raise OSError('Please use Windows 32bit python...')


def main():
    argparser = argparse.ArgumentParser(description='Stock HQ')

    tdxhq.add_arguments(argparser)

    args = argparser.parse_args()

    tdxhq.exec_args(args)


if __name__ == '__main__':
    main()
