
import os.path
import sqlite3


class DBDict(object):
    _db_name = None
    _meta = None
    is_mdd = False

    def __init__(self, db_name):
        if not os.path.exists(db_name):
            return
        sql = 'SELECT name FROM sqlite_master WHERE type="table" AND name=?'
        with sqlite3.connect(db_name) as conn:
            c = conn.execute(sql, ('meta', ))
            meta_row = c.fetchone()
            c = conn.execute(sql, ('mdx', ))
            mdx_row = c.fetchone()
            if not meta_row or not mdx_row:
                return
            self._db_name = db_name
            c = conn.execute(sql, ('mdd', ))
            mdd_row = c.fetchone()
            if mdd_row:
                self._is_mdd = True

            self._meta = {}
            sql = 'SELECT * FROM meta'
            cursor = conn.execute(sql)
            for row in cursor.fetchall():
                self._meta[row[0].lower()] = row[1]

    def is_ok(self):
        return bool(self._db_name)

    def is_mdd(self):
        return self._is_mdd

    def title(self):
        return self._meta.get('title')

    def about(self):
        abouts = []
        with sqlite3.connect(self._db_name) as conn:
            sql = 'SELECT count(*) FROM mdx'
            cursor = conn.execute(sql)
            row = cursor.fetchone()
            mdx_count = row[0]

            sql = 'SELECT count(*) FROM mdx'
            cursor = conn.execute(sql)
            row = cursor.fetchone()
            mdd_count = row[0]

            abouts.append('<ul>')
            abouts.append('<li>%s[MDX][%s]</li>' % (os.path.basename(self._db_name), mdx_count))
            if mdd_count:
                abouts.append('<li>%s[MDD][%s]</li>' % (os.path.basename(self._db_name), mdd_count))
            abouts.append('</ul><hr />')
        abouts.append(self._meta['description'])
        return '\n'.join(abouts)

    def get_mdx_keys(self, conn, part):
        sql = 'SELECT entry FROM mdx WHERE entry like ?'
        cursor = conn.execute(sql, ('%%%s%%' % part, ))
        return [row[0] for row in cursor.fetchall()]

    def get_mdd_keys(self, conn, part):
        sql = 'SELECT entry FROM mdd WHERE entry like ?'
        cursor = conn.execute(sql, ('%%%s%%' % part, ))
        return [row[0] for row in cursor.fetchall()]

    def mdx_lookup(self, conn, word, ignorecase=True):
        sql = 'SELECT paraphrase FROM mdx WHERE entry = ?'
        cursor = conn.execute(sql, (word, ))
        return [row[0] for row in cursor.fetchall()]

    def mdd_lookup(self, conn, word, ignorecase=True):
        if not self._is_mdd:
            return []
        sql = 'SELECT file FROM mdd WHERE entry = ?'
        cursor = conn.execute(sql, (word, ))
        row = cursor.fetchone()
        return row
