
import os.path
import struct
from datetime import datetime


from .config import ths_dir, get_system_config


def load_history_data(hpath):
    """parse ths history data
    """
    if not os.path.exists(hpath):
        raise OSError('could not find file: %s' % hpath)
    datatype = get_system_config().datatype()
    f = open(hpath, 'rb')
    tag, = struct.unpack('<6s', f.read(6))
    if tag != b'hd1.0\x00':
        raise Exception('%s header error' % hpath)
    row, offset, size, column = struct.unpack('<LHHH', f.read(10))
    data = []
    header = []
    for x in range(column):
        B = struct.unpack('<4B', f.read(4))
        # 0: datatype 1: 30 or 70? 2: 0 3: byte
        header.append(datatype[str(B[0])])
        if B[3] != 4:
            raise TypeError(''.join(['%2X' % b for b in B]))
    for y in range(row):
        d = []
        B = struct.unpack('<%dL' % column, f.read(size))
        for x in range(column):
            if header[x] == 'DATETIME':
                value = datetime.strptime('%s' % B[0], '%Y%m%d').date()
            elif B[x] == 0xFFFFFFFF:
                value = float('nan')
            else:
                v = B[x] & 0x0fffffff
                sign = -1 if (B[x] >> 31) == 1 else 1
                power = (B[x] >> 28 & 0b0111) * sign
                value = 10 ** power * v
            d.append((header[x], value))
        data.append(dict(d))
    f.close()
    data.sort(key=lambda x: x['DATETIME'], reverse=True)
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
        if args.period == 'min5':
            filename = '%s.mn5' % (mcode[2:])
        else:
            filename = '%s.%s' % (mcode[2:], args.period)
        hpath = os.path.join(
            args.ths_dir, 'history', market_path, args.period, filename)
        data = load_history_data(hpath)
        if data['data']:
            fmt = '\n'.join(['%s: %%(%s)s' % (h, h) for h in data['header'][:]])
            for d in data['data']:
                print(fmt % d)
