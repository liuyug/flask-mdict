
import io
import re
import os.path

from flask import render_template, send_file, url_for,  \
    redirect, abort, jsonify

from .forms import WordForm
from . import mdict, get_mdict, Config
from . import helper


regex_src_schema = re.compile(r'([ "]src=")(/|file:///)?(.+?")')
regex_href_end_slash = re.compile(r'([ "]href=".+?)(/)(")')
regex_href_schema = re.compile(r'([ "]href=")(sound://|entry://|http://|https://)([^#].+?")')
regex_href_no_schema = re.compile(r'([ "]href=")(?!=sound://|entry://|http://|https://)([^#].+?")')


@mdict.route('/query/<part>')
def query_part(part):
    contents = set()
    for uuid, item in get_mdict().items():
        content = item['query'].get_mdx_keys(part)
        contents |= set(content)
    return jsonify(suggestion=sorted(contents))


@mdict.route('/<uuid>/<path:url>', methods=['GET', 'POST'])
def query_word(uuid, url):
    form = WordForm()
    if form.validate_on_submit():
        url = form.word.data
    else:
        form.word.data = url

    url = url.strip()
    item = get_mdict().get(uuid)
    if not item:
        return redirect(url_for('.query_word2', word=url))

    if url == '@list_mdx':
        contents = item['query'].get_mdx_keys()
        return jsonify(suggestion=sorted(contents))
    elif url == '@list_mdd':
        contents = item['query'].get_mdd_keys()
        return jsonify(suggestion=sorted(contents))

    q = item['query']
    if '.' in url:          # file
        fname = os.path.join(item['root_path'], url)
        if url in item:
            data = [item[url]]
        elif os.path.exists(fname):
            data = [open(fname, 'rb').read()]
        elif url == 'logo.png':
            with mdict.open_resource('static/logo.png') as f:
                data = [f.read()]
        else:
            key = '\\%s' % '\\'.join(url.split('/'))
            data = q.mdd_lookup(key, ignorecase=True)

        if data:
            data = b''.join(data)
            if url not in item and url[-4:] in ['.css', '.png', '.jpg']:
                if url.endswith('.css'):
                    try:
                        s_data = data.decode('utf-8')
                        s_data = helper.fix_css('class_%s' % uuid, s_data)
                        data = s_data.encode('utf-8')
                    except Exception as err:
                        error_css = fname + '.error'
                        with open(error_css, 'wb') as f:
                            f.write(data)
                        print(err)
                        print('Output Error Css:', error_css)
                if Config.MDICT_CACHE:
                    item[url] = data        # cache css file

            bio = io.BytesIO()
            bio.write(data)
            bio.seek(0)
            return send_file(bio, attachment_filename=url)
        else:
            abort(404)
    else:                   # entry and word
        content = q.mdx_lookup(url, ignorecase=True)
        content = ''.join(content)

        content = regex_src_schema.sub(r'\1\3', content)
        content = regex_href_end_slash.sub(r'\1\3', content)

        contents = {}
        contents[uuid] = {
            'title': item['title'],
            'logo': item['logo'],
            'about': item['about'],
            'content': content,
        }
        word_meta = helper.query_word_meta(url)
        return render_template(
            'mdict/query.html',
            form=form,
            word=url,
            word_meta=word_meta,
            contents=contents,
        )


@mdict.route('/', methods=['GET', 'POST'])
@mdict.route('/<word>', methods=['GET', 'POST'])
def query_word2(word=None):
    form = WordForm()
    if form.validate_on_submit():
        word = form.word.data
    else:
        word = word or helper.ecdict_random_word('cet4')
        form.word.data = word

    word = word.strip()
    contents = {}
    for uuid, item in get_mdict().items():
        q = item['query']
        content = q.mdx_lookup(word, ignorecase=True)
        if content:
            content = ''.join(content)
            # add dict uuid into url
            content = regex_src_schema.sub(r'\g<1>%s/\3' % uuid, content)
            content = regex_href_end_slash.sub(r'\1\3', content)
            content = regex_href_schema.sub(r'\1\g<2>%s/\3' % uuid, content)
            content = regex_href_no_schema.sub(r'\g<1>%s/\2' % uuid, content)

        contents[uuid] = {
            'title': item['title'],
            'logo': item['logo'],
            'about': item['about'],
            'content': content,
        }

    word_meta = helper.query_word_meta(word)
    return render_template(
        'mdict/query.html',
        form=form,
        word=word,
        word_meta=word_meta,
        contents=contents,
    )
