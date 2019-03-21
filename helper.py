
import re
import uuid
import os.path
import sqlite3

from flask import url_for
from scss import Scss

from . import Config
from .mdict_query2 import IndexBuilder2


regex_style = re.compile(r'<style.+?</style>', re.DOTALL | re.IGNORECASE)
regex_ln = re.compile(r'<(p|br|tr)[^>]*?>', re.IGNORECASE)
regex_tag = re.compile(r'<[^>]+?>')


def init_ecdict(mdict_dir):
    ecdict_fname = os.path.join(mdict_dir, 'ecdict.db')
    if os.path.exists(ecdict_fname):
        return ecdict_fname
    else:
        print('Do not find ECDICT "%s"' % ecdict_fname)


def ecdict_query(word):
    db = Config.ECDICT_DBNAME
    if not db:
        return []
    sql = 'SELECT * FROM ecdict where WORD = ?'
    with sqlite3.connect(db) as conn:
        conn.row_factory = sqlite3.Row
        cursor = conn.execute(sql, (word, ))
        keys = [dict(item) for item in cursor]
        return keys


def ecdict_random_word(tag):
    word = ['hello']
    db = Config.ECDICT_DBNAME
    if not db:
        return word[0]
    sql = 'SELECT * FROM ecdict WHERE word IN (SELECT word FROM ecdict WHERE ecdict.tag like ? ORDER BY RANDOM() LIMIT 1)'
    with sqlite3.connect(db) as conn:
        cursor = conn.execute(sql, ('%%%s%%' % tag, ))
        word = cursor.fetchone()
    return word[0]


def query_word_meta(word):
    TAGs = {
        'zk': '中考',
        'gk': '高考',
        'ky': '研考',
        'cet4': 'CET-4',
        'cet6': 'CET-6',
        'gre': 'GRE',
        'toefl': 'TOEFL',
        'ielts': 'IELTS',
    }
    keys = ecdict_query(word)
    word_meta = []
    if keys:
        key = keys[0]
        if key['oxford']:
            word_meta.append('<a href="https://www.oxfordlearnersdictionaries.com/us/wordlist/english/oxford3000/" target="_blank">'
                             '<img src="%s" style="height:16px" title="Oxford 3000"/>'
                             '</a>' % url_for('.static', filename='Ox3000_Rect1_mod_web.png')
                             )
        if key['collins']:
            # star = '⭐'
            star = '<i class="text-warning fas fa-star"></i>'
            n = int(key['collins'])
            word_meta.append('<span title="Collins %s star">%s</span>' % (n, star * n))
        if key['tag']:
            tags = ['<span class="badge badge-pill badge-primary">%s</span>' % TAGs.get(t, t) for t in key['tag'].split(' ')]
            word_meta.extend(tags)
        if key['bnc']:
            word_meta.append('<a href="http://www.natcorp.ox.ac.uk/" target="_blank">'
                             '<span class="badge badge-pill badge-info" title="BNC: %s">BNC: %s</span>'
                             '</a>' % (key['bnc'], key['bnc']))
        if key['frq']:
            word_meta.append('<a href="https://www.english-corpora.org/coca/" target="_blank">'
                             '<span class="badge badge-pill badge-info" title="COCA: %s">COCA: %s</span>'
                             '</a>' % (key['frq'], key['frq']))
    return ' '.join(word_meta)


def init_mdict(mdict_dir):
    mdicts = {}
    for root, dirs, files in os.walk(mdict_dir):
        for fname in files:
            if not fname.endswith('.mdx'):
                continue
            name = os.path.splitext(fname)[0]
            print('Initialize MDICT "%s", please wait...' % name)
            logo = 'logo.png'
            for ext in ['.jpg', '.png']:
                if os.path.exists(os.path.join(root, name + ext)):
                    logo = name + ext
                    break
            mdx_file = os.path.join(root, fname)
            dict_uuid = str(uuid.uuid3(uuid.NAMESPACE_URL, mdx_file)).upper()

            idx = IndexBuilder2(mdx_file)
            if not idx._title or idx._title == 'Title (No HTML code allowed)':
                title = name
            else:
                title = idx._title
                title = regex_tag.sub(' ', title)

            abouts = []
            abouts.append('<ul>')
            abouts.append('<li>%s</li>' % os.path.basename(idx._mdx_file))
            for mdd in idx._mdd_files:
                abouts.append('<li>%s</li>' % os.path.basename(mdd))
            abouts.append('</ul><hr />')
            if idx._description == '<font size=5 color=red>Paste the description of this product in HTML source code format here</font>':
                text = ''
            else:
                text = idx._description
            about_html = os.path.join(root, 'about_%s.html' % name)
            if not os.path.exists(about_html):
                with open(about_html, 'wt') as f:
                    f.write(text)
            text = regex_style.sub('', text)
            text = regex_ln.sub('\n', text)
            text = regex_tag.sub(' ', text)
            text = [t for t in [t.strip() for t in text.split('\n')] if t]
            abouts.append('<p>' + '<br />\n'.join(text) + '</p>')
            about = '\n'.join(abouts)
            print('=== %s ===\nuuid: %s\n%s' % (title, dict_uuid, about))
            mdicts[dict_uuid] = {
                'title': title,
                'logo': logo,
                'about': about,
                'root_path': root,
                'query': idx,
            }
    print('--- MDict is Ready ---')
    return mdicts


regex_body = re.compile(r'(#\S+ .mdict)\s+?(body)\s*?({)')
regex_fontface = re.compile(r'(@font-face{.+?})')


def fix_css(prefix_id, css_data):
    # remove fontface with scss bug
    fontface = []
    for m in regex_fontface.findall(css_data):
        fontface.append(m)
    data = regex_fontface.sub('', css_data)

    # with compressed
    css = Scss(scss_opts={'style': True})
    data = css.compile('#%s .mdict { %s }' % (prefix_id, data))

    data = regex_body.sub(r'\2 \1 \3', data)
    # add fontface
    data = '\n'.join(fontface) + data
    return data
