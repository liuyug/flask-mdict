#!/usr/bin/env python3
# -*- encoding:utf-8 -*-

import os.path
import sys

from flask import Flask, redirect, url_for


def create_app():
    app = Flask(__name__)
    app.config['MDICT_DIR'] = 'content'
    app.config['MDICT_CACHE'] = False
    app.config['SECRET_KEY'] = "21ffjfdlsafj2ofjaslfjdsaf"

    from . import init_app
    init_app(app)

    @app.route('/')
    def default():
        return redirect(url_for('mdict.query_word2'))

    return app


if __name__ == "__main__":
    # fix import path
    parent = os.path.dirname(os.path.realpath(__file__))
    pparent = os.path.dirname(parent)
    sys.path.append(pparent)
    __package__ = os.path.basename(parent)

    app = create_app()
    app.run()
