#!/usr/bin/env python3
# -*- encoding:utf-8 -*-

import os.path
import sys

from flask import Flask, redirect, url_for


def create_app():
    if getattr(sys, 'frozen', False):
        template_folder = os.path.join(sys._MEIPASS, 'templates')
        static_folder = os.path.join(sys._MEIPASS, 'static')
        app = Flask(__name__, template_folder=template_folder, static_folder=static_folder)
    else:
        app = Flask(__name__)
    print(__file__)
    app.config['MDICT_DIR'] = 'content'
    app.config['MDICT_CACHE'] = False
    app.config['SECRET_KEY'] = "21ffjfdlsafj2ofjaslfjdsaf"

    from . import init_app
    init_app(app)

    return app


if __name__ == "__main__":
    # fix import path
    parent = os.path.dirname(os.path.realpath(__file__))
    pparent = os.path.dirname(parent)
    sys.path.append(pparent)
    __package__ = os.path.basename(parent)

    app = create_app()
    app.run()
