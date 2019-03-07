
from flask import Blueprint, current_app, render_template

from . import helper

mdict = Blueprint('mdict', __name__, template_folder='templates')

_MDICT = None


def init_mdict(mdict_dir):
    global _MDICT
    _MDICT = helper.init_mdict(mdict_dir)


def get_mdict():
    global _MDICT
    if not _MDICT:
        _MDICT = helper.init_mdict(current_app.config['MDICT_DIR'])
    return _MDICT


@mdict.route('/list')
def list_mdict():
    dicts = []
    for name, instance in get_mdict().items():
        dicts.append({
            'title': instance._title,
            'description': instance._description,
            'version': instance._version,
            'style': instance._stylesheet,
        })
    return render_template('mdict/list.html', dicts=dicts)


@mdict.route('/search/')
def search_word():
    contents = None
    return render_template('mdict/search.html', contents=contents)
