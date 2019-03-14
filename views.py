
import io
import re
import os.path

from flask import current_app, render_template, send_file, url_for,  \
    redirect, abort, jsonify

from .forms import WordForm
from . import mdict, get_mdict
from . import helper


@mdict.route('/query/<part>')
def query_part(part):
    contents = set()
    for name, item in get_mdict().items():
        content = item['query'].get_mdx_keys(part)
        contents |= set(content)
    return jsonify(suggestion=sorted(contents))


@mdict.route('/<name>/<path:url>', methods=['GET', 'POST'])
def query_word(name, url):
    form = WordForm()
    if form.validate_on_submit():
        url = form.word.data
    else:
        form.word.data = url

    item = get_mdict().get(name)
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
            # return redirect(url_for('.static', filename='logo.png'))
        else:
            key = '\\%s' % '\\'.join(url.split('/'))
            data = q.mdd_lookup(key, ignorecase=True)

        if data:
            data = b''.join(data)
            if url not in item and url[-4:] in ['.css', '.png', '.jpg']:
                if url.endswith('.css'):
                    data = data.decode('utf-8')
                    data = helper.fix_css(item['id'], data)
                    data = data.encode('utf-8')
                if current_app.config.get('MDICT_CACHE'):
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
        content = re.sub(r' src="(/|file:///)', r' src="', content)
        content = re.sub(r' href="(.+?)(/"|")', r' href="\1"', content)

        contents = {}
        contents[name.replace('.', '-')] = {
            'title': item['title'],
            'logo': item['logo'],
            'about': item['about'],
            'id': item['id'],
            'content': content,
        }
        return render_template(
            'mdict/query.html',
            form=form,
            word=url,
            contents=contents,
        )


@mdict.route('/', methods=['GET', 'POST'])
@mdict.route('/<word>', methods=['GET', 'POST'])
def query_word2(word=None):
    form = WordForm()
    if form.validate_on_submit():
        word = form.word.data
    else:
        word = word or 'hello'
        form.word.data = word

    contents = {}
    for name, item in get_mdict().items():
        q = item['query']
        content = q.mdx_lookup(word, ignorecase=True)
        if content:
            content = ''.join(content)
            # add dict name into url
            content = re.sub(r' src="(/|file:///)?', r' src="%s/' % name, content)
            content = re.sub(r' href="(.+?)/"', r' href="\1"', content)
            content = re.sub(r' href="(sound://|entry://|http://|https://)?([^#].+?)"', r' href="\1%s/\2"' % name, content)

        contents[name.replace('.', '-')] = {
            'title': item['title'],
            'logo': item['logo'],
            'about': item['about'],
            'id': item['id'],
            'content': content,
        }
    return render_template(
        'mdict/query.html',
        form=form,
        word=word,
        contents=contents,
    )
