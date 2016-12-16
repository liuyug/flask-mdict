#!/usr/bin/env python
# -*- encoding:utf-8 -*-

import datetime

from ..formula import last_year_end


def yylr_lrze(stock):
    """ 营业利润/利润总额 """
    values = {}
    benefits = stock.Benefits
    for benefit in benefits:
        date = benefit.date
        yylr = benefit.yylr
        lrze = benefit.lrze
        if yylr is not None and lrze is not None:
            values[date] = yylr * 100.0 / lrze
    return values


def tzsy_lrze(stock):
    """ 投资收益/利润总额 """
    values = {}
    benefits = stock.Benefits
    for benefit in benefits:
        date = benefit.date
        tzsy = benefit.tzsy
        lrze = benefit.lrze
        if tzsy is not None and lrze is not None:
            values[date] = tzsy * 100.0 / lrze
    return values


def yywlr_lrze(stock):
    """ 营业外利润/利润总额 """
    values = {}
    benefits = stock.Benefits
    for benefit in benefits:
        date = benefit.date
        yywsr = benefit.yywsr
        yywzc = benefit.yywzc
        lrze = benefit.lrze
        if yywsr is not None and yywzc is not None and lrze is not None:
            values[date] = (yywsr - yywzc) * 100.0 / lrze
    return values


def zzcsyl(stock):
    """ 总资产收益率 """
    values = {}
    benefits = stock.Benefits
    debts = stock.Debts
    for benefit in benefits:
        date = benefit.date
        jlr = benefit.jlr
        last_date = last_year_end(date)
        zzc = last_zzc = None
        for debt in debts:
            if debt.date == date:
                zzc = debt.zzc
            if debt.date == last_date:
                last_zzc = debt.zzc
                break
        if jlr is not None and zzc is not None and last_zzc is not None:
            values[date] = jlr * 100.0 * 2 / (zzc + last_zzc)
    return values


def zczzl(stock):
    """ 资产周转率 """
    values = {}
    benefits = stock.Benefits
    debts = stock.Debts
    for benefit in benefits:
        date = benefit.date
        yysr = benefit.yysr
        last_date = last_year_end(date)
        zzc = last_zzc = None
        for debt in debts:
            if debt.date == date:
                zzc = debt.zzc
            if debt.date == last_date:
                last_zzc = debt.zzc
                break
        if yysr is not None and zzc is not None and last_zzc is not None:
            values[date] = yysr * 100.0 * 2 / (zzc + last_zzc)
    return values


def xsjll(stock):
    """ 销售净利率 """
    values = {}
    benefits = stock.Benefits
    for benefit in benefits:
        date = benefit.date
        jlr = benefit.jlr
        yysr = benefit.yysr
        if jlr is not None and yysr is not None:
            values[date] = jlr * 100.0 / yysr
    return values


def xsfyl(stock):
    """ 销售费用率 """
    values = {}
    benefits = stock.Benefits
    for benefit in benefits:
        date = benefit.date
        xsfy = benefit.xsfy
        yysr = benefit.yysr
        if xsfy is not None and yysr is not None:
            values[date] = xsfy * 100.0 / yysr
    return values


def mghbzj(stock):
    """ 每股货币资金 """
    values = {}
    debts = stock.Debts
    for debt in debts:
        date = debt.date
        hbzj = debt.hbzj
        gb = debt.gb
        if hbzj is not None and gb is not None:
            values[date] = hbzj / gb
    return values


def mgjlr(stock):
    """ 每股净利润 """
    values = {}
    benefits = stock.Benefits
    debts = stock.Debts
    for benefit in benefits:
        date = benefit.date
        jlr = benefit.jlr
        gb = None
        for debt in debts:
            if debt.date == date:
                gb = debt.gb
                break
        if jlr is not None and gb is not None:
            values[date] = jlr / gb
    return values


def mgjxjll(stock):
    """ 每股净现金流量 """
    values = {}
    cashs = stock.Cashs
    debts = stock.Debts
    for cash in cashs:
        date = cash.date
        jyxjllje = cash.jyxjllje
        gb = None
        for debt in debts:
            if debt.date == date:
                gb = debt.gb
                break
        if jyxjllje is not None and gb is not None:
            values[date] = jyxjllje / gb
    return values
