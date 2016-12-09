# import common package

import sys
import os.path

common_path = os.path.abspath(os.path.join(
    os.path.dirname(__file__), '..', 'common'))

sys.path.append(common_path)

from common.utils import *
