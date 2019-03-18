
import re
import os.path
import hashlib
import sqlite3

from flask import url_for
from scss import Scss

from . import get_ecdict_name
from .mdict_query2 import IndexBuilder2


regex_tag = re.compile(r'<[^>]+?>')


def init_ecdict(mdict_dir):
    ecdict_fname = os.path.join(mdict_dir, 'ecdict.db')
    if os.path.exists(ecdict_fname):
        return ecdict_fname


def ecdict_query(word):
    db = get_ecdict_name()
    if not db:
        return []
    sql = 'SELECT * FROM ecdict where WORD = ?'
    with sqlite3.connect(db) as conn:
        conn.row_factory = sqlite3.Row
        cursor = conn.execute(sql, (word, ))
        keys = [dict(item) for item in cursor]
        return keys


def ecdict_random_word(tag):
    db = get_ecdict_name()
    if not db:
        return []
    sql = 'SELECT * FROM ecdict WHERE word IN (SELECT word FROM ecdict WHERE ecdict.tag like ? ORDER BY RANDOM() LIMIT 1)'
    with sqlite3.connect(db) as conn:
        cursor = conn.execute(sql, ('%%%s%%' % tag, ))
        word = cursor.fetchone()
        return word[0]


def word_info(word):
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
    word_info = []
    if keys:
        key = keys[0]
        if key['oxford']:
            word_info.append('<a href="https://www.oxfordlearnersdictionaries.com/us/wordlist/english/oxford3000/" target="_blank">'
                             '<img src="%s" height="16px" title="Oxford 3000"/>'
                             '</a>' % url_for('.static', filename='Ox3000_Rect1_mod_web.png')
                             )
        if key['collins']:
            # star = '⭐'
            star = '<i class="text-warning fas fa-star"></i>'
            n = int(key['collins'])
            word_info.append('<span title="Collins %s star">%s</span>' % (n, star * n))
        if key['tag']:
            tags = ['<span class="badge badge-pill badge-primary">%s</span>' % TAGs.get(t, t) for t in key['tag'].split(' ')]
            word_info.extend(tags)
        if key['bnc']:
            word_info.append('<a href="http://www.natcorp.ox.ac.uk/" target="_blank">'
                             '<span class="badge badge-pill badge-info" title="BNC: %s">BNC: %s</span>'
                             '</a>' % (key['bnc'], key['bnc']))
        if key['frq']:
            word_info.append('<a href="https://www.english-corpora.org/coca/" target="_blank">'
                             '<span class="badge badge-pill badge-info" title="COCA: %s">COCA: %s</span>'
                             '</a>' % (key['frq'], key['frq']))
    return ' '.join(word_info)


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
            md5 = hashlib.md5()
            md5.update(mdx_file.encode('utf-8'))
            dict_id = 'dict_%s' % md5.hexdigest()

            idx = IndexBuilder2(mdx_file)
            if idx._title == 'Title (No HTML code allowed)':
                title = name
            else:
                title = regex_tag.sub(' ', idx._title)

            abouts = []
            abouts.append('<ul>')
            abouts.append('<li>%s</li>' % os.path.basename(idx._mdx_file))
            if idx._mdd_file:
                abouts.append('<li>%s</li>' % os.path.basename(idx._mdd_file))
            abouts.append('</ul>')
            text = regex_tag.sub(' ', idx._description)
            text = [t for t in [t.strip() for t in text.split('\n')] if t]
            abouts.extend(text)
            about = '\n'.join(abouts)
            print('=== %s ===\ndict id: %s\n%s' % (title, dict_id, about))
            mdicts[name] = {
                'title': title,
                'logo': logo,
                'about': about,
                'root_path': root,
                'query': idx,
                'id': dict_id,
            }
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
    # data = '\n'.join(['#%s .mdict %s' % (prefix_id, face) for face in fontface]) + data
    return data
