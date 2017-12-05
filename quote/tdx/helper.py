
from .config import tdx_dir
from tdxhq import TdxHq, TdxConfig

# initialize
_cfg = None
_tdxhq = None


def get_config():
    global _cfg
    if _cfg:
        return _cfg
    _cfg = TdxConfig(tdx_dir)
    return _cfg


def get_tdxhq(host=None):
    global _tdxhq
    server = host or get_config().getPrimaryHQHost()
    hq_server = (server['ipaddress'], server['port'])
    if _tdxhq and _tdxhq.is_connected() and _tdxhq.get_hq_server() == hq_server:
        return _tdxhq
    _tdxhq = _tdxhq or TdxHq()
    _tdxhq.disconnect()
    _tdxhq.connect(hq_server[0], hq_server[1])
    return _tdxhq
