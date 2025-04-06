# https://github.com/UlionTse/translators/tree/master
import translators as ts


def translate(content, item):
    try:
        text = ts.translate_text(
            content,
            translator='alibaba',
            from_language=item.get('from_lan', 'auto'),
            to_language=item.get('to_lan', 'zh'),
        )
        return [text]
    except Exception as err:
        return ['Translators error: %s' % (err)]


def init():
    title = '阿里翻译-阿里巴巴'
    dict_uuid = 'alibaba_translate'
    about = 'https://translate.alibaba.com/'
    enable = True
    config = {
        'title': title,
        'uuid': dict_uuid,
        'logo': 'alibaba.ico',
        'about': about,
        'root_path': '',
        'query': translate,
        'cache': {},
        'type': 'app',
        'error': '',
        'enable': enable,
        'from_lan': 'en',
    }
    return config


if __name__ == '__main__':
    content = "How do I access a previous row when iterating through a pandas dataframe? ... How would I access the previous row? I've tried row.shift(1)"
    print(translate(content))
