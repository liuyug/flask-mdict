
import re
import os.path
import hashlib


from .mdict_query import IndexBuilder


def init_mdict(mdict_dir):
    mdicts = {}
    for root, dirs, files in os.walk(mdict_dir):
        for fname in files:
            if fname.endswith('.mdx'):
                name = os.path.splitext(fname)[0]
                mdx_file = os.path.join(root, fname)
                md5 = hashlib.md5()
                md5.update(mdx_file.encode('utf-8'))
                print('Initialize MDICT "%s", please wait...' % name)
                idx = IndexBuilder(mdx_file)
                name = name.replace('.', '-')

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
                print('=== %s ===\n%s' % (title, about))
                mdicts[name] = {
                    'title': title,
                    'about': about,
                    'query': idx,
                    'class': 'dict_%s' % md5.hexdigest(),
                }
    return mdicts
