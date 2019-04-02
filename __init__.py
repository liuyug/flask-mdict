
from flask import Blueprint

from .utils import singleton


mdict = Blueprint(
    'mdict', __name__,
    static_folder='static', template_folder='templates')


@singleton
class Config():
    pass


def init_app(app):
    Config.MDICT_DIR = app.config.get('MDICT_DIR')
    Config.MDICT_CACHE = app.config.get('MDICT_CACHE')
    if not Config.MDICT_DIR:
        raise ValueError('Please set "MDICT_DIR" in app.config')

    Config.MDICT = helper.init_mdict(Config.MDICT_DIR)
    # sqlite3 db do not support thread
    Config.ECDICT_DBNAME = helper.init_ecdict(Config.MDICT_DIR)

    app.register_blueprint(mdict, url_prefix='/mdict')


def get_mdict():
    return Config.MDICT


# must import at bottom
from . import helper, views
