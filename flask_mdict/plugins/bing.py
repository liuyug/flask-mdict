# https://github.com/UlionTse/translators/tree/master
import translators as ts


def translate(content, item):
    text = ts.translate_text(
        content,
        translator='bing',
        to_language=item.get('to_lan', 'zh'),
    )
    return [text]


def init():
    title = '必应翻译'
    dict_uuid = 'bing_translate'
    about = 'https://cn.bing.com/translator/'
    enable = True
    config = {
        'title': title,
        'uuid': dict_uuid,
        'logo': 'bing.svg',
        'about': about,
        'root_path': '',
        'query': translate,
        'cache': {},
        'type': 'app',
        'error': '',
        'enable': enable,
        'from_lan': 'en',
        'to_lan': 'zh',
    }
    return config


if __name__ == '__main__':
    content = "How do I access a previous row when iterating through a pandas dataframe? ... How would I access the previous row? I've tried row.shift(1)"
    print(translate(content))
