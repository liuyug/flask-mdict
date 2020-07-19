#!/usr/bin/env python3
# -*- encoding:utf-8 -*-

import os.path
import sys
import argparse
import uuid

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


def init_mdict(mdict_dir, action=None):
    for root, dirs, files in os.walk(mdict_dir, followlinks=True):
        for fname in files:
            if action == 'clean' and (fname.endswith('.mdx') or fname.endswith('.mdd')):
                db_fname = os.path.join(root, fname + '.db')
                if os.path.exists(db_fname):
                    os.remove(db_fname)
                    print('Remove "%s".' % db_fname)
            elif action == 'init' and fname.endswith('.mdx'):
                db_fname = os.path.join(root, fname + '.db')
                if action == 'clean':
                    if os.path.exists(db_fname):
                        os.remove(db_fname)
                        print('Remove "%s".' % db_fname)
                elif action == 'init':
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


def main():
    parser = argparse.ArgumentParser(description='Flask Mdict Initialize Tool')
    parser.add_argument('--version', action='version',
                        version='Flask Mdict Server v%s' % __version__,
                        help='about')
    parser.add_argument('--server', action='store_true', help='run Flask Mdict Server')
    parser.add_argument('--clean', action='store_true', help='clean db file')
    parser.add_argument('--init', action='store_true', help='initialize mdict db file')
    parser.add_argument('mdict_dir', nargs='?', default='content', help='mdict directory. default: content')

    args = parser.parse_args()

    if args.clean:
        init_mdict(args.mdict_dir, 'clean')
    elif args.init:
        init_mdict(args.mdict_dir, 'init')
    else:
        app = create_app(args.mdict_dir)
        app.run()


if __name__ == "__main__":
    main()
