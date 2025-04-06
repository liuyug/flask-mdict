import sqlite3
import os.path

from flask import Blueprint, g

from .utils import singleton


__version__ = '1.4.20'


mdict = Blueprint(
    'mdict', __name__,
    static_folder='static', template_folder='templates')


@singleton
class Config():
    pass


def init_app(app, url_prefix=None):
    Config.MDICT_DIR = app.config.get('MDICT_DIR')
    Config.MDICT_CACHE = app.config.get('MDICT_CACHE')
    if not Config.MDICT_DIR:
        raise ValueError('Please set "MDICT_DIR" in app.config')

    Config.INDEX_DIR = app.config.get('INDEX_DIR')

    Config.DB_NAMES = {}

    # for flask mdict: setting, history...
    Config.DB_NAMES['app_db'] = app.config.get('APP_DB')
    Config.DB_NAMES['wfd_db'] = app.config.get('WFD_DB')
    helper.init_flask_mdict()

    mdicts, db_names = helper.init_mdict(Config.MDICT_DIR, Config.INDEX_DIR)
    Config.MDICT = mdicts
    Config.DB_NAMES.update(db_names)

    app.register_blueprint(mdict, url_prefix=url_prefix)


def get_mdict():
    return Config.MDICT


def get_db(uuid):
    database = getattr(g, '_database', None)
    if not database:
        database = g._database = {}
    db = database.get(uuid)
    if db is None:
        db_name = Config.DB_NAMES.get(uuid)
        if db_name:
            if not os.path.exists(db_name):
                return
            db = sqlite3.connect(db_name)
            db.row_factory = sqlite3.Row
            database[uuid] = db
    return db


# must import at bottom
from . import helper, views
