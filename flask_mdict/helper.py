
import re
import sys
import uuid
import os.path
import sqlite3
import datetime
import csv
import logging
from importlib import import_module

from flask import url_for

from . import Config, get_db
from .dbdict_query import DBDict
from .mdict_query2 import IndexBuilder2


logger = logging.getLogger(__name__)

regex_style = re.compile(r'<style.+?</style>', re.DOTALL | re.IGNORECASE)
regex_ln = re.compile(r'<(p|br|tr)[^>]*?>', re.IGNORECASE)
regex_tag = re.compile(r'<[^>]+?>')


def ecdict_query_word(word, item=None):
    def convert(data):
        html = []
        data = data.replace('\\n', '\n')
        for d in data.split('\n'):
            f = d.partition(' ')
            html.append('<div class="dcb">')
            html.append('<span class="pos">%s</span>' % f[0])
            html.append('<span class="dcn">%s</span>' % f[2])
            html.append('</div>')
        return '\n'.join(html)

    db = get_db('wfd_db')
    if not db:
        return []
    sql = 'SELECT * FROM ecdict where WORD = ?'
    cursor = db.execute(sql, (word.lower(), ))
    EXCHANGE = {
        'p': '过去式',
        'd': '过去分词',
        'i': '现在分词',
        '3': '第三人称单数',
        'r': '形容词比较级',
        't': '形容词最高级',
        's': '名词复数形式',
        '0': '词根',
        '1': '词根变换',
    }
    html_group = []
    for row in cursor:
        exchanges = []
        for e in row['exchange'].split('/'):
            if e:
                t, w = e.split(':')
                exchanges.append('%s: %s' % (EXCHANGE.get(t, t), w))
        html = []
        html.append('<link href="ecdict_wfd.css" rel="stylesheet" type="text/css">')
        html.append('<div class="bdy" id="ecdict">')
        html.append('<div class="ctn" id="content">')
        html.append(f'<div class="hwd">{row["word"]}</div>')
        html.append('<hr class="hrz" />')
        if row['phonetic']:
            html.append(f'<div class="git"><span class="ipa">[{row["phonetic"]}]</span></div>')
        if row['exchange']:
            html.append(f'<span>{" ".join(exchanges)}</span>')
        if row['definition']:
            html.append('<div>%s</div>' % convert(row["definition"]))
        html.append('<div class="gdc">%s</div>' % convert(row["translation"]))

        html.append('<hr class="hr2" />')
        html.append('</div>')
        html.append('</div>')
        html_group.append('\n'.join(html))
    return html_group


def ecdict_random_word(tag):
    word = ['hello']
    db = get_db('wfd_db')
    if not db:
        return word[0]
    sql = 'SELECT word FROM ecdict WHERE word IN (SELECT word FROM ecdict WHERE ecdict.tag like ? ORDER BY RANDOM() LIMIT 1)'
    cursor = db.execute(sql, ('%%%s%%' % tag, ))
    row = cursor.fetchone()
    return row['word']


def query_word_meta(word):
    TAGs = {
        'zk': '中考',
        'gk': '高考',
        'ky': '考研',
        'cet4': 'CET-4',
        'cet6': 'CET-6',
        'gre': 'GRE',
        'toefl': 'TOEFL',
        'ielts': 'IELTS',
    }
    db = get_db('wfd_db')
    if not db:
        key = {'error': 'Could not found "Word Frequency Database - ecdict_wfd.db"!'}
    else:
        sql = 'SELECT * FROM ecdict where WORD = ?'
        cursor = db.execute(sql, (word, ))
        row = next(cursor, None)
        key = dict(row) if row else {}
    word_meta = []
    if key.get('oxford'):
        word_meta.append('<a href="https://www.oxfordlearnersdictionaries.com/us/wordlist/english/oxford3000/" target="_blank">'
                         '<img src="%s" style="height:16px" title="Oxford 3000"/>'
                         '</a>' % url_for('.static', filename='Ox3000_Rect1_mod_web.png')
                         )
    if key.get('collins'):
        # star = '⭐'
        star = '<i class="text-warning fas fa-star"></i>'
        n = int(key['collins'])
        word_meta.append('<span title="Collins %s star">%s</span>' % (n, star * n))
    if key.get('tag'):
        tags = ['<span class="badge badge-pill badge-primary">%s</span>' % TAGs.get(t, t) for t in key['tag'].split(' ')]
        word_meta.extend(tags)
    if key.get('bnc'):
        word_meta.append('<a href="http://www.natcorp.ox.ac.uk/" target="_blank">'
                         '<span class="badge badge-pill badge-info" title="BNC: %s">BNC: %s</span>'
                         '</a>' % (key['bnc'], key['bnc']))
    if key.get('frq'):
        word_meta.append('<a href="https://www.english-corpora.org/coca/" target="_blank">'
                         '<span class="badge badge-pill badge-info" title="COCA: %s">COCA: %s</span>'
                         '</a>' % (key['frq'], key['frq']))
    if key.get('error'):
        word_meta.append('<span class="badge badge-pill badge-danger"></span>')
    return ' '.join(word_meta)


def init_flask_mdict():
    db_name = Config.DB_NAMES.get('app_db')
    db = sqlite3.connect(db_name)
    c = db.cursor()
    # history
    sql = 'SELECT name FROM sqlite_master WHERE type="table" AND name="history";'
    row = c.execute(sql).fetchone()
    if not row:
        sql = 'CREATE TABLE history(word TEXT PRIMARY KEY, count INT, last_time DATETIME);'
        db.execute(sql)
        db.commit()
    # mdict setting
    sql = 'SELECT name FROM sqlite_master WHERE type="table" AND name="setting";'
    row = c.execute(sql).fetchone()
    if not row:
        sql = 'CREATE TABLE setting(name TEXT PRIMARY KEY, value TEXT);'
        db.execute(sql)
        db.commit()
    db.close()


def mdict_enable(uuid, value=None):
    db = get_db('app_db')
    if not db:
        logger.error('no app db')
        return
    c = db.cursor()
    if value is not None:
        sql = 'INSERT INTO setting (name, value) VALUES(?, ?) ON CONFLICT(name) DO UPDATE SET value = ?;'
        c.execute(sql, (uuid, value, value))
        db.commit()
    else:
        sql = 'SELECT value FROM setting WHERE name = ?;'
        row = c.execute(sql, (uuid,)).fetchone()
        if row:
            return row[0]
        else:
            sql = 'INSERT INTO setting (name, value) VALUES(?, ?);'
            c.execute(sql, (uuid, True))
            db.commit()
            return True


def add_history(word):
    db = get_db('app_db')
    if not db:
        logger.error('no app db')
        return
    now = datetime.datetime.now()
    c = db.cursor()
    sql = 'INSERT INTO history (word, count, last_time) VALUES(?, 1, ?) ON CONFLICT(word) DO UPDATE SET count = count + 1, last_time = ?;'
    c.execute(sql, (word, now, now))
    db.commit()


def get_history(max_num=500):
    db = get_db('app_db')
    if not db:
        logger.error('no app db')
        return
    c = db.cursor()
    sql = 'SELECT * FROM history ORDER BY last_time DESC LIMIT ?;'
    rows = c.execute(sql, (max_num, )).fetchall()
    return rows


def clear_history():
    db = get_db('app_db')
    if not db:
        logger.error('no app db')
        return
    c = db.cursor()
    sql = 'DELETE FROM history;'
    c.execute(sql)
    db.commit()


def export_history(sio):
    db = get_db('app_db')
    if not db:
        logger.error('no app db')
        return
    c = db.cursor()
    sql = 'SELECT * FROM history;'
    rows = c.execute(sql).fetchall()
    csv_writer = csv.writer(sio)
    for row in rows:
        csv_writer.writerow((row['word'], row['count'], row['last_time'].rpartition('.')[0]))
    return sio


def init_mdict(mdict_dir, index_dir=None):
    mdicts = {}
    db_names = {}
    mdict_setting = {}
    with sqlite3.connect(Config.DB_NAMES['app_db']) as conn:
        rows = conn.execute('SELECT name, value FROM setting;')
        for row in rows:
            mdict_setting[row[0]] = row[1] == '1'
    for root, dirs, files in os.walk(mdict_dir, followlinks=True):
        for fname in files:
            if fname.endswith('.db') \
                    and not fname.endswith('.mdx.db') \
                    and not fname.endswith('.mdd.db'):
                db_file = os.path.join(root, fname)
                d = DBDict(db_file)
                if not d.is_ok():
                    continue
                # mdict db
                dict_uuid = str(uuid.uuid3(uuid.NAMESPACE_URL, db_file.replace('\\', '/'))).upper()
                name = os.path.splitext(fname)[0]
                enable = mdict_setting.get(dict_uuid, True)
                logger.info('Initialize DICT DB "%s" {%s} [%s]...' % (name, dict_uuid, 'Enable' if enable else 'Disable'))
                logger.info('\tfind %s:mdx' % fname)
                if d.is_mdd():
                    logger.info('\tfind %s:mdd' % fname)
                logo = 'logo.ico'
                for ext in ['ico', '.jpg', '.png']:
                    if os.path.exists(os.path.join(root, name + ext)):
                        logo = name + ext
                        break
                db_names[dict_uuid] = db_file
                mdicts[dict_uuid] = {
                    'title': d.title(),
                    'uuid': dict_uuid,
                    'logo': logo,
                    'about': d.about(),
                    'root_path': root,
                    'query': d,
                    'cache': {},
                    'type': 'mdict_db',
                    'error': '',
                    'enable': enable,
                }
            elif fname.endswith('.mdx'):
                name = os.path.splitext(fname)[0]
                logo = 'logo.ico'
                for ext in ['ico', '.jpg', '.png']:
                    if os.path.exists(os.path.join(root, name + ext)):
                        logo = name + ext
                        break
                mdx_file = os.path.join(root, fname)
                dict_uuid = str(uuid.uuid3(uuid.NAMESPACE_URL, mdx_file.replace('\\', '/'))).upper()
                enable = mdict_setting.get(dict_uuid, True)
                logger.info('Initialize MDICT "%s" {%s} [%s]...' % (name, dict_uuid, 'Enable' if enable else 'Disable'))

                if index_dir:
                    mdict_index_dir = os.path.join(index_dir, dict_uuid)
                    if not os.path.exists(mdict_index_dir):
                        os.makedirs(mdict_index_dir)
                else:
                    mdict_index_dir = None
                idx = IndexBuilder2(mdx_file, index_dir=mdict_index_dir)
                if not idx._title or idx._title == 'Title (No HTML code allowed)':
                    title = name
                else:
                    title = idx._title
                    title = regex_tag.sub(' ', title)

                abouts = []
                abouts.append('<ul>')
                abouts.append('<li>%s</li>' % os.path.basename(idx._mdx_file))
                logger.info('\t+ %s' % os.path.basename(idx._mdx_file))
                for mdd in idx._mdd_files:
                    abouts.append('<li>%s</li>' % os.path.basename(mdd))
                    logger.info('\t+ %s' % os.path.basename(mdd))
                abouts.append('</ul><hr />')
                if idx._description == '<font size=5 color=red>Paste the description of this product in HTML source code format here</font>':
                    text = ''
                else:
                    text = fix_html(idx._description)
                about_html = os.path.join(root, 'about_%s.html' % name)
                if not os.path.exists(about_html):
                    with open(about_html, 'wt', encoding='utf-8') as f:
                        f.write(text)
                if False:
                    text = regex_style.sub('', text)
                    text = regex_ln.sub('\n', text)
                    text = regex_tag.sub(' ', text)
                    text = [t for t in [t.strip() for t in text.split('\n')] if t]
                    abouts.append('<p>' + '<br />\n'.join(text) + '</p>')
                else:
                    abouts.append(text)
                about = '\n'.join(abouts)
                mdicts[dict_uuid] = {
                    'title': title,
                    'uuid': dict_uuid,
                    'logo': logo,
                    'about': about,
                    'root_path': root,
                    'query': idx,
                    'cache': {},
                    'type': 'mdict',
                    'error': '',
                    'enable': enable,
                }

    init_plugins(mdicts, mdict_setting, db_names)

    logger.info('--- MDict is Ready ---')
    return mdicts, db_names


def init_plugins(mdicts, mdict_setting, db_names):
    if getattr(sys, 'frozen', False) and hasattr(sys, '_MEIPASS'):
        plugins_dir = os.path.abspath(os.path.join(sys._MEIPASS, 'flask_mdict', 'plugins'))
    else:
        plugins_dir = os.path.join(os.path.dirname(__file__), 'plugins')

    exclude_files = ['__init__.py']
    for file in os.listdir(plugins_dir):
        if file.endswith('.py') and file not in exclude_files:
            modulename = os.path.splitext(file)[0]
            module = import_module('flask_mdict.plugins.%s' % (modulename))
            config = module.init()
            if config['enable']:
                config['plugins_dir'] = plugins_dir
                dict_uuid = config['uuid']
                mdicts[dict_uuid] = config
                enable = mdict_setting.get(dict_uuid, False)
                config['enable'] = enable
                db_names[dict_uuid] = None
                logger.info('Add "%s" [%s]...' % (config['title'], 'Enable' if enable else 'Disable'))
            else:
                logger.info('Skip "%s" [%s]...' % (config['title'], 'Disable'))


regex_css_comment = re.compile(r'(/\*.*?\*/)', re.DOTALL)
regex_css_tags = re.compile(r'([^}/;]+?){')


def fix_css(prefix_id, css_data):
    def replace(mo):
        tags = mo.group(1).strip()
        if not tags or tags.startswith('@'):
            return mo.group(0)
        else:
            fix_tags = []
            for tag in tags.split(','):
                tag = tag.strip()
                fix_tags.append(f'{prefix_id} .mdict {tag}')
            return '\n%s {' % ','.join(fix_tags)
    data = regex_css_comment.sub('', css_data)
    data = regex_css_tags.sub(replace, data)
    return data


regex_opened_tag = re.compile(r'<([a-z]+)(?: .*?)?>', re.DOTALL | re.IGNORECASE)
regex_closed_tag = re.compile(r'</([a-z]+)>', re.IGNORECASE)


def fix_html(html_data):
    opened_tags = regex_opened_tag.findall(html_data)
    closed_tags = regex_closed_tag.findall(html_data)
    opened_tags = [tag.lower() for tag in opened_tags]
    closed_tags = [tag.lower() for tag in closed_tags]
    # remove single tag
    for tag in ['img', 'link', 'input', 'br', 'hr', 'p', 'meta']:
        while tag in opened_tags:
            opened_tags.remove(tag)
        while tag in closed_tags:
            closed_tags.remove(tag)
    if len(opened_tags) == len(closed_tags):
        return html_data
    for tag in opened_tags[::-1]:
        if tag in closed_tags:
            closed_tags.remove(tag)
        else:
            html_data += '</%s>' % tag
    for tag in closed_tags:
        html_data = '<%s>' % tag + html_data
    return html_data
