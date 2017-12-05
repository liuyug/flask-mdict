#!/usr/bin/env python
# -*- encoding:utf-8 -*-

import os
import os.path
import logging
import json
import datetime

import xlrd

from ..utils import url_downloader
from ..config import get_config

from . import config


logger = logging.getLogger(__name__)


def download_finance_data(mcode, report='all', typ='json', overwrite=False):
    """ typ: xls or json """
    base_dir = get_config().get('general', 'base_dir')

    finance_dir = os.path.join(base_dir, 'finance_report')
    if not os.path.exists(finance_dir):
        os.makedirs(finance_dir)

    if typ == 'json':
        url_map = config.json_url_map
    elif typ == 'xls':
        url_map = config.xls_url_map
    else:
        return

    if report == 'all':
        reports = url_map.keys()
    else:
        reports = [report]

    for report in reports:
        path = os.path.join(finance_dir, '%s-%s.%s' % (mcode, report, typ))
        if os.path.exists(path):
            if overwrite:
                os.remove(path)
            else:
                continue
        url = url_map[report] % {'stock': mcode[2:]}
        logger.info('Download %s %s ...\t%s' % (
            mcode, report, os.path.basename(path)))
        url_downloader(url, path=path, retry=3)


def get_report_from_xls(mcode, report='all'):
    base_dir = get_config().get('general', 'base_dir')
    finance_dir = os.path.join(base_dir, 'finance_report')

    if report == 'all':
        reports = config.xls_url_map.keys()
    else:
        reports = [report]

    report_data = {}
    for report in reports:
        logger.info('Convert %s - %s into db...' % (mcode, report))
        xls_path = os.path.join(finance_dir, '%s-%s.xls' % (mcode, report))
        # excel
        try:
            book = xlrd.open_workbook(xls_path)
        except Exception as err:
            logger.error(err)
            os.remove(xls_path)
            return

        sheet = book.sheet_by_index(0)
        header = [u'日期'] + sheet.col_values(0)[1:]
        data = [header]

        for i in range(1, sheet.ncols):
            record = []
            date = datetime.datetime.strptime(sheet.col_values(i)[0], '%Y-%m-%d')
            record.append(date)
            for x in range(1, len(header)):
                record.append(sheet.col_values(i)[x])
            data.append(record)
        report_data[report] = data
    return report_data


def get_report_from_json(mcode, report='all'):
    base_dir = get_config().get('general', 'base_dir')
    finance_dir = os.path.join(base_dir, 'finance_report')

    if report == 'all':
        reports = config.json_url_map.keys()
    else:
        reports = [report]

    report_data = {}
    for report in reports:
        json_path = os.path.join(finance_dir, '%s-%s.json' % (mcode, report))
        try:
            json_data = json.load(open(json_path))
        except Exception as err:
            if os.path.exists(json_path):
                os.remove(json_path)
            logger.error(err)
            continue
        header = [u'日期'] + json_data['title'][1:]
        data = [header]
        for i in range(len(json_data['report'][0])):
            record = []
            date = datetime.datetime.strptime(json_data['report'][0][i], '%Y-%m-%d')
            record.append(date)
            for x in range(1, len(header)):
                record.append(json_data['report'][x][i])
            data.append(record)
        report_data[report] = data
    return report_data
