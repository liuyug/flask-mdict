

from . import config
from .thshq import SystemConfig, UserConfig, ThsHq, Datatype

# initialize
_system_cfg = None
_user_cfg = None
_thshq = None
_stock_market = None
_stock_code = None


def get_system_config():
    global _system_cfg
    if _system_cfg:
        return _system_cfg
    _system_cfg = SystemConfig(config.ths_dir)
    return _system_cfg


def get_user_config():
    global _user_cfg
    if _user_cfg:
        return _user_cfg
    _user_cfg = UserConfig(config.ths_dir)
    return _user_cfg


def get_thshq(config=None):
    global _thshq
    if config:
        server = config.get('current_host')
        datatype = Datatype(data=config.get('datatype'))
    else:
        server = get_user_config().getPrimaryHQHost()
        datatype = get_system_config().datatype()

    hq_server = (server['ipaddress'], 80)
    if _thshq and _thshq.get_hq_server() == hq_server:
        return _thshq

    _thshq = _thshq or ThsHq(datatype)
    _thshq.disconnect()
    _thshq.connect(hq_server[0], hq_server[1])
    return _thshq


def get_stock_market():
    global _stock_market
    if _stock_market:
        return _stock_market
    _stock_market = get_thshq().getMarket()
    return _stock_market


def get_stock_code():
    global _stock_code
    if _stock_code:
        return _stock_code
    _stock_code = get_thshq().getStock()
    return _stock_code
