#!/usr/bin/env python
# -*- encoding:utf-8 -*-

from sqlalchemy import Column, Sequence, \
    Date, Float, Integer, String, ForeignKey
from sqlalchemy.orm import relationship, backref
from sqlalchemy.ext.declarative import declared_attr

from .config import Benefit_field, Main_field, Cash_field, Debt_field, \
    FinanceModelDesc


class FinanceModel(object):
    _mapper = {}
    _report = {
        'Debt': Debt_field,
        'Cash': Cash_field,
        'Main': Main_field,
        'Benefit': Benefit_field,
    }

    @classmethod
    def model(cls, class_name):
        if class_name not in cls._report:
            return
        ModelClass = cls._mapper.get(class_name, None)
        if ModelClass is None:
            items = {}
            items['__module__'] = __name__
            items['__name__'] = '%sBase' % class_name
            items['__doc__'] = FinanceModelDesc[class_name]
            items['__tablename__'] = class_name.lower()
            items['__repr__'] = lambda x: '<%s>' % class_name
            items['_columns'] = {}
            items['id'] = Column(
                Integer,
                Sequence('%s_id_seq' % class_name.lower()),
                primary_key=True)

            for name, typ, desc, chart, unit in cls._report.get(class_name):
                if typ == 'DATE':
                    typ = 'Date'
                elif typ == 'REAL':
                    typ = 'Float'
                items[name] = Column(eval(typ))
                items['_columns'][name] = {
                    'name': name,
                    'typ': typ,
                    'desc': desc,
                    'chart': chart,
                    'unit': unit,
                }
            ModelClass = type(class_name, (object,), items)
            cls._mapper[class_name] = ModelClass
        return ModelClass


MainBaseBase = FinanceModel.model('Main')
DebtBaseBase = FinanceModel.model('Debt')
CashBaseBase = FinanceModel.model('Cash')
BenefitBaseBase = FinanceModel.model('Benefit')


class MainBase(MainBaseBase):
    __doc__ = MainBaseBase.__doc__

    @declared_attr
    def stock_mcode(cls):
        return Column(String, ForeignKey('stock.mcode'))

    @declared_attr
    def stock(cls):
        return relationship(
            'Stock', backref=backref('Mains'),
        )

    @classmethod
    def get_columns(cls):
        return cls._columns


class DebtBase(DebtBaseBase):
    __doc__ = DebtBaseBase.__doc__

    @declared_attr
    def stock_mcode(cls):
        return Column(String, ForeignKey('stock.mcode'))

    @declared_attr
    def stock(cls):
        return relationship(
            'Stock', backref=backref('Debts'),
        )

    @classmethod
    def get_columns(cls):
        return cls._columns


class CashBase(CashBaseBase):
    __doc__ = CashBaseBase.__doc__

    @declared_attr
    def stock_mcode(cls):
        return Column(String, ForeignKey('stock.mcode'))

    @declared_attr
    def stock(cls):
        return relationship(
            'Stock', backref=backref('Cashs'),
        )

    @classmethod
    def get_columns(cls):
        return cls._columns


class BenefitBase(BenefitBaseBase):
    __doc__ = BenefitBaseBase.__doc__

    @declared_attr
    def stock_mcode(cls):
        return Column(String, ForeignKey('stock.mcode'))

    @declared_attr
    def stock(cls):
        return relationship(
            'Stock', backref=backref('Benefits'),
        )

    @classmethod
    def get_columns(cls):
        return cls._columns


class PdfReportBase(object):
    __doc__ = 'PDF Report'
    __tablename__ = 'pdfreport'

    year = Column(String)
    period = Column(String(length=1))
    link = Column(String)

    def __repr__(self):
        return '<date: %s>' % self.date

    @declared_attr
    def stock_mcode(cls):
        return Column(String, ForeignKey('stock.mcode'))

    @declared_attr
    def stock(cls):
        return relationship(
            'Stock', backref=backref('Benefits'),
        )
