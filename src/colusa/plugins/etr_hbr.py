import re

from bs4 import Tag, BeautifulSoup

from colusa.etr import Extractor, Transformer, register_extractor, register_transformer
from colusa import logs


@register_extractor('//hbr.org')
class HBRExtractor(Extractor):
    def _find_main_content(self):
        import json
        from urllib.parse import urlparse
        from colusa.fetch import Fetch, Downloader
        script = self.bs.find('script', id="__NEXT_DATA__")
        data = json.loads(script.text)
        data = data['props']['pageProps']['article']
        endpoint_url = (
            'https://platform.hbr.org/hbr/bff/content/article' + urlparse(self.url_path).path
        )
        key_ = {
            'contentKey': data['contentKey'],
        }
        headers = {
            'User-Agent': Downloader.UserAgent,
            'Pragma': 'no-cache',
            'Cache-Control': 'no-cache',
            'Content-Type': 'application/json',
        }
        fetcher = Fetch()
        res = fetcher.post(
            endpoint_url,
            headers=headers,
            data=json.dumps(key_),
        )
        body = res.json()
        return BeautifulSoup(body['content'], 'html.parser')


    def cleanup(self):
        self.remove_tag(self.main_content, 'div', attrs={'class': 'left-rail--container'})
        self.remove_tag(self.main_content, 'div', attrs={'class': 'translate-message'})
        self.remove_tag(self.main_content, 'div', attrs={'class': 'right-rail--container'})
        self.remove_tag(self.main_content, 'div', attrs={'class': 'post-container'})

