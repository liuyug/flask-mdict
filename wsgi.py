#!/usr/bin/env python3
# -*- encoding:utf-8 -*-


from flask import Flask, redirect, url_for

from . import init_app


def create_app():
    app = Flask(__name__)
    app.config['MDICT_DIR'] = 'content'
    app.config['MDICT_CACHE'] = False
    app.config['SECRET_KEY'] = "21ffjfdlsafj2ofjaslfjdsaf"
    init_app(app)
    return app


app = create_app()


@app.route('/')
def default():
    return redirect(url_for('mdict.query_word2'))
