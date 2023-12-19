
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
            # 'from': 'en',
            'from': 'auto',
            'to': 'auto',
            'q': entry,
        }

        encrypt_str = f'{cls.prefix}{cls.midfix}{entry}'
        sign_str = hashlib.md5(encrypt_str.encode()).hexdigest()
        query_data['sign'] = sign_str[:16]

        try:
            res = requests.post(cls.base_url, params=query_data, data=form_data)
            res.raise_for_status()
            json_data = res.json()
        except Exception as err:
            if res.content:
                message = res.content.decode()
            else:
                message = str(err)
            json_data = {'content': {
                'err_no': '{}'.format(message),
                'ciba_use': '',
            }}

        return json_data


def translate(text, item=None):
    result = Ciba.fy(text)
    content = result.get('content')
    if content:
        if content.get('err_no') == 0:
            out = content.get('out', '')
            ciba_use = content.get('ciba_use', '')
            trans = f'<div title="{ciba_use}">{out}</div>'
        else:
            trans = '<div>Translate Error: %s</div>' % content.get('err_no')
    elif 'error_code' in result:
        trans = '<div>Translate Error: {error_code} - {message}</div>'.format(**result)
    else:
        trans = str(result)
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
