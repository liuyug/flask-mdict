
import string
import sqlite3
import re
import os.path
import ast

from .word_query.mdict_query import IndexBuilder

version = '1.2'


class IndexBuilder2(IndexBuilder):
    _mdd_files = None
    _index_dir = None

    def __init__(self, fname, encoding="", passcode=None,
                 force_rebuild=False, enable_history=False,
                 sql_index=True, check=False, index_dir=None):
        # from super class
        self._mdx_file = fname
        self._mdd_file = ""
        self._encoding = ''
        self._stylesheet = {}
        self._title = ''
        self._version = ''
        self._description = ''
        self._sql_index = sql_index
        self._check = check

        dirname = os.path.dirname(self._mdx_file)
        basename = os.path.basename(self._mdx_file)
        name, _ = os.path.splitext(basename)

        self._index_dir = index_dir or dirname
        self._mdx_db = self.get_index_db(self._mdx_file, self._index_dir)

        self._mdd_files = []
        if os.path.isfile(os.path.join(dirname, name + '.mdd')):
            self._mdd_file = os.path.join(dirname, name + '.mdd')
            self._mdd_files.append(self._mdd_file)
        regex_mdd = re.compile(r'^(.+?)\..+?\.mdd$')
        for fname in os.listdir(dirname):
            m = regex_mdd.match(fname)
            if m and m.group(1) == name:
                self._mdd_files.append(os.path.join(dirname, fname))

        if force_rebuild or self.is_update(self._mdx_file, self._index_dir):
            self._make_mdx_index(self.get_index_db(self._mdx_file, self._index_dir))
        else:
            # read meta from index db
            conn = sqlite3.connect(self._mdx_db)
            # 判断有无版本号
            cursor = conn.execute("SELECT * FROM META WHERE key = \"version\"")
            for cc in cursor:
                self._version = cc[1]
            cursor = conn.execute("SELECT * FROM META WHERE key = \"encoding\"")
            for cc in cursor:
                self._encoding = cc[1]
            cursor = conn.execute("SELECT * FROM META WHERE key = \"stylesheet\"")
            for cc in cursor:
                self._stylesheet = ast.literal_eval(cc[1])

            cursor = conn.execute("SELECT * FROM META WHERE key = \"title\"")
            for cc in cursor:
                self._title = cc[1]

            cursor = conn.execute("SELECT * FROM META WHERE key = \"description\"")
            for cc in cursor:
                self._description = cc[1]

        if self._mdd_file and self.is_update(self._mdd_file, self._index_dir):
            self._mdd_db = self.get_index_db(self._mdd_file, self._index_dir)
            self._make_mdd_index(self._mdd_db)

        # check mdd db
        for mdd_file in self._mdd_files:    # parent class has initialize first item
            if mdd_file == self._mdd_file:
                continue
            if force_rebuild or self.is_update(mdd_file, self._index_dir):
                self._make_mdd_index(
                    self.get_index_db(mdd_file, self._index_dir),
                    mdd_file
                )

    @classmethod
    def get_index_db(cls, mdx_file, index_dir=None):
        if index_dir:
            basename = os.path.basename(mdx_file)
            db_name = os.path.join(index_dir, basename + '.db')
        else:
            db_name = mdx_file + '.db'
        return db_name

    @classmethod
    def is_update(cls, mdx_file, index_dir=None):
        db_name = cls.get_index_db(mdx_file, index_dir)
        if not os.path.isfile(db_name):
            return True

        m_time = '%s' % os.path.getmtime(mdx_file)

        conn = sqlite3.connect(db_name)
        c = conn.cursor()
        c.execute('SELECT * FROM META where key = "m_time"')
        row = dict(c.fetchall())
        conn.close()
        if not row or m_time != row['m_time']:
            return True

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
        m_time = '%s' % os.path.getmtime(self._mdx_file)
        c.execute('INSERT INTO META VALUES (?,?)', ('m_time', m_time))
        conn.commit()
        conn.close()

    def _make_mdd_index(self, db_name, mdd_name=None):
        if os.path.exists(db_name):
            os.remove(db_name)
        old_mdd_file = self._mdd_file
        if not mdd_name:
            # first mdd, mdd_name is self._mdd_file
            pass
        else:
            # second mdd
            self._mdd_file = mdd_name
        m_time = '%s' % os.path.getmtime(self._mdd_file)
        super(IndexBuilder2, self)._make_mdd_index(db_name)
        self._mdd_file = old_mdd_file

        conn = sqlite3.connect(db_name)
        c = conn.cursor()
        c.execute('''CREATE TABLE META (key text, value text)''')
        conn.commit()
        c.execute('INSERT INTO META VALUES (?,?)', ('m_time', m_time))
        conn.commit()
        conn.close()

    @staticmethod
    def lookup_indexes(db, keyword, ignorecase=None):
        indexes = []
        with sqlite3.connect(db) as conn:
            if ignorecase:
                sql = 'SELECT * FROM MDX_INDEX WHERE lower(key_text) = ?'
                cursor = conn.execute(sql, (keyword.lower(), ))
            else:
                sql = 'SELECT * FROM MDX_INDEX WHERE key_text = ?'
                cursor = conn.execute(sql, (keyword, ))

            for result in cursor:
                index = {}
                index['file_pos'] = result[1]
                index['compressed_size'] = result[2]
                index['decompressed_size'] = result[3]
                index['record_block_type'] = result[4]
                index['record_start'] = result[5]
                index['record_end'] = result[6]
                index['offset'] = result[7]
                indexes.append(index)
        return indexes

    def mdx_lookup(self, conn, keyword, ignorecase=None):
        if not os.path.exists(self._mdx_db):
            return []
        # return super(IndexBuilder2, self).mdx_lookup(keyword, ignorecase)
        # super mdx_lookup code
        lookup_result_list = []
        indexes = self.lookup_indexes(self._mdx_db, keyword, ignorecase)
        with open(self._mdx_file, 'rb') as mdx_file:
            for index in indexes:
                lookup_result_list.append(self.get_mdx_by_index(mdx_file, index))
        return lookup_result_list

    def mdd_lookup(self, conn, keyword, ignorecase=None):
        """ MDD is resource file, should always return one file """
        for mdd_file in self._mdd_files:
            mdd_db = self.get_index_db(mdd_file, self._index_dir)
            if not os.path.exists(mdd_db):
                continue
            indexes = self.lookup_indexes(mdd_db, keyword, ignorecase)
            if indexes:
                with open(mdd_file, 'rb') as mdd_fobj:
                    return self.get_mdd_by_index(mdd_fobj, indexes[0])

    @staticmethod
    def get_keys(db, query=''):
        if not db:
            return []
        with sqlite3.connect(db) as conn:
            if query:
                if '*' in query:
                    query = query.replace('*', '%')
                else:
                    query = query + '%'
                sql = 'SELECT key_text FROM MDX_INDEX WHERE key_text LIKE ?;'
                cursor = conn.execute(sql, (query,))
            else:
                sql = 'SELECT key_text FROM MDX_INDEX;'
                cursor = conn.execute(sql)

            keys = [item[0] for item in cursor]
            return keys

    def get_mdx_keys(self, conn, query=''):
        return self.get_keys(self._mdx_db, query)

    def get_mdd_keys(self, conn, query=''):
        keys = []
        for mdd_file in self._mdd_files:
            mdd_db = self.get_index_db(mdd_file, self._index_dir)
            keys.extend(self.get_keys(mdd_db, query))
        return keys
