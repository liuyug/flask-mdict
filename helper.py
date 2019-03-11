
import os.path


from .mdict_query import IndexBuilder


def init_mdict(mdict_dir):
    mdicts = {}
    for root, dirs, files in os.walk(mdict_dir):
        for fname in files:
            if fname.endswith('.mdx'):
                key = os.path.basename(root)
                print('Initialize MDICT "%s/%s", please wait...' % (key, fname))
                mdx_file = os.path.join(root, fname)
                idx = IndexBuilder(mdx_file)
                name = os.path.splitext(fname)[0]
                if idx._title == 'Title (No HTML code allowed)':
                    idx._title = name
                mdicts[key] = idx
    return mdicts
