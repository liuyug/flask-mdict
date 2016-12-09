#!/usr/bin/env python
# -*- encoding:utf-8 -*-

import datetime


def next_yoy_date(date):
    return datetime.date(date.year - 1, date.month, date.day)


def next_mom_date(date):
    year = date.year
    month = date.month
    if month == 3:
        year -= 1
        month = 12
        day = 31
    else:
        month -= 3
        if month in [3, 12]:
            day = 31
        else:
            day = 30
    return datetime.date(year, month, day)


def last_year_end(date):
    return datetime.date(date.year - 1, 12, 31)


def yoy(values):
    new_values = {}
    for date in values:
        next_date = next_yoy_date(date)
        if next_date in values \
                and values[date] is not None \
                and values[next_date] is not None:
            if values[next_date] != 0:
                new_values[date] = (values[date] - values[next_date]) \
                    * 100.0 / values[next_date]
    return new_values


def mom(values):
    new_values = {}
    for date in values:
        next_date = next_mom_date(date)
        next_next_date = next_mom_date(next_date)
        if next_date in values and next_next_date in values \
                and values[date] is not None \
                and values[next_date] is not None \
                and values[next_next_date] is not None:
            if date.month == 3:
                v1 = values[date]
            else:
                v1 = values[date] - values[next_date]
            if next_date.month == 3:
                v2 = values[next_date]
            else:
                v2 = values[next_date] - values[next_next_date]
            if v2 != 0:
                new_values[date] = (v1 - v2) * 100.0 / v2
    return new_values


def calc_pe(code, price):
    """
    pe_list:
    0: LYR  1: LYR
    2: TTM  3: TTM
    4: 动   5: 动
    """
    pass
    # row = db_session.query(
    #     Benefit.model(code).date,
    #     Benefit.model(code).jlr,
    #     Benefit.model(code).lrze,
    #     Benefit.model(code).sds,
    # ).order_by(Benefit.model(code).date.desc()).first()
    # if not row:
    #     return None
    # cur_date = row[0]
    # cur_jlr = row[1]
    # cur_total_jlr = row[2] - row[3]

    # row = db_session.query(Debt.model(code).gb).filter_by(date=cur_date).first()
    # cur_gb = row[0] or 0
    # if cur_date.month < 12:
    #     last_year = cur_date.year - 1
    # else:
    #     last_year = cur_date.year

    # row = db_session.query(
    #     Benefit.model(code).jlr,
    #     Benefit.model(code).lrze,
    #     Benefit.model(code).sds,
    # ).filter_by(date=datetime.datetime(last_year, 12, 31)).first()
    # last_year_jlr = row[0]
    # last_year_total_jlr = row[1] - row[2]

    # row = db_session.query(
    #     Debt.model(code).gb
    # ).filter_by(date=datetime.datetime(last_year, 12, 31)).first()
    # last_year_gb = row[0] or 0

    # row = db_session.query(
    #     Benefit.model(code).jlr,
    #     Benefit.model(code).lrze,
    #     Benefit.model(code).sds,
    # ).filter_by(date=datetime.datetime(last_year, cur_date.month, cur_date.day)).first()
    # yoy_jlr = row[0]
    # yoy_total_jlr = row[1] - row[2]
    # pe_list = []
    # if last_year_jlr and last_year_gb:
    #     pe = price / (last_year_jlr / last_year_gb)
    # else:
    #     pe = None
    # pe_list.append(pe)
    # if last_year_jlr and cur_gb:
    #     pe = price * cur_gb / last_year_jlr
    # else:
    #     pe = None
    # pe_list.append(pe)
    # if last_year_gb and cur_gb:
    #     pe = price / (cur_jlr / cur_gb + (last_year_jlr - yoy_jlr) / last_year_gb)
    # else:
    #     pe = None
    # pe_list.append(pe)
    # if cur_gb:
    #     pe = price * cur_gb / (cur_jlr + last_year_jlr - yoy_jlr)
    # else:
    #     pe = None
    # pe_list.append(pe)
    # if cur_gb:
    #     pe = price / (cur_jlr / cur_gb / (cur_date.month / 3) * 4)
    # else:
    #     pe = None
    # pe_list.append(pe)
    # if cur_gb:
    #     pe = price * cur_gb / (cur_jlr / (cur_date.month / 3) * 4)
    # else:
    #     pe = None
    # pe_list.append(pe)
    # # total jlr
    # if last_year_gb:
    #     pe = price / (last_year_total_jlr / last_year_gb)
    # else:
    #     pe = None
    # pe_list.append(pe)
    # pe = price * cur_gb / last_year_total_jlr
    # pe_list.append(pe)
    # if last_year_gb:
    #     pe = price / (cur_total_jlr / cur_gb + (last_year_total_jlr - yoy_total_jlr) / last_year_gb)
    # else:
    #     pe = None
    # pe_list.append(pe)
    # if cur_gb:
    #     pe = price * cur_gb / (cur_total_jlr + last_year_total_jlr - yoy_total_jlr)
    # else:
    #     pe = None
    # pe_list.append(pe)
    # if cur_gb:
    #     pe = price / (cur_total_jlr / cur_gb / (cur_date.month / 3) * 4)
    # else:
    #     pe = None
    # pe_list.append(pe)
    # if cur_gb:
    #     pe = price * cur_gb / (cur_total_jlr / (cur_date.month / 3) * 4)
    # else:
    #     pe = None
    # pe_list.append(pe)
    # return pe_list


def calc_pb(code, price):
    """
    pb
    """
    pass
    # r = db_session.query(Main.model(code)).order_by(Main.model(code).date.desc()).first()
    # if r and r.mgjzc > 0.0:
    #     return price / r.mgjzc
    # return None


def get_announcement_period(now):
    """
    now: datetime.date type. It's current date.
    """
    year = now.year
    period = 0
    if now.month < 5:
        period = 3
        year -= 1
    elif now.month < 6:
        period = 0
    elif now.month < 9:
        period = 1
    elif now.month < 11:
        period = 2
    return (year, period)


def get_gb_desc(gb):
    if gb < 9999:
        return '小盘股'
    elif gb < 99999:
        return '中盘股'
    else:
        return '大盘股'
