#!/usr/bin/env python
# -*- encoding:utf-8 -*-


from pypinyin import pinyin, FIRST_LETTER


def f2h(char, errors=None):
    """ half-width char to full-width char
    全角空格为12288，半角空格为32
    其他字符半角(33-126)与全角(65281-65374)的对应关系是：均相差65248
    """
    halfs = [chr(x) for x in range(32, 127)]
    fulls = [unichr(x + 65248) for x in range(32, 127)]
    f2h_data = {
        '　': ' ',
        '。': '.',
        '“': '"',
        '”': '"',
        '‘': "'",
        '’': "'",
        # '》》
        '『': '{',
        '』': '}',
        '【': '[',
        '】': ']',
    }
    if char in fulls:
        index = fulls.index(char)
        new_char = halfs[index]
    else:
        new_char = f2h_data.get(char, char)
    return new_char


def pyabbr(words):
    return ''.join([x[0] for x in pinyin(words, style=FIRST_LETTER, errors=f2h)]).replace(' ', '').lower()
