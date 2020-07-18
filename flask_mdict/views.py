import io
import re
import os.path

from flask import render_template, send_file, url_for,  \
    redirect, abort, jsonify

from .forms import WordForm
from . import mdict, get_mdict, get_db, Config
from . import helper


regex_word_link = re.compile(r'^(@@@LINK=)(.+)$')
regex_src_schema = re.compile(r'([ "]src=["\'])(/|file:///)?(?!data:)(.+?["\'])')
regex_href_end_slash = re.compile(r'([ "]href=["\'].+?)(/)(["\'])')
regex_href_schema = re.compile(r'([ "]href=["\'])(sound://|entry://)([^#].+?["\'])')
regex_href_no_schema = re.compile(r'([ "]href=["\'])(?!sound://|entry://)([^#].+?["\'])')


@mdict.route('/search/<part>')
def query_part(part):
    contents = set()
    for uuid, item in get_mdict().items():
        content = item['query'].get_mdx_keys(get_db(uuid), part)
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

    q = item['query']
    if '.' in url and url[-1] != '.' and url[0] != '.':    # file
        fname = os.path.join(item['root_path'], url)
        if url in item:
            data = item[url]
        elif os.path.exists(fname):
            data = open(fname, 'rb').read()
        elif url == 'logo.png':
            with mdict.open_resource(os.path.join('static', 'logo.png')) as f:
                data = f.read()
        else:
            key = '\\%s' % '\\'.join(url.split('/'))
            data = q.mdd_lookup(get_db(uuid), key, ignorecase=True)

        if data:
            ext = url.rpartition('.')[-1]
            if url not in item and ext in ['css', 'js', 'png', 'jpg', 'woff2']:
                if url.endswith('.css'):
                    try:
                        s_data = data.decode('utf-8')
                        s_data = helper.fix_css('class_%s' % uuid, s_data)
                        data = s_data.encode('utf-8')
                        item['error'] = ''
                    except Exception as err:
                        err_msg = 'Error: %s - %s' % (url, err.format_original_error())
                        print(err_msg)
                        item['error'] = err_msg
                        abort(404)
                if Config.MDICT_CACHE:
                    item[url] = data        # cache css file

            bio = io.BytesIO()
            bio.write(data)
            bio.seek(0)
            return send_file(bio, attachment_filename=url)
        else:
            abort(404)
    else:                   # entry and word
        records = q.mdx_lookup(get_db(uuid), url, ignorecase=True)
        html_content = []
        if item['error']:
            html_content.append('<div style="color: red;">%s</div>' % item['error'])
        for record in records:
            record = helper.fix_html(record)
            mo = regex_word_link.match(record)
            if mo:
                link = mo.group(2).strip()
                if '#' in link:
                    link, anchor = link.split('#')
                    return redirect(url_for('.query_word', uuid=uuid, url=link, _anchor=anchor))
                else:
                    record = '<p>Also: <a href="%s">%s</a></p>' % (
                        url_for('.query_word', uuid=uuid, url=link),
                        link,
                    )
            else:
                record = regex_src_schema.sub(r'\1\3', record)
                record = regex_href_end_slash.sub(r'\1\3', record)
            html_content.append(record)
        html_content = '<hr />'.join(html_content)
        about = item['about']
        about = regex_href_end_slash.sub(r'\1\3', about)

        contents = {}
        contents[uuid] = {
            'title': item['title'],
            'logo': item['logo'],
            'about': about,
            'content': html_content,
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
@mdict.route('/query/<word>', methods=['GET', 'POST'])
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
        records = q.mdx_lookup(get_db(uuid), word, ignorecase=True)
        html_content = []
        if item['error']:
            html_content.append('<div style="color: red;">%s</div>' % item['error'])
        for record in records:
            record = helper.fix_html(record)
            mo = regex_word_link.match(record)
            if mo:
                link = mo.group(2).strip()
                if '#' in link:
                    link, anchor = link.split('#')
                    return redirect(url_for('.query_word2', word=link, _anchor=anchor))
                else:
                    record = '<p>Also: <a href="%s">%s</a></p>' % (
                        url_for('.query_word2', word=link),
                        link,
                    )
            else:
                # add dict uuid into url
                record = regex_src_schema.sub(r'\g<1>%s/\3' % uuid, record)
                record = regex_href_end_slash.sub(r'\1\3', record)
                record = regex_href_schema.sub(r'\1\g<2>%s/\3' % uuid, record)
                record = regex_href_no_schema.sub(r'\g<1>%s/\2' % uuid, record)
            html_content.append(record)
        html_content = '<hr />'.join(html_content)
        about = item['about']
        about = regex_src_schema.sub(r'\g<1>%s/\3' % uuid, about)
        about = regex_href_end_slash.sub(r'\1\3', about)
        about = regex_href_schema.sub(r'\1\g<2>%s/\3' % uuid, about)
        contents[uuid] = {
            'title': item['title'],
            'logo': item['logo'],
            'about': about,
            'content': html_content,
        }

    word_meta = helper.query_word_meta(word)
    return render_template(
        'mdict/query.html',
        form=form,
        word=word,
        word_meta=word_meta,
        contents=contents,
    )
