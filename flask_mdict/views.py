import io
import re
import os.path

from flask import render_template, send_file, url_for,  \
    redirect, abort, jsonify, request

from .forms import WordForm
from . import mdict, get_mdict, get_db, Config
from . import helper


regex_word_link = re.compile(r'^(@@@LINK=)(.+)$')
# img src
regex_src_schema = re.compile(r'([ "]src=["\'])(/|file:///)?(?!data:)(.+?["\'])')
# http://.../
regex_href_end_slash = re.compile(r'([ "]href=["\'].+?)(/)(["\'])')
# sound://
regex_href_schema_sound = re.compile(r'([ "]href=["\'])(sound://)([^#].+?["\'])')
# entry://
regex_href_schema_entry = re.compile(r'([ "]href=["\'])(entry://)([^#].+?["\'])')
# default: http
regex_href_no_schema = re.compile(r'([ "]href=["\'])(?!sound://|entry://)([^#].+?["\'])')


@mdict.route('/search/<part>')
def query_part(part):
    contents = set()
    for uuid, item in get_mdict().items():
        if item['type'] == 'app':
            continue
        content = item['query'].get_mdx_keys(get_db(uuid), part)
        contents |= set(content)
    return jsonify(suggestion=sorted(contents))


@mdict.route('/<uuid>/resource/<path:resource>', methods=['GET', 'POST'])
def query_resource(uuid, resource):
    resource = resource.strip()
    item = get_mdict().get(uuid)
    if not item:
        abort(404)

    # file, load from cache, local, static, mdd
    fname = os.path.join(item['root_path'], resource)
    # check cache
    if resource in item:
        data = item['cache'][resource]
    elif os.path.exists(fname):
        data = open(fname, 'rb').read()
    elif resource == 'logo.ico':
        with mdict.open_resource(os.path.join('static', 'logo.ico')) as f:
            data = f.read()
    else:
        q = item['query']
        if item['type'] == 'app':
            with mdict.open_resource(os.path.join('static', resource)) as f:
                data = f.read()
        else:
            key = '\\%s' % '\\'.join(resource.split('/'))
            data = q.mdd_lookup(get_db(uuid), key, ignorecase=True)

    if data:
        ext = resource.rpartition('.')[-1]
        if resource not in item and ext in ['css', 'js', 'png', 'jpg', 'woff2']:
            if resource.endswith('.css'):
                try:
                    s_data = data.decode('utf-8')
                    s_data = helper.fix_css('#class_%s' % uuid, s_data)
                    data = s_data.encode('utf-8')
                    item['error'] = ''
                except Exception as err:
                    err_msg = 'Error: %s - %s' % (resource, err.format_original_error())
                    print(err_msg)
                    item['error'] = err_msg
                    abort(404)
            if Config.MDICT_CACHE:
                item['cache'][resource] = data        # cache css file

        bio = io.BytesIO()
        bio.write(data)
        bio.seek(0)
        return send_file(bio, attachment_filename=resource)
    else:
        abort(404)


@mdict.route('/<uuid>/query/<word>', methods=['GET', 'POST'])
def query_word(uuid, word):
    form = WordForm()
    if form.validate_on_submit():
        word = form.word.data
    else:
        form.word.data = word

    word = word.strip()
    item = get_mdict().get(uuid)
    if not item:
        abort(404)

    # entry and word, load from mdx, db
    q = item['query']
    if item['type'] == 'app':
        records = q(word, item)
    else:
        records = q.mdx_lookup(get_db(uuid), word, ignorecase=True)
    html_content = []
    if item['error']:
        html_content.append('<div style="color: red;">%s</div>' % item['error'])
    prefix_resource = '%s/resource' % '..'
    # prefix_entry = '%s/query' % '..'
    for record in records:
        record = helper.fix_html(record)
        mo = regex_word_link.match(record)
        if mo:
            link = mo.group(2).strip()
            if '#' in link:
                link, anchor = link.split('#')
                return redirect(url_for('.query_resource', uuid=uuid, resource=link, _anchor=anchor))
            else:
                record = '<p>Also: <a href="%s">%s</a></p>' % (
                    f'entry://{link}',
                    link,
                )
        else:
            record = regex_src_schema.sub(r'\g<1>%s/\3' % prefix_resource, record)
            record = regex_href_end_slash.sub(r'\1\3', record)
            record = regex_href_schema_sound.sub(r'\1\g<2>%s/\3' % prefix_resource, record)
            # record = regex_href_schema_entry.sub(r'\1\g<2>%s/\3' % prefix_entry, record)
            record = regex_href_no_schema.sub(r'\g<1>%s/\2' % prefix_resource, record)
        html_content.append(record)
    html_content = '<hr />'.join(html_content)
    about = item['about']
    about = regex_href_end_slash.sub(r'\1\3', about)
    about = regex_src_schema.sub(r'\g<1>%s/\3' % prefix_resource, about)
    about = regex_href_schema_sound.sub(r'\1\g<2>%s/\3' % prefix_resource, about)

    contents = {}
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


@mdict.route('/', methods=['GET', 'POST'])
def query_word_all():
    form = WordForm()
    if form.validate_on_submit():
        word = form.word.data
    else:
        word = request.args.get('word')
        word = word or helper.ecdict_random_word('cet4')
        form.word.data = word

    word = word.strip()
    contents = {}
    for uuid, item in get_mdict().items():
        q = item['query']
        if item['type'] == 'app':
            records = q(word, item)
        else:
            records = q.mdx_lookup(get_db(uuid), word, ignorecase=True)
        html_content = []
        if item['error']:
            html_content.append('<div style="color: red;">%s</div>' % item['error'])
        prefix_resource = '%s/resource' % uuid
        prefix_entry = '%s/query' % uuid
        for record in records:
            record = helper.fix_html(record)
            mo = regex_word_link.match(record)
            if mo:
                link = mo.group(2).strip()
                if '#' in link:
                    link, anchor = link.split('#')
                    return redirect(url_for('.query_word_all', word=link, _anchor=anchor))
                else:
                    record = '<p>Also: <a href="%s">%s</a></p>' % (
                        f'entry://{uuid}/query/{link}',
                        link,
                    )
            else:
                # add dict uuid into url
                record = regex_src_schema.sub(r'\g<1>%s/\3' % prefix_resource, record)
                record = regex_href_end_slash.sub(r'\1\3', record)
                record = regex_href_schema_sound.sub(r'\1\g<2>%s/\3' % prefix_resource, record)
                record = regex_href_schema_entry.sub(r'\1\g<2>%s/\3' % prefix_entry, record)
                record = regex_href_no_schema.sub(r'\g<1>%s/\2' % prefix_resource, record)
            html_content.append(record)
        html_content = '<hr />'.join(html_content)
        about = item['about']
        about = regex_src_schema.sub(r'\g<1>%s/\3' % prefix_resource, about)
        about = regex_href_end_slash.sub(r'\1\3', about)
        about = regex_href_schema_sound.sub(r'\1\g<2>%s/\3' % prefix_resource, about)
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


@mdict.route('/gtranslate/query/<word>', methods=['GET', 'POST'])
def google_translate(word):
    trans = helper.google_translate(word)
    return '\n'.join(trans)
