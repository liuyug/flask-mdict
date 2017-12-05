#!/usr/bin/env python
# -*- encoding:utf-8 -*-

import os.path
import logging
import json

from bs4 import BeautifulSoup
from six.moves.configparser import ConfigParser

from ..utils import url_downloader

from .config import ths_dir


logger = logging.getLogger(__name__)


def create_plate_from_local():
    """
    Create plate from ths local data
    """
    plate_path = os.path.join(ths_dir, 'industry.ini')
    if not os.path.exists(plate_path):
        raise TypeError('could not find directory: %s' % plate_path)
    plate_config = ConfigParser()
    plate_config.read(plate_path)
    plates = []
    for code, name in plate_config.items('name'):
        plates.append((
            code,
            name.decode('gbk').split(';')[0],
            plate_config.get('industry', code).split(','),
        ))
    return plates


def create_plate_from_site():
    """
    http://q.10jqka.com.cn/thshy/
    http://q.10jqka.com.cn/thshy/detail/field/199112/order/desc/page/1/ajax/1/code/881121
    http://q.10jqka.com.cn/gn/
    http://q.10jqka.com.cn/dy/
    """
    # get all plate
    urls = {
        'thshy': {
            'name': u'同花顺行业',
            'url': 'http://q.10jqka.com.cn/thshy/',
        },
        'gn': {
            'name': u'概念板块',
            'url': 'http://q.10jqka.com.cn/gn/',
        },
        'dy': {
            'name': u'地域板块',
            'url': 'http://q.10jqka.com.cn/dy/',
        },
    }
    plates = {}
    for key, url in urls.items():
        response = url_downloader(url['url'], retry=3)
        data = response['data']
        if data is None:
            logger.warn(response['error'])
            return
        soup = BeautifulSoup(data.decode('gbk'), "html5lib")
        tags = soup.find_all('div', class_='cate_items')
        plates[key] = []
        for tag in tags:
            for item in tag.find_all('a'):
                plate = {}
                plate['plate_category'] = key
                plate['plate_category_name'] = url['name']
                plate['code'] = item['href'].split('/')[-2]
                plate['name'] = item.get_text(strip=True)
                plate['stock'] = []
                plates[key].append(plate)
        logger.info('find %s %s(%s) plates' % (
            len(plates[key]), url['name'], key))
    # get stock code for plate
    base_url = 'http://q.10jqka.com.cn/%s/detail/field/199112/order/desc/page/%s/ajax/1/code/%s'
    for key, items in plates.items():
        logger.info('fetch "%s(%s)" plate:' % (urls[key]['name'], key))
        for plate in items:
            url = base_url % (key, 1, plate['code'])
            response = url_downloader(url, retry=3)
            data = response['data']
            if data is None:
                logger.warn(response['error'])
                return
            soup = BeautifulSoup(data.decode('gbk'), "html5lib")
            # find total page number
            tag = soup.find('span', class_='page_info')
            if tag:
                page_info = tag.get_text(strip=True)
                page_max = int(page_info.split('/')[-1])
            else:
                page_max = 1
            # find stock code
            codes = []
            # 1 page
            table = soup.find('table', class_='m-table')
            for tr in table.find_all('tr')[1:]:
                td = tr.find('td').find_next_sibling('td')
                codes.append(td.get_text(strip=True))
            # other page
            for page in range(1, page_max):
                page += 1
                url = base_url % (key, page, plate['code'])
                response = url_downloader(url, retry=3)
                data = response['data']
                if data is None:
                    logger.warn(response['error'])
                    return
                soup = BeautifulSoup(data.decode('gbk'), "html5lib")

                table = soup.find('table', class_='m-table')
                for tr in table.find_all('tr')[1:]:
                    td = tr.find('td').find_next_sibling('td')
                    if not td:
                        break
                    codes.append(td.get_text(strip=True))
            plate['stock'] = codes
            logger.info('[%s] %s : %s stocks' % (
                plate['code'], plate['name'], len(plate['stock'])))
    return plates


def create_plate_from_site_2():
    """
    Create plate from ths site
    http://q.10jqka.com.cn/stock/thshy/
    http://q.10jqka.com.cn/interface/stock/thshy/zdf/desc/1/quote/quote
    """
    plates = {}
    for i in range(1, 10):
        url = 'http://q.10jqka.com.cn/interface/stock/thshy/zdf/desc/%d/quote/quote' % i
        logger.debug('Download plate list(%d)...' % i)
        response = url_downloader(url, retry=3)
        if response['data'] is None:
            logger.warn(response['error'])
            continue
        plate_data = json.loads(response['data'].decode('utf8'))
        if plate_data['data'] is None:
            break
        for plate in plate_data['data']:
            stock_num = int(plate['num'])
            plate_hycode = plate['hycode']
            plate_code = plate['platecode']
            plate_name = plate['platename']
            code_list = []
            page = stock_num / 50 + 1
            logger.info('Download plate %s(%d) ...' % (plate_name, stock_num))
            for p in range(1, page + 1):
                url = 'http://q.10jqka.com.cn/interface/stock/detail/zdf/desc/%d/1/%s' % (
                    p,
                    plate_hycode,
                )
                logger.debug('Download plate %s(%d) detail(%d/%d)...' % (
                    plate_name, stock_num, p, page))
                response = url_downloader(url, retry=3)
                if response['data'] is None:
                    logger.warn(response['error'])
                    continue
                stock_data = json.loads(response['data'].decode('utf8'))
                if stock_data['data'] is None:
                    break
                for stock in stock_data['data']:
                    code_list.append(stock['stockcode'])
            if plate_code in plates:
                logger.warn('Merge duplicated plate: %s %s' % (plate_code, plate_name))
                code_list = list(set(plates[plate_code][2]) | set(code_list))
            plates[plate_code] = (plate_code, plate_name, code_list)
    return list(plates.values())
