import os.path
import logging
import json

from six.moves.configparser import ConfigParser

from ..utils import url_downloader

from .config import ths_dir


logger = logging.getLogger(__name__)


def create_plate_from_local():
    """
    Create plate from ths local data
    """
    plate_path = os.path.join(ths_dir, 'industry.ini')
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
