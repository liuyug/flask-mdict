#!/usr/bin/env python
# -*- encoding:utf-8 -*-
import json
import logging
import struct

from six import BytesIO

from ..utils import url_downloader

from . import config

logger = logging.getLogger(__name__)


def get_news(mcode, typ=None):
    """
    mcode: SH600000
    typ: mine, pub
    """
    if typ is None:
        typ = ['mine', 'pub']
    elif isinstance(typ, str):
        typ = [typ]
    data = {}
    for t in typ:
        url = config.json_news[t] % {'stock': mcode[2:]}
        logger.info('Download %s %s...' % (mcode, t))
        response = url_downloader(url)
        if response['data'] is None:
            logger.error(response['error'])
            continue
        ret_data = response['data'].decode()
        if ret_data[:7] == 'success':
            data[t] = json.loads(ret_data[7:])
    return data


def load_selected_stock(fobj):
    """
    file format:
    pos length  desc
    0   2       number
    ...  stock list ...
    0   1       total length of type and code
    1   1       stock type
    2   6?      stock code
    """
    count, = struct.unpack('<H', fobj.read(2))
    for i in range(count):
        ll, = struct.unpack('<B', fobj.read(1))
        typ, code = struct.unpack('<B%ds' % (ll - 1), fobj.read(ll))
        yield '%s%s' % (config.market_id[typ], code)


def dump_selected_stock(stocks):
    fobj = BytesIO()
    fobj.write(struct.pack('<H', len(stocks)))
    for stock in stocks:
        typ = config.market_id[stock.mcode[:2]]
        fobj.write(struct.pack('<BB%ds' % len(stock.mcode[2:]),
                            len(stock.mcode[2:]) + 1,
                            typ,
                            stock.mcode[2:].encode()))
    return fobj
