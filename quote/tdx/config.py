
import sys
from collections import OrderedDict


if sys.platform == 'win32':
    tdx_dir = 'c:\\new_tdx'
else:
    tdx_dir = ''


HQDATATYPE = OrderedDict((
    ('MCODE', -1),
    ('ZQMC', 1),
    ('OPEN', 5),
    ('PRE', 4),
    ('NEW', 3),
    ('HIGH', 6),
    ('LOW', 7),
    ('BUYPRICE', 17),
    ('SELLPRICE', 18),
    ('VOL', 10),
    ('MONEY', 12),
    ('BUYCOUNT1', 19),
    ('BUYPRICE1', 17),
    ('BUYCOUNT2', 23),
    ('BUYPRICE2', 21),
    ('BUYCOUNT3', 27),
    ('BUYPRICE3', 25),
    ('BUYCOUNT4', 31),
    ('BUYPRICE4', 29),
    ('BUYCOUNT5', 35),
    ('BUYPRICE5', 33),
    ('SELLCOUNT1', 20),
    ('SELLPRICE1', 18),
    ('SELLCOUNT2', 24),
    ('SELLPRICE2', 22),
    ('SELLCOUNT3', 28),
    ('SELLPRICE3', 26),
    ('SELLCOUNT4', 32),
    ('SELLPRICE4', 30),
    ('SELLCOUNT5', 36),
    ('SELLPRICE5', 34),
    ('DATE', -1),
    ('TIME', 8)
))
