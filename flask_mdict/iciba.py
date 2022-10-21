
import requests
import hashlib


class Ciba(object):
    base_url = 'http://ifanyi.iciba.com/index.php'
    prefix = '6key_web_fanyi'
    midfix = 'ifanyiweb8hc9s98e'
    # http://ifanyi.iciba.com/index.php?c=trans&m=fy&client=6&auth_user=key_web_fanyi&sign=27554cf4754750b2

    @classmethod
    def fy(cls, entry):
        query_data = {
            'c': 'trans',
            'm': 'fy',
            'client': '6',
            'auth_user': 'key_web_fanyi',
            'sign': '',
        }
        form_data = {
            'from': 'en',
            'to': 'auto',
            'q': entry,
        }

        encrypt_str = f'{cls.prefix}{cls.midfix}{entry}'
        sign_str = hashlib.md5(encrypt_str.encode()).hexdigest()
        query_data['sign'] = sign_str[:16]

        res = requests.post(cls.base_url, params=query_data, data=form_data)
        res.raise_for_status()
        json_data = res.json()
        return json_data


def translate(text, item=None):
    result = Ciba.fy(text)
    content = result['content']
    if content.get('err_no') == 0:
        trans = '<div title="%(ciba_use)s">%(out)s</div>' % content
    else:
        trans = '<div>Translate Error: %s</div>' % content.get('err_no')
    return [trans]


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
