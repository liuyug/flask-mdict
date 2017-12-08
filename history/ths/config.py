# -*- encoding:utf-8 -*-

import os.path
import sys


quote_path = os.path.abspath(os.path.join(
    os.path.dirname(__file__), '..', 'quote'))

sys.path.append(quote_path)

from quote.ths.config import ths_dir
from quote.ths.helper import get_system_config

datatype_type = {
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
