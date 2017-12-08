
import os.path
import struct
from datetime import datetime


from .config import ths_dir, get_system_config, datatype_type


def decode_ths_time(ths_time):
    """
    ths time format:
    bit:    32     20     16   11      6     0
              year   month  day  hour  minute
    mask:     0xfff  0xf    0x1f 0x1f  0x3f
    """
    minute = ths_time & 0x3f
    hour = ths_time >> 6 & 0x1f
    day = ths_time >> 11 & 0x1f
    month = ths_time >> 16 & 0xf
    year = (ths_time >> 20 & 0xfff) + 1990
    return datetime(year, month, day, hour, minute)


def decode_ths_date(ths_date):
    if ths_date == 0xffffffff:
        return None
    return datetime.strptime(str(ths_date), '%Y%m%d').date()


def decode_ths_float(ths_float):
    """
    32   31     28           0
    sign  power   value
    """
    if ths_float == 0xffffffff:
        return float('nan')
    v = ths_float & 0x0fffffff
    sign = -1 if (ths_float >> 31) == 1 else 1
    power = (ths_float >> 28 & 0b0111) * sign
    value = 10 ** power * v
    return value


def load_quote_file(path, period):
    """parse ths history file: .day .min .mn5
    """
    if not os.path.exists(path):
        raise OSError('could not find file: %s' % path)
    datatype = get_system_config().datatype()
    fsize = os.path.getsize(path)
    f = open(path, 'rb')
    # tag
    tag, = struct.unpack('<6s', f.read(6))
    if tag != b'hd1.0\x00':
        raise Exception('%s header error' % path)
    row, offset, bsize, column = struct.unpack('<LHHH', f.read(10))
    if fsize != (offset + row * bsize):
        raise ValueError('Struct:', fsize, offset + row * bsize)
    # header
    header = []
    fmt = '<'
    for x in range(column):
        B = struct.unpack('<H2B', f.read(4))
        # 0: datatype 1: reserve, 0 2: size
        typ = B[0] >> 12
        dt = B[0] & 0xfff
        header.append({
            'type': typ,
            'name': datatype[dt],
            'desc': datatype.getDesc(dt),
            'format': datatype_type[typ][B[2]],
            'length': B[2],
        })
        fmt += datatype_type[typ][B[2]]

    # data
    data = []
    for y in range(row):
        d = []
        B = struct.unpack(fmt, f.read(bsize))
        for x in range(column):
            if header[x]['name'] == 'DATETIME':
                if period == 'day':
                    value = decode_ths_date(B[x])
                else:
                    value = decode_ths_time(B[x])
            elif header[x]['type'] == 7:
                value = decode_ths_float(B[x])
            else:
                raise ValueError(header[x])
            d.append((header[x]['name'], value))
        data.append(dict(d))
    f.close()
    data.sort(key=lambda x: x['DATETIME'], reverse=True)
    return {'header': header, 'data': data}


def load_quote_data(ths_dir, mcode, period):
    """period: day, min, min5
    """
    mcode = mcode.upper()
    if mcode.startswith('SH'):
        market_path = 'shase'
    elif mcode.startswith('SZ'):
        market_path = 'sznse'
    else:
        market_path = ''

    if period == 'min5':
        filename = '%s.mn5' % (mcode[2:])
    else:
        filename = '%s.%s' % (mcode[2:], period)

    hpath = os.path.join(ths_dir, 'history', market_path, period, filename)
    return load_quote_file(hpath, period)


def load_finance_file(path, mcode):
    datatype = get_system_config().datatype()
    fsize = os.path.getsize(path)
    f = open(path, 'rb')
    # tag
    tag, = struct.unpack('<6s', f.read(6))
    if tag != b'hd1.0\x00':
        raise Exception('%s header error' % path)

    row, offset, bsize, column = struct.unpack('<LHHH', f.read(10))
    # unknown = row >> 24  # 0b11
    row &= 0xffffff
    offset |= (column >> 14) << 16
    column &= 0x3fff
    if fsize != (offset + row * bsize):
        raise ValueError('Struct:', fsize, offset + row * bsize)
    # header
    h_fmt = '<'
    header = []
    for x in range(column):
        B = struct.unpack('<H2B', f.read(4))
        # 0: datatype 1: reserve  2: size
        typ = B[0] >> 12
        dt = B[0] & 0xfff
        fmt = datatype_type[typ].get(B[2], '%s%s' % (B[2], datatype_type[typ].get(0)))
        field = {
            'type': typ,
            'name': datatype[dt],
            'desc': datatype.getDesc(dt),
            'format': fmt,
            'length': B[2],
        }
        h_fmt += field['format']
        header.append(field)

    # padding, always 0x00
    f.read(column * 2)

    # index
    idx_size, idx_total = struct.unpack('<2H', f.read(4))
    idx_size |= (idx_total >> 14) << 16
    idx_total &= 0x3fff
    if (idx_size - 4) != idx_total * 18:
        raise ValueError('Index: idx size(%s) - 4 != idx_total(%s) * 18' % (idx_size, idx_total))
    data_index = {}
    for x in range(idx_total):
        code_typ, code, idle_count, row_offset, total = struct.unpack('<B9sHLH', f.read(18))
        code = code.decode().strip('\x00')
        data_index[code] = (code_typ, code, idle_count, row_offset, total)

    # data
    cur_idx = data_index.get(mcode[2:])
    data = []
    if cur_idx:
        f.seek(offset + cur_idx[3] * bsize)
        for y in range(cur_idx[4] - cur_idx[2]):
            B = struct.unpack(h_fmt, f.read(bsize))
            d = []
            for x in range(column):
                if header[x]['name'] in ['DATETIME', '301', 'CQR', 'DJR', 'PSSR']:
                    value = decode_ths_date(B[x])
                elif header[x]['type'] == 7:
                    value = decode_ths_float(B[x])
                elif header[x]['type'] == 2:
                    value = B[x].decode('gbk').strip('\00')
                else:
                    value = B[x]
                d.append((header[x]['name'], value))
            data.append(dict(d))
    f.close()
    data.sort(key=lambda x: x['DATETIME'], reverse=True)
    return {'header': header, 'data': data}


def load_finance_data(ths_dir, mcode, finance):
    choice = dict([
        ('1', '财务附注.财经'),
        ('2', '股本结构.财经'),
        ('3', '股东户数.财经'),
        ('4', '净资产收益率.财经'),
        ('5', '利润分配.财经'),
        ('6', '每股净资产.财经'),
        ('7', '每股盈利.财经'),
        ('8', '权息资料.财经'),
        ('9', '现金流量.财经'),
        ('10', '资产负债.财经'),
        ('11', '自由流通股本.财经'),
    ])

    path = os.path.join(ths_dir, 'finance', choice[finance])
    if not os.path.exists(path):
        raise OSError('could not find file: %s' % path)
    return load_finance_file(path, mcode)


def add_arguments(parser):
    parser.add_argument('--directory', dest='ths_dir', default=ths_dir, help='THS Software directory')

    parser.add_argument('--period', choices=['day', 'min', 'min5'], help='history period')
    parser.add_argument('--finance', choices=[str(x + 1) for x in range(11)], help='finance')
    parser.add_argument('mcode', nargs='+', help='Stock code, SH600000')


def exec_args(args):
    for mcode in args.mcode:
        if args.period:
            data = load_quote_data(args.ths_dir, mcode, args.period)
        elif args.finance:
            data = load_finance_data(args.ths_dir, mcode, args.finance)
        if data['data']:
            print('=' * 40)
            fmt = '\n'.join(['%(desc)s(%(name)s): %%(%(name)s)s' % h for h in data['header']])
            for x in range(len(data['data'])):
                print(fmt % data['data'][x])
                print((' %s ' % (x + 1)).center(40, '-'))
