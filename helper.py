
import re
import os.path
import hashlib

from scss import Scss

from .mdict_query2 import IndexBuilder2


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
                title = re.sub(r'<[^>]+>', ' ', idx._title)

            abouts = []
            abouts.append('<ul>')
            abouts.append('<li>%s</li>' % os.path.basename(idx._mdx_file))
            if idx._mdd_file:
                abouts.append('<li>%s</li>' % os.path.basename(idx._mdd_file))
            abouts.append('</ul>')
            text = re.sub(r'<[^>]+>', ' ', idx._description)
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


def fix_css(prefix_id, css_data):
    # with compressed
    css = Scss(scss_opts={'style': True})
    data = css.compile('#%s .mdict { %s }' % (prefix_id, css_data))
    data = re.sub(r'(#%s .mdict\s+)body' % prefix_id, r'body \1', data)
    return data
