#!/usr/bin/env python3
# -*- encoding:utf-8 -*-

import os.path
import sys
import argparse
import uuid
import sqlite3
import csv
import webbrowser
import zipfile

import requests
from flask import Flask, redirect, url_for

from flask_mdict import __version__, init_app, mdict_query2


def create_app(mdict_dir='content'):
    app = Flask(__name__, template_folder=None, static_folder=None)
    app.config['MDICT_DIR'] = mdict_dir
    app.config['MDICT_CACHE'] = False
    app.config['SECRET_KEY'] = "21ffjfdlsafj2ofjaslfjdsaf"

    init_app(app, url_prefix='/')

    @app.route('/favicon.ico')
    def favicon():
        return redirect(url_for('mdict.static', filename='logo.ico'))

    return app


def start_flask_mdict_server(mdict_dir, host, port, debug=False):
    app = create_app(mdict_dir)
    url = 'http://%s:%s' % (host, port)
    webbrowser.open_new_tab(url)
    app.run(host=host, port=port, debug=debug)


def mdict_index(mdict_dir, action=None):
    for root, dirs, files in os.walk(mdict_dir, followlinks=True):
        for fname in files:
            if action == 'check' and (fname.endswith('.mdx') or fname.endswith('.mdd')):
                fname_path = os.path.join(root, fname)
                is_update = mdict_query2.IndexBuilder2.is_update(fname_path)
                if is_update:
                    print(f'{fname} need be update...')
            elif action == 'remove' and (fname.endswith('.mdx') or fname.endswith('.mdd')):
                db_fname = os.path.join(root, fname + '.db')
                if os.path.exists(db_fname):
                    os.remove(db_fname)
                    print('Remove "%s".' % db_fname)
            elif action == 'create' and fname.endswith('.mdx'):
                # scan mdd automaticly by mdx
                name = os.path.splitext(fname)[0]
                mdx_file = os.path.join(root, fname)
                dict_uuid = str(uuid.uuid3(uuid.NAMESPACE_URL, mdx_file)).upper()
                print('Initialize MDICT "%s" {%s}...' % (name, dict_uuid))
                idx = mdict_query2.IndexBuilder2(mdx_file)
                if idx._description == '<font size=5 color=red>Paste the description of this product in HTML source code format here</font>':
                    text = ''
                else:
                    text = idx._description
                about_html = os.path.join(root, 'about_%s.html' % name)
                if not os.path.exists(about_html):
                    with open(about_html, 'wt') as f:
                        f.write(text)


def install_wfd(mdict_dir):
    csv_file = os.path.join(mdict_dir, 'ecdict.csv')
    db_file = os.path.join(mdict_dir, 'ecdict_wfd.db')
    if not os.path.exists(csv_file):
        url = 'https://github.com/skywind3000/ECDICT/raw/master/ecdict.csv'
        print('get ecdict.csv.', end='', flush=True)
        r = requests.get(url, stream=True)
        with open(csv_file, 'wb') as f:
            for chunk in r.iter_content(chunk_size=10240):
                print('.', end='', flush=True)
                f.write(chunk)
        print()
    print('convert ecdict.csv to ecdict_wfd.db...')
    with open(csv_file, newline='', encoding='utf-8') as f:
        reader = csv.reader(f)
        with sqlite3.connect(db_file) as conn:
            conn.execute('DROP TABLE IF EXISTS ecdict')
            conn.execute('DROP INDEX IF EXISTS ecdict_index_word')
            c = conn.cursor()
            header = ['"%s" TEXT' % h for h in next(reader)]
            sql = 'CREATE TABLE ecdict(%s);' % ','.join(header + ['PRIMARY KEY(word)'])
            c.execute(sql)
            conn.commit()
            sql = 'INSERT INTO ecdict VALUES (%s)' % ','.join(['?'] * len(header))
            for row in reader:
                c.execute(sql, row)
            conn.commit()
            # primary key or index
            # conn.execute('CREATE INDEX ecdict_index_word ON ecdict(word)')


def install_ecdict(mdict_dir):
    url = 'https://github.com/skywind3000/ECDICT/releases/download/1.0.28/ecdict-mdx-style-28.zip'
    fname = os.path.basename(url)
    zip_file = os.path.join(mdict_dir, fname)
    if not os.path.exists(zip_file):
        print(f'get {fname}.', end='', flush=True)
        r = requests.get(url, stream=True)
        with open(zip_file, 'wb') as f:
            for chunk in r.iter_content(chunk_size=10240):
                print('.', end='', flush=True)
                f.write(chunk)
        print()
    dict_dir = os.path.join(mdict_dir, os.path.splitext(fname)[0])
    print(f'extract "{fname}" into "{dict_dir}"...')
    os.makedirs(dict_dir, exist_ok=True)
    with zipfile.ZipFile(zip_file) as z:
        z.extractall(dict_dir)


def main():
    parser = argparse.ArgumentParser(description='Flask Mdict Tool')
    parser.add_argument('--version', action='version',
                        version='Flask Mdict Tool v%s' % __version__,
                        help='show version')
    group = parser.add_argument_group('Flask Mdict Server')
    group.add_argument('--server', action='store_true', help='start Flask Mdict Server')
    group.add_argument('--host', default='127.0.0.1', help='the interface to bind to')
    group.add_argument('--port', default=5248, help='the interface to bind to')
    group.add_argument('--debug', action='store_true', help='debug mode')

    group = parser.add_argument_group('ECDICT - Free English to Chinese Dictionary')
    group.add_argument('--install-wfd', action='store_true',
                       help='install Word Frequency Database from ECDICT csv')
    group.add_argument('--install-ecdict', action='store_true',
                       help='install ECDICT dictionary.')

    group = parser.add_argument_group('Mdict Index for Flask Mdict')
    group.add_argument('--create-index', action='store_true',
                       help='create MDICT index database')
    group.add_argument('--remove-index', action='store_true',
                       help='remove MDICT index database')
    group.add_argument('--check-index', action='store_true',
                       help='check if the index is out of date')

    parser.add_argument('mdict_dir', nargs='?', default='content',
                        help='dictionary directory. default: "content"')

    args = parser.parse_args()

    if args.install_wfd:
        install_wfd(args.mdict_dir)
    elif args.install_ecdict:
        install_ecdict(args.mdict_dir)
    elif args.remove_index:
        mdict_index(args.mdict_dir, 'remove')
    elif args.create_index:
        mdict_index(args.mdict_dir, 'create')
    elif args.check_index:
        mdict_index(args.mdict_dir, 'check')
    else:
        start_flask_mdict_server(args.mdict_dir, args.host, args.port, args.debug)


if __name__ == "__main__":
    main()
