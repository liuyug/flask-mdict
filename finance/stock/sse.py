#!/usr/bin/env python
# -*- encoding:utf-8 -*-
#
# Refer:
# http://bluegene8210.is-programmer.com/posts/37986.html
# https://github.com/kongscn/pyshow
#
# stock list in Shanghai Security Exchange
# http referer: http://www.sse.com.cn
# http://www.sse.com.cn/assortment/stock/list/share/
# excel file:
# http://query.sse.com.cn/security/stock/downloadStockListFile.do?csrcCode=&stockCode=&areaName=&stockType=1

#
# Get stock list with curl
# curl --referer http://www.sse.com.cn http://query.sse.com.cn/commonQuery.do?sqlId=COMMON_SSE_ZQPZ_GPLB_MCJS_SSAG_L
# Get year report
# http://www.sse.com.cn/disclosure/announcement/regular/
# curl --referer http://www.sse.com.cn "http://query.sse.com.cn/infodisplay/queryBltnBookInfo.do?bulletintype=L011&cmpCode=600035&publishYear=2014"

import json
import logging
import os.path
import datetime

from six.moves.urllib.request import urlopen, Request
from six.moves.urllib.parse import urlencode

from ..config import get_config
from ..utils import url_downloader


logger = logging.getLogger(__name__)


sse_market = {
    'stock': {
        'default': '股票',
        'A': '上市A股',
        'B': '上市B股',
        'IPO': '首次发型待上市股票',
        'Pause': '暂停上市股票',
        'Quit': '终止上市',
    },
    'fund': {
        'default': '基金',
    },
    'bond': {
        'default': '债券',
        'T': '国债列表',
        'M': '地方债',
        'C': '公司债企业债',
        'Tr': '可转换债',
        'R': '债券回购',
        'S': '分离债列表',
    },
    'derivative': {
        'default': '衍生品',
    }
}


def download_stocks_csv(csv_path):
    url = 'http://query.sse.com.cn/security/stock/downloadStockListFile.do?csrcCode=&stockCode=&areaName=&stockType=1'
    referer = 'http://www.sse.com.cn'
    return url_downloader(url, path=csv_path, referer=referer)


def get_stocks():
    """
    股本单位: 万股
    """
    base_dir = get_config().get('general', 'base_dir')
    csv_path = os.path.join(base_dir, 'sha.csv')
    encoding = 'gbk'
    response = download_stocks_csv(csv_path)
    data = []
    if not response['path']:
        logger.error(response['error'])
        logger.error(response['url'])
        return data
    header = [
        u'A股代码',
        u'A股简称',
        u'A股上市日期',
        u'A股总股本',
        u'A股流通股本',
    ]

    lines = []
    with open(csv_path, 'rU') as f:
        lines = f.read().decode(encoding).split('\n')
    data.append(header)
    csv_header = [l.strip() for l in lines[0].split('\t')]
    header_index = [csv_header.index(h) for h in header]
    for line in lines[1:]:
        line.strip()
        if not line:
            continue
        rows = line.split('\t')
        data.append([
            'SH%s' % rows[header_index[0]].strip(),
            rows[header_index[1]].strip(),
            datetime.datetime.strptime(rows[header_index[2]].strip(), '%Y-%m-%d').date(),
            float(rows[header_index[3]].strip()) * 10000.0,
            float(rows[header_index[4]].strip()) * 10000.0,
        ])
    return data


def _querysse(url, headers={}, **values):
    referer = 'http://www.sse.com.cn/'
    data = urlencode(values)
    data = data.encode('utf-8')  # data should be bytes
    req = Request(url, data)
    req.add_header('Referer', referer)
    req.headers.update(headers)
    content = urlopen(req).read()
    reply = json.loads(content.decode('utf-8'))
    return reply['result']


def get_company_info(code):
    """
    Get details of a company by company code.
    :param code: company code
    """
    url = 'http://query.sse.com.cn/commonQuery.do'
    logging.info('Download stock info from SSE(%s) site...' % code)
    reply = _querysse(url, sqlId='COMMON_SSE_ZQPZ_GP_GPLB_C', productid=code)
    return reply


def get_stock_list(category='A'):
    """
    Get stock code list of a specific type
    :param category: Can be A, B, IPO, Pause, or Quit, case sensitive.
    SSAG    A股
    SSBG    B股
    SCFXDSSGP   首次发型待上市股票
    ZTSSGS  暂停上市股票
    ZZSSGGJBXX  终止上市
    """
    category_code = {'A': 'SSAG',
                     'B': 'SSBG',
                     'IPO': 'SCFXDSSGP',
                     'Pause': 'ZTSSGS',
                     'Quit': 'ZZSSGGJBXX'}
    sqlid = 'COMMON_SSE_ZQPZ_GPLB_MCJS_%s_L' % category_code[category]
    url = 'http://query.sse.com.cn/commonQuery.do'
    logging.info('Download stock list from SSE(%s) site...' % category)
    reply = _querysse(url, sqlId=sqlid)
    return reply


def get_fund_list():
    """
    基金
    """
    sqlid = 'COMMON_SSE_ZQPZ_JJLB_L'
    url = 'http://query.sse.com.cn/commonQuery.do'
    reply = _querysse(url, sqlId=sqlid)
    return reply


def get_bond_list(category='T'):
    """
    债券
    GZLB  国债列表
    DFZLB  地方债
    GSZQYZLB  公司债企业债
    KZHZLB 可转换债
    ZQHGLB 债券回购
    FLZLB 分离债列表
    """
    category_code = {'T': 'COMMON_SSE_ZQPZ_ZQLB_GZLB_L',
                     'M': 'COMMON_SSE_ZQPZ_ZQLB_DFZLB_L',
                     'C': 'COMMON_SSE_ZQPZ_ZQLB_GSZQYZLB_L',
                     'Tr': 'COMMON_SSE_ZQPZ_ZQLB_KZHZLB_L',
                     'R': 'COMMON_SSE_ZQPZ_ZQLB_ZQHGLB_L',
                     'S': 'COMMON_SSE_ZQPZ_ZQLB_FLZLB_L'}
    sqlid = category_code[category]
    url = 'http://query.sse.com.cn/commonQuery.do'
    reply = _querysse(url, sqlId=sqlid)
    return reply


def get_derivative_list():
    sqlid = 'COMMON_SSE_ZQPZ_QZ_QZLB_YDQ_L'
    url = 'http://query.sse.com.cn/commonQuery.do'
    reply = _querysse(url, sqlId=sqlid)
    return reply


def get_period_announcement_date(market, code, period):
    """
    period: 0:1Q 1:2Q 2:3Q 3:4Q
    """
    period_param = ['L013', 'L012', 'L014', 'L011']
    url = 'http://query.sse.com.cn/infodisplay/queryBltnBookInfo.do'
    now = datetime.date.today()
    year = now.year
    if period == 3 and now.month < 6:
        year -= 1
    kwargs = {
        'publishYear': year,
        'bulletintype': period_param[period],
        'cmpCode': code,
    }
    logging.debug('Get period announcement date from SSE site...%s' % code)
    reply = _querysse(url, **kwargs)
    if not reply:
        return None
    data = reply[0]
    if data['actualDate']:
        return data['actualDate']
    elif data['publishDate3']:
        return data['publishDate3']
    elif data['publishDate2']:
        return data['publishDate2']
    elif data['publishDate1']:
        return data['publishDate1']
    return data['publishDate0']


if __name__ == '__main__':
    stocks = get_stock_list()
    for stock in stocks:
        for k, v in stock.items():
            print('%s: %s' % (k, v))
        print('-' * 80)
    info = get_company_info('600000')
    for i in info:
        for k, v in i.items():
            print('%s: %s' % (k, v))
        print('-' * 80)
