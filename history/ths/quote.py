
import os.path
import struct
from datetime import datetime


from .config import ths_dir


def load_history_data(hpath):
    """parse ths history data
    """
    if not os.path.exists(hpath):
        raise OSError('could not find file: %s' % hpath)
    f = open(hpath, 'rb')
    tag, = struct.unpack('<6s', f.read(6))
    if tag != b'hd1.0\x00':
        raise Exception('%s header error' % hpath)
    rnum, roffset, rsize, rcnum = struct.unpack('<LHHH', f.read(10))
    data = []
    # XXX: unknown
    for x in range(rcnum):
        B = struct.unpack('<2H', f.read(4))
    for x in range(rnum):
        # day
        B = struct.unpack('<%dL' % rcnum, f.read(rsize))
        day = dict([
            ('date', datetime.strptime('%s' % B[0], '%Y%m%d').date()),
            ('open', 1.0 * (B[1] & 0x0FFFFFFF) / 10 ** ((B[1] >> 28) - 8)),
            ('max', 1.0 * (B[2] & 0x0FFFFFFF) / 10 ** ((B[2] >> 28) - 8)),
            ('min', 1.0 * (B[3] & 0x0FFFFFFF) / 10 ** ((B[3] >> 28) - 8)),
            ('close', 1.0 * (B[4] & 0x0FFFFFFF) / 10 ** ((B[4] >> 28) - 8)),
            ('amount', 1.0 * (B[5] & 0x0FFFFFFF) / 10 ** ((B[5] >> 28) - 8 + 9)),
            ('volume', 1.0 * (B[6] & 0x0FFFFFFF) / 10 ** ((B[6] >> 28) - 8 + 9)),
        ])
        data.append(day)
    f.close()
    data.sort(key=lambda x: x['date'], reverse=True)
    return data


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
        print(data)
