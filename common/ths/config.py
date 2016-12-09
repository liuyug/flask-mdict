#!/usr/bin/env python
# -*- encoding:utf-8 -*-

market_id = {
    17: 'SH',
    'SH': 17,
    33: 'SZ',
    'SZ': 33,
}


json_news = {
    # 新闻
    'mine': "http://basic.10jqka.com.cn/ajax/code/%(stock)s/type/mine",
    # 公告
    'pub': "http://basic.10jqka.com.cn/ajax/code/%(stock)s/type/pub",
}
