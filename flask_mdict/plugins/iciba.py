
# http://github.com/UlionTse/translators/tree/master
import translators as ts


def translate(content, item):
    text = ts.translate_text(
        content,
        translator='iciba',
        to_language=item.get('to_lan', 'zh'),
    )
    return [text]


def init():
    title = '金山词霸 - 在线翻译'
    dict_uuid = 'iciba_translate'
    about = 'http://www.iciba.com/fy'
    enable = True
    config = {
        'title': title,
        'uuid': dict_uuid,
        'logo': 'iciba.ico',
        'about': about,
        'root_path': '',
        'query': translate,
        'cache': {},
        'type': 'app',
        'error': '',
        'enable': enable,
    }
    return config
