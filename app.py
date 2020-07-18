#!/usr/bin/env python3
# -*- encoding:utf-8 -*-

import os.path
import sys

from flask import Flask, redirect, url_for


def create_app():
    app = Flask(__name__, template_folder=None, static_folder=None)
    app.config['MDICT_DIR'] = 'content'
    app.config['MDICT_CACHE'] = False
    app.config['SECRET_KEY'] = "21ffjfdlsafj2ofjaslfjdsaf"

    from flask_mdict import init_app
    init_app(app, url_prefix='/')

    @app.route('/favicon.ico')
    def favicon():
        return redirect(url_for('mdict.static', filename='logo.ico'))

    return app


if __name__ == "__main__":
    app = create_app()
    app.run()
