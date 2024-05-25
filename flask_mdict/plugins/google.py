
from googletranslate.googletranslate import main as gtranslate


def translate(word, item=None):
    """
    python -m googletranslate.googletranslate -s "translate.google.cn" -r plain zh-CN "word"
    """
    class Args:
        target: str = 'zh-CN'
        query: str = ''
        host: str = 'translate.google.com'
        proxy: str = ''
        alternative: str = 'en'
        type: str = 'plain'
        synonyms: bool = False
        definitions: bool = True
        examples: bool = False
        tkk: str = ''
    Args.host = item['root_path'] if item else 'translate.google.cn'
    Args.query = word
    trans = []
    trans_group = []
    result = gtranslate(Args)
    tags = []
    for line in result.split('\n'):
        if not line:
            continue
        elif line == '=========':
            trans_group.append('<div>%s%s</div>' % (
                '<br />'.join(trans),
                ''.join(['</%s>' % t for t in tags[::-1]])
            ))
            trans = []
            tags = []
            continue
        elif line.startswith('^_^:'):
            line = '<span>%s</span>' % line
        elif line.startswith('0_0:'):
            line = '<span>%s</span>' % line
        elif line.startswith('#'):
            if tags:
                line = '</%s><%s>%s' % (tags[-1], tags[-1], line)
            else:
                tags.append('ul')
                tags.append('li')
                line = '<%s><%s>%s' % (tags[-2], tags[-1], line)
        else:
            line = '%s' % line
        trans.append(line)
    if trans:
        trans_group.append('<div>%s%s</div>' % (
            '<br />'.join(trans),
            ''.join(['</%s>' % t for t in tags[::-1]])
        ))
    return trans_group


def init():
    title = 'Google 翻译'
    dict_uuid = 'gtranslate'
    about = 'google-translate-for-goldendict<br />https://github.com/xinebf/google-translate-for-goldendict'
    enable = True
    config = {
        'title': title,
        'uuid': dict_uuid,
        'logo': 'google_translate.ico',
        'about': about,
        'root_path': 'translate.google.com',
        'query': translate,
        'cache': {},
        'type': 'app',
        'error': '',
        'enable': enable,
    }
    return config


if __name__ == '__main__':
    word = 'hello word'
    print('Goolge Translate', word)
    translate(word)
