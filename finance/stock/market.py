#!/usr/bin/env python
# -*- encoding:utf-8 -*-

import logging

from ..database import get_session
from .model import Market


logger = logging.getLogger(__name__)

market_dict = dict([
    ('SHSZA', u'沪深A股'),
    ('SSE', u'沪市主板'),
    ('SZSE_MAIN', u'深市主板'),
    ('SZSE_SME', u'深市中小板'),
    ('SZSE_GEM', u'深市创业板'),
])


def create_market():
    Market.__table__.drop(get_session().get_bind(), checkfirst=True)
    Market.__table__.create(get_session().get_bind(), checkfirst=True)
    get_session().commit()

    for k, v in market_dict.items():
        if get_session().query(Market).filter_by(code=k.upper()).first():
            continue
        market = Market()
        market.code = k.upper()
        market.name = v
        logging.info('Add market: <%s: %s>' % (market.code, market.name))
        get_session().add(market)
    get_session().commit()


def get_market(code=None):
    if code is None:
        return get_session().query(Market).order_by(code).all()
    return get_session().query(Market).filter_by(code=code).first()
