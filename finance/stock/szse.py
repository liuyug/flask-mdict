#!/usr/bin/env python
# -*- encoding:utf-8 -*-
#
# Shenzhen security exchange
# http://www.szse.cn/main/marketdata/jypz/colist/

import os
import os.path
import logging
import datetime

import xlrd
from six.moves.html_parser import HTMLParser

from ..config import get_config

from ..utils import url_downloader


logger = logging.getLogger(__name__)


def download_stocks_xlsx(xlsx_path):
    url = 'http://www.szse.cn/szseWeb/ShowReport.szse?SHOWTYPE=xlsx&CATALOGID=1110&tab2PAGENUM=1&ENCODE=1&TABKEY=tab2'
    referer = 'http://www.szse.cn'
    return url_downloader(url, path=xlsx_path, referer=referer)


def get_stocks():
    base_dir = get_config().get('general', 'base_dir')
    xlsx_path = os.path.join(base_dir, 'sza.xlsx')
    response = download_stocks_xlsx(xlsx_path)
    data = []
    if not response['path']:
        logger.error(response['error'])
        logger.error(response['url'])
        return data
    try:
        book = xlrd.open_workbook(xlsx_path)
    except Exception as err:
        logger.error(err)
        return
    sheet = book.sheet_by_index(0)
    header = [
        u'A股代码',
        u'A股简称',
        u'A股上市日期',
        u'A股总股本',
        u'A股流通股本',
    ]

    szse_header = sheet.row_values(0)
    header_index = [szse_header.index(h) for h in header]
    data.append(header)
    for row in range(1, sheet.nrows):
        values = sheet.row_values(row)
        data.append([
            'SZ%s' % values[header_index[0]],
            values[header_index[1]],
            datetime.datetime.strptime(values[header_index[2]], '%Y-%m-%d').date(),
            float(values[header_index[3]].replace(',', '')),
            float(values[header_index[4]].replace(',', '')),
        ])
    return data


def parse_stocklist_data(fp):
    class HtmlData(HTMLParser):
        line = []
        data = []
        ncol = 0
        table = False

        def handle_starttag(self, tag, attrs):
            if tag == 'table':
                for k, v in attrs:
                    if k == 'id' and v[:9] == 'REPORTID_':
                        self.table = True
                        break
            elif tag == 'tr':
                self.line = []
                self.ncol = 0

        def handle_endtag(self, tag):
            if tag == 'table':
                self.table = False
            elif self.table and tag == 'tr':
                self.data.append(self.line)

        def handle_data(self, data):
            if self.table and self.ncol < 2:
                self.line.append(data)
                self.ncol += 1

        def get_data(self):
            return self.data

    parser = HtmlData()
    parser.feed(fp.read())
    return parser.get_data()


def get_stock_list(category='A'):
    category_code = {
        'A': 'http://www.szse.cn/szseWeb/ShowReport.szse?SHOWTYPE=EXCEL&CATALOGID=1110&tab2PAGENUM=1&ENCODE=1&TABKEY=tab2',
        'B': 'http://www.szse.cn/szseWeb/ShowReport.szse?SHOWTYPE=EXCEL&CATALOGID=1110&tab3PAGENUM=1&ENCODE=1&TABKEY=tab3',
        # 中小板
        'SME': 'http://www.szse.cn/szseWeb/ShowReport.szse?SHOWTYPE=EXCEL&CATALOGID=1110&tab5PAGENUM=1&ENCODE=1&TABKEY=tab5',
        # 创业板
        'CN': 'http://www.szse.cn/szseWeb/ShowReport.szse?SHOWTYPE=EXCEL&CATALOGID=1110&tab6PAGENUM=1&ENCODE=1&TABKEY=tab6',
    }

    base_dir = get_config().get('general', 'base_dir')

    html_url = category_code[category]
    html_path = os.path.join(base_dir, 'SZ-%s.html' % category)
    logging.info('Download stock list from SZSE(%s) site...' % category)
    url_downloader(html_url, path=html_path)
    data = parse_stocklist_data(open(html_path))
    return data[1:]


if __name__ == '__main__':
    stocklist = get_stock_list()
    for stock in stocklist:
        print(stock)
