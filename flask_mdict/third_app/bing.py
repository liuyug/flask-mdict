
import urllib.request
import urllib.parse


def translate(content, item):
    url = "http://api.microsofttranslator.com/v2/ajax.svc/TranslateArray2?"
    data = {}
    data['from'] = '"' + item.get('from_lan', 'en') + '"'
    data['to'] = '"' + item.get('to_lan', 'zh') + '"'
    data['texts'] = '["'
    data['texts'] += content
    data['texts'] += '"]'
    data['options'] = "{}"
    data['oncomplete'] = 'onComplete_3'
    data['onerror'] = 'onError_3'
    data['_'] = '1430745999189'
    data = urllib.parse.urlencode(data).encode('utf-8')
    strUrl = url + data.decode() + "&appId=%223DAEE5B978BA031557E739EE1E2A68CB1FAD5909%22"
    response = urllib.request.urlopen(strUrl)
    str_data = response.read().decode('utf-8')
    tmp, str_data = str_data.split('"TranslatedText":')
    translate_data = str_data[1:str_data.find('"', 1)]
    return [translate_data]


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
