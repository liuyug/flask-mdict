
from flask import Blueprint


mdict = Blueprint(
    'mdict', __name__,
    static_folder='static', template_folder='templates')

_MDICT = None


def init_app(app):
    global _MDICT
    _MDICT = helper.init_mdict(app.config['MDICT_DIR'])

    app.register_blueprint(mdict, url_prefix='/mdict')


def get_mdict():
    global _MDICT
    return _MDICT


# must import at bottom
from . import helper, views
