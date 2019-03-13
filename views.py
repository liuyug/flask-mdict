
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
    q = item['query']
    if '.' in url:          # file
        fname = os.path.join(os.path.dirname(q._mdx_file), url)
        if url in item:
            data = [item[url]]
        elif os.path.exists(fname):
            data = [open(fname, 'rb').read()]
        else:
            key = '\\%s' % '\\'.join(url.split('/'))
            data = q.mdd_lookup(key, ignorecase=True)

        if data:
            data = b''.join(data)
            if url not in item and url.endswith('.css'):
                data = re.sub(r'(.*{)', r'.%s \1' % item['class'], data.decode('utf-8'))
                data = data.encode('utf-8')
                item[url] = data        # cache css file

            bio = io.BytesIO()
            bio.write(data)
            bio.seek(0)
            return send_file(bio, attachment_filename=url)
        else:
            abort(404)
    else:                   # entry and word
        content = q.mdx_lookup(url, ignorecase=True)
        content = '<div class="%s">%s</div>' % (item['class'], ''.join(content))
        contents = {}
        contents[name] = {
            'title': item['title'],
            'about': item['about'],
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
            content = content.replace('src="/', 'src="')
            content = content.replace('src="file:///', 'src="')
            content = content.replace('src="', 'src="%s/' % name)

            content = content.replace('href="sound://', 'href2="sound://%s/' % name)
            content = content.replace('href="entry://', 'href2="entry://%s/' % name)
            content = content.replace('href="http://', 'href2="http://')
            content = content.replace('href="https://', 'href2="https://')
            content = content.replace('href="#', 'href2="#')

            content = content.replace('href="', 'href="%s/' % name)
            content = content.replace('href2="', 'href="')
            content = '<div class="%s">%s</div>' % (item['class'], ''.join(content))
        contents[name] = {
            'title': item['title'],
            'about': item['about'],
            'content': content,
        }
    return render_template(
        'mdict/query.html',
        form=form,
        word=word,
        contents=contents,
    )
