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


def zzcjll(stock):
    """ 总资产净利率 """
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


def yyjll(stock):
    """ 营业净利率 """
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
