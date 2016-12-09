#!/usr/bin/env python
# -*- encoding:utf-8 -*-

from sqlalchemy import ForeignKey, Column, String, Date, Float
from sqlalchemy.orm import relationship, backref
from sqlalchemy.ext.declarative import declared_attr


class StockBase(object):
    __tablename__ = 'stock'

    mcode = Column(String, primary_key=True)
    name = Column(String)
    abbr = Column(String)

    date = Column(Date)
    zgb = Column(Float)
    ltgb = Column(Float)

    @declared_attr
    def market_code(cls):
        return Column(String, ForeignKey('market.code'))

    @declared_attr
    def market(cls):
        return relationship(
            'Market', backref=backref('stocks'),
        )

    @declared_attr
    def plate_code(cls):
        return Column(String, ForeignKey('plate.code'))

    @declared_attr
    def plate(cls):
        return relationship(
            'Plate', backref=backref('stocks'),
        )

    def __repr__(self):
        return '<code: %s>' % self.mcode


class MarketBase(object):
    __tablename__ = 'market'

    code = Column(String, primary_key=True)
    name = Column(String)

    def __repr__(self):
        return '<code: %s>' % self.code


class PlateBase(object):
    __tablename__ = 'plate'

    code = Column(String, primary_key=True)
    name = Column(String)

    def __repr__(self):
        return '<code: %s>' % self.code
