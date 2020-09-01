#!/usr/bin/env python3
# -*- encoding:utf-8 -*-
import os
import logging

from flask import Flask, redirect, url_for

from flask_mdict import __version__, init_app, mdict_query2


logger = logging.getLogger(__name__)


def create_app(mdict_dir='content'):
    logging.basicConfig(
        level=20,
        format='%(message)s',
    )
    mdict_dir = os.path.realpath(mdict_dir)

    app = Flask(__name__, template_folder=None, static_folder=None)
    app.config['MDICT_DIR'] = mdict_dir
    app.config['MDICT_CACHE'] = False
    app.config['SECRET_KEY'] = "21ffjfdlsafj2ofjaslfjdsaf"
    app.config['APP_DB'] = os.path.join(mdict_dir, 'flask_mdict.db')

    init_app(app, url_prefix='/')
    logger.info(' * app db: %s' % app.config['APP_DB'])

    @app.route('/favicon.ico')
    def favicon():
        return redirect(url_for('mdict.static', filename='logo.ico'))

    return app
