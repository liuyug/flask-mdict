#!/usr/bin/env python
# -*- encoding:utf-8 -*-
import sys
import os.path

common_path = os.path.abspath(os.path.join(
    os.path.dirname(__file__), '..', 'common'))

sys.path.append(common_path)

from common.finance.model_base import *

from ..database_base import Base


class Main(MainBase, Base):
    __doc__ = MainBase.__doc__


class Debt(DebtBase, Base):
    __doc__ = DebtBase.__doc__


class Cash(CashBase, Base):
    __doc__ = CashBase.__doc__


class Benefit(BenefitBase, Base):
    __doc__ = BenefitBase.__doc__
