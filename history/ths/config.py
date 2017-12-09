# -*- encoding:utf-8 -*-

import os.path
import sys


quote_path = os.path.abspath(os.path.join(
    os.path.dirname(__file__), '..', 'quote'))

sys.path.append(quote_path)

from quote.ths.config import ths_dir
from quote.ths.helper import get_system_config


FINANCE_HISTORY = dict([
    (1, '财务附注.财经'),
    (2, '股本结构.财经'),
    (3, '股东户数.财经'),
    (4, '净资产收益率.财经'),
    (5, '利润分配.财经'),
    (6, '每股净资产.财经'),
    (7, '每股盈利.财经'),
    (8, '权息资料.财经'),
    (9, '现金流量.财经'),
    (10, '资产负债.财经'),
    (11, '自由流通股本.财经'),
    (12, '十大股东.财经'),
])


DATATYPE_FORMAT = {
    0: {  # default
        1: 'B',
        2: 'H',
        4: 'L',
        8: 'Q',
    },
    2: {  # char
        0: 's',
    },
    3: {  # integer
        2: 'H',
        4: 'L',
        8: 'Q',
    },
    5: {  # float
        4: 'f',
        8: 'd',
    },
    7: {  # ths float
        4: 'L',
    }
}
