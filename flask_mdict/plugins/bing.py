
import requests
import re


class BingTranslator:
    name: str = "bing"
    url: str = "http://bing.com/dict/SerpHoverTrans"
    cnurl: str = "http://cn.bing.com/dict/SerpHoverTrans"

    def __init__(self) -> None:
        self.pat_attr = re.compile(
            r'<span class="ht_attr" lang=".*?">\[(.*?)\] </span>'
        )
        self.pat_trs = re.compile(
            r'<span class="ht_pos">(.*?)</span>'
            r'<span class="ht_trs">(.*?)</span>'
        )

        self.session = requests.Session()

    def translate(self, text, tl, sl):
        url = self.cnurl if "zh" in tl else self.url
        params = {"q": text}
        headers = {
            "Accept": (
                "text/html,application/xhtml+xml,application/xml;"
                "q=0.9,*/*;q=0.8"
            ),
            "Accept-Language": "en-US,en;q=0.5",
            "Cookie": "_EDGE_S=mkt=" + tl,
        }
        self.session.headers.update(headers)
        resp = self.session.get(url, params=params)
        if resp.status_code != 200:
            return
        print('result', text, resp.text)
        # phonetic = self.get_phonetic(resp)
        # explains = self.get_explains(resp)
        return resp.text

    def get_phonetic(self, html):
        if not html:
            return ""
        m = self.pat_attr.findall(html)
        if not m:
            return ""
        return m[0]
        # return self.html_unescape(m[0].strip())

    def get_explains(self, html):
        expls = {}
        if not html:
            return expls
        m = self.pat_trs.findall(html)
        for pos, explain in m:
            expls[pos] = explain
        return expls


def translate(content, item):
    b = BingTranslator()
    text = b.translate(content, item.get('from_lan', 'auto'), item.get('to_lan', 'zh'))
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
