#!/usr/bin/env python
# -*- encoding:utf-8 -*-

from ..formula import last_year_end


def average_zzc(stock):
    debts = stock.Debts.all()
    values = {}
    for debt in debts:
        date = debt.date
        values[date] = debt.zzc
    for date in values:
        zzc = values.get(date)
        if not zzc:
            continue
        last_date = last_year_end(date)
        last_zzc = values.get(last_date)
        if last_zzc:
            values[date] = (values[date] + last_zzc) * 1.0 / 2
    return values


def zyywlr_lrze(stock):
    """ 主营业务利润/利润总额 """
    values = {}
    benefits = stock.Benefits
    for benefit in benefits:
        date = benefit.date
        yyzsr = benefit.yyzsr
        yyzcb = benefit.yyzcb
        lrze = benefit.lrze
        if yyzsr is not None and yyzcb is not None and lrze is not None:
            values[date] = (yyzsr - yyzcb) * 100.0 / lrze
    return values


def qtywlr_lrze(stock):
    """ 其它业务利润/利润总额 """
    values = {}
    benefits = stock.Benefits
    for benefit in benefits:
        date = benefit.date
        yyzsr = benefit.yyzsr
        yyzcb = benefit.yyzcb
        tzsy = benefit.tzsy
        yylr = benefit.yylr
        lrze = benefit.lrze
        if yylr is not None and tzsy is not None and \
                yyzsr is not None and yyzcb is not None and lrze is not None:
            values[date] = (yylr - tzsy - (yyzsr - yyzcb)) * 100.0 / lrze
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


def jlrxjhl(stock):
    """ 净利润现金含量 """
    values = {}
    benefits = stock.Benefits
    cashs = stock.Cashs
    jyxjlljes = {}
    for cash in cashs:
        jyxjlljes[cash.date] = cash.jyxjllje
    for benefit in benefits:
        date = benefit.date
        jlr = benefit.jlr
        jyxjllje = jyxjlljes.get(date)
        if jyxjllje is not None and jlr is not None:
            values[date] = jyxjllje * 100.0 / jlr
    return values


def zzcsyl(stock):
    """ 总资产收益率 """
    values = {}
    benefits = stock.Benefits
    zzcs = average_zzc(stock)
    for benefit in benefits:
        date = benefit.date
        jlr = benefit.jlr
        zzc = zzcs.get(date)
        if jlr is not None and zzc is not None:
            values[date] = jlr * 100.0 / zzc
    return values


def zczzl(stock):
    """ 资产周转率 """
    values = {}
    benefits = stock.Benefits
    zzcs = average_zzc(stock)
    for benefit in benefits:
        date = benefit.date
        yysr = benefit.yysr
        zzc = zzcs.get(date)
        if yysr is not None and zzc is not None:
            values[date] = yysr * 100.0 / zzc
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
    gbs = {}
    for debt in stock.Debts:
        gbs[debt.date] = debt.gb
    for benefit in benefits:
        date = benefit.date
        jlr = benefit.jlr
        gb = gbs.get(date)
        if jlr is not None and gb is not None:
            values[date] = jlr / gb
    return values


def mgjxjll(stock):
    """ 每股净现金流量 """
    values = {}
    gbs = {}
    for debt in stock.Debts:
        gbs[debt.date] = debt.gb
    cashs = stock.Cashs
    for cash in cashs:
        date = cash.date
        jyxjllje = cash.jyxjllje
        tzxjllje = cash.tzxjllje
        czxjllje = cash.czxjllje
        xjllje = 0
        if jyxjllje is not None:
            xjllje += jyxjllje
        if tzxjllje is not None:
            xjllje += tzxjllje
        if czxjllje is not None:
            xjllje += czxjllje
        gb = gbs.get(date)
        if gb is not None:
            values[date] = xjllje / gb
    return values
