
import string
import sqlite3
import re
import os.path

from .word_query.mdict_query import IndexBuilder

version = '1.2'


class IndexBuilder2(IndexBuilder):
    _mdd_files = None

    def __init__(self, fname, encoding="", passcode=None,
                 force_rebuild=False, enable_history=False,
                 sql_index=True, check=False):
        super(IndexBuilder2, self).__init__(
            fname, encoding, passcode,
            force_rebuild, enable_history, sql_index, check)

        # all mdd file
        self._mdd_files = []
        if self._mdd_file:
            self._mdd_files.append(self._mdd_file)
        dirname = os.path.dirname(self._mdx_file)
        basename = os.path.basename(self._mdx_file)
        name, _ = os.path.splitext(basename)
        regex_mdd = re.compile(r'^(.+?)\..+?\.mdd$')
        for fname in os.listdir(dirname):
            m = regex_mdd.match(fname)
            if m and m.group(1) == name:
                self._mdd_files.append(os.path.join(dirname, fname))

        # check mdd db
        for mdd_file in self._mdd_files:    # parent class has initialize first item
            if mdd_file == self._mdd_file:
                continue
            mdd_db = mdd_file + '.db'
            if force_rebuild or not os.path.isfile(mdd_db):
                self._make_mdd_index(mdd_db, mdd_file)

    def _make_mdx_index(self, db_name):
        super(IndexBuilder2, self)._make_mdx_index(db_name)

        pattern = '[%s ]' % string.punctuation.replace('@', '')
        regex_strip = re.compile(pattern)

        conn = sqlite3.connect(db_name)
        c = conn.cursor()
        fix_keys = []
        for row in c.execute('SELECT * FROM MDX_INDEX').fetchall():
            fix_key = regex_strip.sub(' ', row[0].strip())
            if fix_key != row[0]:
                fix_keys.append((fix_key,) + row[1:])
        c.executemany('INSERT INTO MDX_INDEX VALUES (?,?,?,?,?,?,?,?)', fix_keys)
        conn.commit()
        conn.close()

    def _make_mdd_index(self, db_name, mdd_name=None):
        if os.path.exists(db_name):
            os.remove(db_name)
        old_mdd_file = self._mdd_file
        if mdd_name:
            self._mdd_file = mdd_name
        super(IndexBuilder2, self)._make_mdd_index(db_name)
        self._mdd_file = old_mdd_file

    def mdx_lookup(self, conn, keyword, ignorecase=None):
        if not os.path.exists(self._mdx_db):
            return []
        return super(IndexBuilder2, self).mdx_lookup(keyword, ignorecase)

    def mdd_lookup(self, conn, keyword, ignorecase=None):
        """ MDD is resource file, should always return one file """
        for mdd_file in self._mdd_files:
            mdd_db = mdd_file + '.db'
            if not os.path.exists(mdd_db):
                continue
            indexes = self.lookup_indexes(mdd_db, keyword, ignorecase)
            if indexes:
                with open(mdd_file, 'rb') as mdd_fobj:
                    return self.get_mdd_by_index(mdd_fobj, indexes[0])

    def get_mdx_keys(self, conn, query=''):
        return super(IndexBuilder2, self).get_mdx_keys(query)

    def get_mdd_keys(self, conn, query=''):
        keys = []
        for mdd_file in self._mdd_files:
            mdd_db = mdd_file + '.db'
            keys.extend(self.get_keys(mdd_db, query))
        return keys
