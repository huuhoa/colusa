import re
import json
import os
import pathlib

from bs4 import Tag, BeautifulSoup

from colusa.etr import Extractor, Transformer, register_extractor, register_transformer
from colusa import logs
from colusa.utils import get_hexdigest


@register_extractor('//hbr.org')
class HBRExtractor(Extractor):
    def _find_main_content(self):
        import json
        from urllib.parse import urlparse
        script = self.bs.find('script', id="__NEXT_DATA__")
        data = json.loads(script.text)
        data = data['props']['pageProps']['article']
        endpoint_url = 'https://platform.hbr.org/hbr/bff/content/article' + urlparse(self.url_path).path
        key_ = {
            'contentKey': data['contentKey'],
        }
        body = self.__download_content(endpoint_url, content_key=key_)
        return BeautifulSoup(body['content'], 'html.parser')

    def __download_content(self, endpoint_url: str, content_key):
        """
        Download the main content from HBR platform.

        Caches the result to avoid multiple downloads.        
        """
        from colusa.fetch import Fetch, Downloader

        # Create cache key from endpoint and content_key
        key_str = f"{endpoint_url}|{json.dumps(content_key, sort_keys=True)}"
        cache_dir = os.path.join(self.cached_path, 'hbr_cache')
        os.makedirs(cache_dir, exist_ok=True)
        cache_file = os.path.join(cache_dir, f"{get_hexdigest(key_str)}.json")

        # Check if cached
        if os.path.exists(cache_file):
            with open(cache_file, 'r', encoding='utf-8') as f:
                logs.info(f"Loading cached content for {endpoint_url}")
                return json.load(f)

        # Download content
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
            data=json.dumps(content_key),
        )
        body = res.json()

        # Cache the result
        with open(cache_file, 'w', encoding='utf-8') as f:
            json.dump(body, f)

        return body

    def cleanup(self):
        self.remove_tag(self.main_content, 'div', attrs={'class': 'left-rail--container'})
        self.remove_tag(self.main_content, 'div', attrs={'class': 'translate-message'})
        self.remove_tag(self.main_content, 'div', attrs={'class': 'right-rail--container'})
        self.remove_tag(self.main_content, 'div', attrs={'class': 'post-container'})

