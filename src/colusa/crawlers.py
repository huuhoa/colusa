from colusa import logs
from bs4 import BeautifulSoup
import pathlib
from collections import OrderedDict
from urllib.parse import urljoin
from .utils import scan, download_url, get_hexdigest


class Crawler(object):
    def __init__(self, url, output_dir, output_file):
        self.url = url
        self.output_dir = output_dir
        self.output_file = output_file

    def run(self):
        logs.info(f"hello: {self.url}")
        self.content = self.download_content()
        self.dom = BeautifulSoup(self.content, 'html.parser')

        table_chapter = self.dom.find('table', id='chapters')
        anchors = table_chapter.find_all('a')
        urls = OrderedDict()
        for a in anchors:
            href = a.attrs.get('href')
            final_url = urljoin(self.url, href)
            urls[final_url] = True
        
        import json
        result = [str(k) for k in urls.keys()]
        json.dump(result, self.output_file, indent=3)


    def download_content(self):
        """
        Download html content of given `url_path` then cached in `.cached` folder of local file system
        :param url_path: url of html article
        :return: content of downloaded file
        """
        output_path = pathlib.Path(self.output_dir)
        cached_file_path = output_path.joinpath('.cached', f'{get_hexdigest(self.url)}.html')
        logs.info(self.url, cached_file_path)

        if not cached_file_path.exists():
            # download file from url_path
            download_url(self.url, str(cached_file_path))

        with open(cached_file_path, 'rt', encoding='utf-8') as file_in:
            content = file_in.read()
        return content
