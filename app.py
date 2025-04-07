#!/usr/bin/env python3
# -*- encoding:utf-8 -*-
import os
import sys
import json
import argparse
import logging

from flask import Flask, redirect, url_for, g

from flask_mdict import __version__, init_app


logger = logging.getLogger(__name__)


def create_app(config=None):
    logging.basicConfig(
        level=20,
        format='%(message)s',
    )
    app = Flask(__name__, template_folder=None, static_folder=None)
    # csrf 永久有效
    app.config['WTF_CSRF_TIME_LIMIT'] = None
    app.config['MDICT_DIR'] = os.path.realpath('content')
    app.config['MDICT_CACHE'] = False
    app.config['SECRET_KEY'] = "21ffjfdlsafj2ofjaslfjdsaf"
    app.config['INDEX_DIR'] = None
    app.config['APP_NAME'] = 'Flask Mdict'

    if config:
        app.config.update(config)

    mdict_dir = app.config['MDICT_DIR']
    if not os.path.exists(mdict_dir):
        os.makedirs(mdict_dir)

    app.config['APP_DB'] = os.path.join(mdict_dir, 'flask_mdict.db')

    wfd_db = None
    local_wfd_db = os.path.join(mdict_dir, 'flask_mdict_wfd.db')
    app_wfd_db = os.path.join(os.path.dirname(__file__), os.path.basename(local_wfd_db))
    if os.path.exists(local_wfd_db):
        wfd_db = local_wfd_db
        app.config['WFD_DB'] = wfd_db
    elif os.path.exists(app_wfd_db):
        wfd_db = app_wfd_db
        app.config['WFD_DB'] = wfd_db

    logger.info(' * app version: %s' % __version__)
    logger.info(' * app db: %s' % app.config['APP_DB'])
    if wfd_db:
        logger.info(f' * Word Frequency Database: {wfd_db}"')
    else:
        logger.error(f' * Could not found "Word Frequency Database - {local_wfd_db}"!')

    init_app(app, url_prefix='/mdict')

    @app.route('/')
    def index():
        return redirect(url_for('mdict.query_word_all'))

    @app.route('/favicon.ico')
    def favicon():
        return redirect(url_for('mdict.static', filename='favicon.ico'))

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

    parser.add_argument('--config-file', default='flask_mdict.json', help='app config json file. default: flask_mdict.json')
    parser.add_argument('--debug', action='store_true', help='flask run as debug mode')
    parser.add_argument('--host', help='service listen ip:port')
    parser.add_argument('--mdict-dir', help='mdict dictionary path')

    args = parser.parse_args()

    config_data = {}
    if os.path.exists(args.config_file):
        config_data = json.load(open(args.config_file))

    if 'server' not in config_data:
        config_data['server'] = {}
        config_data['server']['ip'] = '127.0.0.1'
        config_data['server']['port'] = '5248'
        config_data['server']['debug'] = False
        config_data['server']['threaded'] = True
        config_data['server']['process'] = 1

    ip = config_data['server'].get('ip', '127.0.0.1')
    port = config_data['server'].get('port', '5248')
    debug = config_data['server'].get('debug', False)
    threaded = config_data['server'].get('threaded', True)
    process = config_data['server'].get('process', 1)

    if args.host:
        ip, port = args.host.split(':')
    if args.debug:
        debug = args.debug

    if 'mdict' not in config_data:
        config_data['mdict'] = {}
        config_data['mdict']['SECRET_KEY'] = '21fwkepawlsafj2jaslfjdsaf'

        if getattr(sys, 'frozen', False) and hasattr(sys, '_MEIPASS'):
            config_data['mdict']['MDICT_DIR'] = os.path.realpath('.')
        else:
            config_data['mdict']['MDICT_DIR'] = os.path.realpath('content')

    if not os.path.exists(args.config_file):
        json.dump(config_data, open('flask_mdict.json', 'wt'), indent=4)

    if args.mdict_dir:
        config_data['mdict']['MDICT_DIR'] = os.path.realpath(args.mdict_dir)

    app = create_app(config_data['mdict'])

    ssl_context = None
    # ssl_context = 'adhoc'
    app.run(
        host=ip, port=port, debug=debug,
        ssl_context=ssl_context,
        threaded=threaded, processes=process
    )


if __name__ == "__main__":
    cli()
