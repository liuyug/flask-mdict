#!/usr/bin/env python
# -*- encoding:utf-8 -*-

import json
import logging

from ..utils import url_downloader


logger = logging.getLogger(__name__)


def get_pdf_report(mcode):
    base_url = 'http://www.cninfo.com.cn/cninfo-new/announcement/query'
    referer = 'http://www.cninfo.com.cn/'
    logger.debug('Get report links from CNINFO site...%s' % mcode[2:])
    category = {
        1: {
            'name': u'一季度报告(本年4月30日前发布)',
            'key': 'category_yjdbg_szsh',
        },
        2: {
            'name': u'中报(本年8月31日前发布)',
            'key': 'category_bndbg_szsh',
        },
        3: {
            'name': u'三季度报告(本年10月31日前发布)',
            'key': 'category_sjdbg_szsh',
        },
        4: {
            'name': u'年报(次年4月30前发布)',
            'key': 'category_ndbg_szsh',
        },
    }
    code = mcode[2:]
    if code.startswith('6'):
        market = 'sse'
    elif code.startswith('3'):
        market = 'szse_gem'
    elif code.startswith('002'):
        market = 'szse_sme'
    else:
        market = 'szse_main'

    post_data = {
        'stock': code,
        'category': '',
        'column': market,
        'tabName': 'fulltext',
    }
    report_data = {}
    for quarter, period in category.items():
        post_data['category'] = period['key']
        response = url_downloader(base_url, data=post_data, referer=referer)
        if response['data'] is None:
            logger.error(response['error'])
            return []
        json_data = json.loads(response['data'].decode('utf8'))
        for report in json_data['announcements']:
            if report['adjunctType'].lower() != 'pdf':
                continue
            if u'摘要' in report['announcementTitle']:
                continue
            if u'已取消' in report['announcementTitle']:
                continue
            year = report['announcementTitle'][:4]
            if not year.isdigit():
                continue
            if year not in report_data:
                report_data[year] = {}
            if report_data[year].get(quarter) and u'修订版' not in report['announcementTitle']:
                continue
            report_data[year][quarter] = referer + report['adjunctUrl']
    years = sorted(list(report_data.keys()), reverse=True)
    data = []
    data.append([u'年份'] + [v['name'] for v in category.values()])
    for year in years:
        data.append(
            [year] +
            [report_data[year].get(quarter) for quarter in category.keys()]
        )
    return data
