import sqlite3
import os.path

from flask import Blueprint, g

from .utils import singleton


__version__ = '1.0.2'


mdict = Blueprint(
    'mdict', __name__,
    static_folder='static', template_folder='templates')


@singleton
class Config():
    pass


def init_app(app):
    @app.teardown_appcontext
    def close_connection(exception):
        database = getattr(g, '_database', None)
        if not database:
            return
        for conn in database.values():
            conn.close()

    Config.MDICT_DIR = app.config.get('MDICT_DIR')
    Config.MDICT_CACHE = app.config.get('MDICT_CACHE')
    if not Config.MDICT_DIR:
        raise ValueError('Please set "MDICT_DIR" in app.config')

    Config.MDICT, Config.DB_NAMES = helper.init_mdict(Config.MDICT_DIR)
    ecdict_fname = os.path.join(Config.MDICT_DIR, 'ecdict.db')
    if os.path.exists(ecdict_fname):
        Config.DB_NAMES['ecdict'] = ecdict_fname
    else:
        print('Do not find ECDICT "%s"' % ecdict_fname)

    app.register_blueprint(mdict, url_prefix='/mdict')


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
            db = sqlite3.connect(db_name)
            db.row_factory = sqlite3.Row
            database[uuid] = db
    return db


# must import at bottom
from . import helper, views
