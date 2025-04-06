#!/usr/bin/env python3
# -*- encoding:utf-8 -*-
import os
import argparse
import logging

from flask import Flask, redirect, url_for, g

from flask_mdict import __version__, init_app


logger = logging.getLogger(__name__)


def create_app(mdict_dir='content'):
    logging.basicConfig(
        level=20,
        format='%(message)s',
    )
    mdict_dir = os.path.realpath(mdict_dir)

    app = Flask(__name__, template_folder=None, static_folder=None)
    # csrf 永久有效
    app.config['WTF_CSRF_TIME_LIMIT'] = None
    app.config['MDICT_DIR'] = mdict_dir
    app.config['MDICT_CACHE'] = False
    app.config['SECRET_KEY'] = "21ffjfdlsafj2ofjaslfjdsaf"
    app.config['APP_DB'] = os.path.join(mdict_dir, 'flask_mdict.db')
    app.config['INDEX_DIR'] = None
    app.config['APP_NAME'] = 'Flask Mdict'

    wfd_db = None
    local_wfd_db = os.path.join(mdict_dir, 'ecdict_wfd.db')
    app_wfd_db = os.path.join(os.path.dirname(__file__), os.path.basename(local_wfd_db))
    if os.path.exists(local_wfd_db):
        wfd_db = local_wfd_db
        app.config['WFD_DB'] = wfd_db
    elif os.path.exists(app_wfd_db):
        wfd_db = app_wfd_db
        app.config['WFD_DB'] = wfd_db

    init_app(app, url_prefix='/')

    logger.info(' * app version: %s' % __version__)
    logger.info(' * app db: %s' % app.config['APP_DB'])
    if wfd_db:
        logger.info(f' * Word Frequency Database: {wfd_db}"')
    else:
        logger.error(f' * Could not found "Word Frequency Database - {local_wfd_db}"!')

    @app.route('/favicon.ico')
    def favicon():
        return redirect(url_for('mdict.static', filename='logo.ico'))

    @app.teardown_appcontext
    def close_connection(exception):
        database = getattr(g, '_database', None)
        if not database:
            return
        for conn in database.values():
            conn.close()

    return app


def cli():
    parser = argparse.ArgumentParser(description='Flask-mdict')
    about = 'Flask-mdict version: %s' % __version__
    parser.add_argument('--version', action='version', version=about, help='show version')

    parser.add_argument('--host', default='127.0.0.1:5678', help='service listen ip:port')
    parser.add_argument('-m', '--mdict-dir', default='content', help='mdict dictionary path')

    args = parser.parse_args()

    app = create_app(args.mdict_dir)

    ip, port = args.host.split(':')

    debug = False
    threaded = True
    process = 1

    app.run(
        host=ip, port=port, debug=debug,
        threaded=threaded, processes=process
    )


if __name__ == "__main__":
    cli()
