
import os.path


from .mdict_query import IndexBuilder


def init_mdict(mdict_dir):
    mdicts = {}
    for root, dirs, files in os.walk(mdict_dir):
        for fname in files:
            if fname.endswith('.mdx'):
                name = os.path.splitext(fname)[0]
                mdx_file = os.path.join(root, fname)
                print('Initialize MDICT "%s", please wait...' % name)
                idx = IndexBuilder(mdx_file)
                print('%s: %s' % (idx._title, idx._description))
                if idx._title == 'Title (No HTML code allowed)':
                    idx._title = name
                mdicts[name] = idx
    return mdicts
