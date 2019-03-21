
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
            basename, _ = os.path.splitext(self._mdd_file)
            for x in range(10):
                mdd_file = '%s.%s.mdd' % (basename, x)
                if os.path.isfile(mdd_file):
                    self._mdd_files.append(mdd_file)

        # check mdd db
        for mdd_file in self._mdd_files[1:]:    # parent class has initialize first item
            mdd_db = mdd_file + '.db'
            if force_rebuild or not os.path.isfile(mdd_db):
                self._make_mdd_index(mdd_db, mdd_file)

    def _make_mdd_index(self, db_name, mdd_name=None):
        if os.path.exists(db_name):
            os.remove(db_name)
        if mdd_name:
            self._mdd_file = mdd_name
        super(IndexBuilder2, self)._make_mdd_index(db_name)
        if self._mdd_files:
            self._mdd_file = self._mdd_files[0]

    def mdd_lookup(self, keyword, ignorecase=None):
        lookup_result_list = []
        for mdd_file in self._mdd_files:
            mdd_db = mdd_file + '.db'
            indexes = self.lookup_indexes(mdd_db, keyword, ignorecase)
            with open(mdd_file, 'rb') as mdd_fobj:
                for index in indexes:
                    lookup_result_list.append(self.get_mdd_by_index(mdd_fobj, index))
        return lookup_result_list

    def get_mdd_keys(self, query=''):
        keys = []
        for mdd_file in self._mdd_files:
            mdd_db = mdd_file + '.db'
            keys.extend(self.get_keys(mdd_db, query))
        return keys
