
# http://github.com/UlionTse/translators/tree/master
import translators as ts


def translate(content, item):
    try:
        text = ts.translate_text(
            content,
            translator='iciba',
            from_language=item.get('from_lan', 'auto'),
            to_language=item.get('to_lan', 'zh'),
        )
        return [text]
    except Exception as err:
        return ['Translators error: %s' % (err)]


def init():
    title = '金山词霸 - 在线翻译'
    dict_uuid = 'iciba_translate'
    about = 'http://www.iciba.com/fy'
    enable = False
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
