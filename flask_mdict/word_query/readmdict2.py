from struct import unpack

from .readmdict import MDX as MDXBase, MDD as MDDBase


class Index():
    def get_index(self, check_block=True):
        if self._version >= 3:
            return self.get_index_v3(check_block=check_block)
        else:
            return self.get_index_v1v2(check_block=check_block)

    def get_index_v1v2(self, check_block=True):
        # 获取 mdx 文件的索引列表，格式为
        # key_text(关键词，可以由后面的 keylist 得到)
        # file_pos(record_block开始的位置)
        # compressed_size(record_block压缩前的大小)
        # decompressed_size(解压后的大小)
        # record_block_type(record_block 的压缩类型)
        # record_start (以下三个为从 record_block 中提取某一调记录需要的参数，可以直接保存）
        # record_end
        # offset
        # 所需 metadata
        index_dict_list = []

        f = open(self._fname, 'rb')
        f.seek(self._record_block_offset)

        num_record_blocks = self._read_number(f)
        num_entries = self._read_number(f)
        assert (num_entries == self._num_entries)
        record_block_info_size = self._read_number(f)
        record_block_size = self._read_number(f)

        # record block info section
        record_block_info_list = []
        size_counter = 0
        for i in range(num_record_blocks):
            compressed_size = self._read_number(f)
            decompressed_size = self._read_number(f)
            record_block_info_list += [(compressed_size, decompressed_size)]
            size_counter += self._number_width * 2
        assert (size_counter == record_block_info_size)

        # actual record block
        offset = 0
        i = 0
        size_counter = 0
        for compressed_size, decompressed_size in record_block_info_list:
            current_pos = f.tell()
            record_block_compressed = f.read(compressed_size)
            record_block_type, = unpack('<L', record_block_compressed[:4])

            # split record block according to the offset info from key block
            while i < len(self._key_list):
                index_dict = {}
                index_dict['file_pos'] = current_pos
                index_dict['compressed_size'] = compressed_size
                index_dict['decompressed_size'] = decompressed_size
                index_dict['record_block_type'] = record_block_type

                record_start, key_text = self._key_list[i]
                index_dict['record_start'] = record_start
                index_dict['key_text'] = key_text.decode("utf-8")
                index_dict['offset'] = offset

                # reach the end of current record block
                # next block
                if record_start - offset >= decompressed_size:
                    break

                # record end index
                if i < len(self._key_list) - 1:
                    record_end = self._key_list[i + 1][0]
                else:
                    record_end = decompressed_size + offset
                index_dict['record_end'] = record_end
                i += 1
                index_dict_list.append(index_dict)
            offset += decompressed_size
            size_counter += compressed_size
        assert (size_counter == record_block_size)

        f.close()
        # 这里比 mdd 部分稍有不同，应该还需要传递编码以及样式表信息
        meta = {}
        meta['encoding'] = self._encoding
        meta['stylesheet'] = self._stylesheet
        meta['version'] = self._version
        meta['title'] = self.header[b'Title'].decode(self._encoding)
        meta['description'] = self.header[b'Title'].decode(self._encoding)
        return {"index_dict_list": index_dict_list, 'meta': meta}

    def get_index_v3(self, check_block=False):
        index_dict_list = []

        f = open(self._fname, 'rb')
        f.seek(self._record_block_offset)

        offset = 0
        i = 0
        size_counter = 0

        num_record_blocks = self._read_int32(f)
        num_bytes = self._read_number(f)  # noqa
        for j in range(num_record_blocks):
            current_pos = f.tell()
            decompressed_size = self._read_int32(f)
            compressed_size = self._read_int32(f)
            record_block_compressed = f.read(compressed_size)
            record_block_type, = unpack('<L', record_block_compressed[:4])

            # split record block according to the offset info from key block
            while i < len(self._key_list):
                index_dict = {}
                index_dict['file_pos'] = current_pos
                index_dict['compressed_size'] = compressed_size
                index_dict['decompressed_size'] = decompressed_size
                index_dict['record_block_type'] = record_block_type

                record_start, key_text = self._key_list[i]
                index_dict['record_start'] = record_start
                index_dict['key_text'] = key_text.decode("utf-8")
                index_dict['offset'] = offset

                # reach the end of current record block
                if record_start - offset >= decompressed_size:
                    break
                # record end index
                if i < len(self._key_list) - 1:
                    record_end = self._key_list[i + 1][0]
                else:
                    record_end = decompressed_size + offset

                index_dict['record_end'] = record_end
                i += 1
                index_dict_list.append(index_dict)

            offset += decompressed_size
            size_counter += compressed_size

        f.close()
        # 这里比 mdd 部分稍有不同，应该还需要传递编码以及样式表信息
        meta = {}
        meta['encoding'] = self._encoding
        meta['version'] = self._version
        meta['stylesheet'] = self._stylesheet
        meta['title'] = self.header[b'Title'].decode(self._encoding)
        meta['description'] = self.header[b'Title'].decode(self._encoding)
        return {"index_dict_list": index_dict_list, 'meta': meta}


class MDX(MDXBase, Index):
    pass


class MDD(MDDBase, Index):
    pass
