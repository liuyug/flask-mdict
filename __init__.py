
from flask import Blueprint


mdict = Blueprint(
    'mdict', __name__,
    static_folder='static', template_folder='templates')

_MDICT = None
_ECDICT_NAME = None


def init_app(app):
    global _MDICT, _ECDICT_NAME
    _MDICT = helper.init_mdict(app.config['MDICT_DIR'])
    _ECDICT_NAME = helper.init_ecdict(app.config['MDICT_DIR'])

    app.register_blueprint(mdict, url_prefix='/mdict')


def get_mdict():
    global _MDICT
    return _MDICT


def get_ecdict_name():
    global _ECDICT_NAME
    return _ECDICT_NAME


# must import at bottom
from . import helper, views
