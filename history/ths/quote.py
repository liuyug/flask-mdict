
import os.path
import struct
from datetime import datetime


from .config import ths_dir


def load_history_data(hpath):
    """parse ths history data
    """
    datatype = dict([
        (1, 'date'),
        (7, 'open'),
        (8, 'high'),
        (9, 'low'),
        (11, 'close'),
        (19, 'money'),
        (13, 'vol'),
        (14, 'outvol'),
        (15, 'invol'),
        (17, 'openvol'),
        (18, 'volamount'),
        (80, 'yjlx'),
        (231, 'buytick'),
        (232, 'selltick'),
        (122, 'avgbuyprice'),
        (123, 'allbuycount'),
        (124, 'avgsellprice'),
        (125, 'allsellcount'),
        (201, 'bigbuycount1'),
        (202, 'bigsellcount1'),
        (203, 'bigbuycount2'),
        (204, 'bigsellcount2'),
        (205, 'bigbuycount3'),
        (206, 'bigsellcount3'),
        (207, 'waitbuycount1'),
        (208, 'waitsellcount1'),
        (209, 'waitbuycount2'),
        (210, 'waitsellcount2'),
        (211, 'waitbuycount3'),
        (212, 'waitsellcount3'),
        (223, 'bigbuymoney1'),
        (224, 'bigsellmony1'),
        (225, 'bigbuymony2'),
        (226, 'bigsellmony2'),
        (227, 'waitbuymoney1'),
        (228, 'waitsellmoney1'),
        (229, 'waitbuymoney2'),
        (230, 'waitsellmoney2'),
        (3, 'codetype'),
        (4, 'n/a'),
        (5, 'code'),
        (6, 'pre'),
    ])

    if not os.path.exists(hpath):
        raise OSError('could not find file: %s' % hpath)
    f = open(hpath, 'rb')
    tag, = struct.unpack('<6s', f.read(6))
    if tag != b'hd1.0\x00':
        raise Exception('%s header error' % hpath)
    row, offset, size, column = struct.unpack('<LHHH', f.read(10))
    data = []
    header = []
    for x in range(column):
        B = struct.unpack('<4B', f.read(4))
        # other 3B, unknown
        header.append(datatype.get(B[0]))
    for y in range(row):
        d = []
        B = struct.unpack('<%dL' % column, f.read(size))
        for x in range(column):
            if B[x] == 0xFFFFFFFF:
                continue
            if header[x] == 'date':
                value = datetime.strptime('%s' % B[0], '%Y%m%d').date()
            else:
                v = B[x] & 0x0fffffff
                sign = -1 if (B[x] >> 31) == 1 else 1
                power = (B[x] >> 28 & 0b0111) * sign
                value = 10 ** power * v
            d.append((header[x], value))
        data.append(dict(d))
    f.close()
    data.sort(key=lambda x: x['date'], reverse=True)
    return {'header': header, 'data': data}


def add_arguments(parser):
    parser.add_argument('--directory', dest='ths_dir', default=ths_dir, help='THS Software directory')

    parser.add_argument('--period', choices=['day', 'min', 'min5'], help='HQ data with hq-datatype')
    parser.add_argument('mcode', nargs='+', help='Stock code, SH600000')


def exec_args(args):
    for mcode in args.mcode:
        mcode = mcode.upper()
        if mcode.startswith('SH'):
            market_path = 'shase'
        elif mcode.startswith('SZ'):
            market_path = 'sznse'
        else:
            market_path = ''
        filename = '%s.%s' % (mcode[2:], args.period)
        hpath = os.path.join(
            args.ths_dir, 'history', market_path, args.period, filename)
        data = load_history_data(hpath)
        if data['data']:
            fmt = '\n'.join(['%s: %%(%s)s' % (h, h) for h in data['header'][:7]])
            for d in data['data']:
                print(fmt % d)
