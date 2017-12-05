# -*- encoding:utf-8 -*-

import os.path
import sys


quote_path = os.path.abspath(os.path.join(
    os.path.dirname(__file__), '..', 'quote'))

sys.path.append(quote_path)

from quote.ths.config import ths_dir
from quote.ths.helper import get_system_config
