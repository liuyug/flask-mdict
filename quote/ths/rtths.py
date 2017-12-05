
import datetime
import json

from .thshq import ThsHq


def get_realtime_data(mcodes, ip=None, port=80):
    hqhost_path = 'hqhost.json'
    datatype_path = 'datatype.json'

    hqhost = json.load(open(hqhost_path))
    ip = ip or hqhost['default']['ipaddress']

    thshq = ThsHq(ip, dt=datatype_path)

    datatype = 'zqmc,open,pre,new,high,low,buyprice,sellprice,vol,money,buycount1,buyprice1,buycount2,buyprice2,buycount3,buyprice3,buycount4,buyprice4,buycount5,buyprice5,sellcount1,sellprice1,sellcount2,sellprice2,sellcount3,sellprice3,sellcount4,sellprice4,sellcount5,sellprice5,fromopen'
    hq_data = thshq.getHQ(mcodes, datatype.upper().split(','))

    data = {}
    now = datetime.datetime.now()
    for hq in hq_data[0]:
        hq['MCODE'] = hq['CODE']
        hq['NAME'] = hq['ZQMC']
        hq['DATE'] = now.date()
        fromopen = float(hq['FROMOPEN']) - 1
        if fromopen > 121:
            fromopen += 90
        fromopen += 30
        hour = fromopen / 60 + 9
        minute = fromopen % 60
        hq['TIME'] = '%02d:%02d:00' % (hour, minute)
        data[hq['MCODE']] = hq
    return data
