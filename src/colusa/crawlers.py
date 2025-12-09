from typing import Any, TextIO
from colusa import logs
from colusa.fetch import Downloader
from bs4 import BeautifulSoup
import pathlib
from collections import OrderedDict
from urllib.parse import urljoin
from colusa import utils


class Crawler:
    def __init__(self, url: str, output_dir: str, output_file: TextIO) -> None:
        self.url: str = url
        self.output_dir: str = output_dir
        self.output_file: TextIO = output_file
        self.downloader: Downloader = Downloader()
        self.content: str = ''
        self.dom: BeautifulSoup

    def run(self) -> None:
        logs.info(f"hello: {self.url}")
        self.content = self.download_content()
        self.dom = BeautifulSoup(self.content, 'html.parser')

        table_chapter = self.dom.find('table', id='chapters')
        anchors = table_chapter.find_all('a')
        urls: OrderedDict[str, bool] = OrderedDict()
        for a in anchors:
            href = a.attrs.get('href')
            final_url = urljoin(self.url, href)
            urls[final_url] = True
        
        import json
        result: list[str] = [str(k) for k in urls.keys()]
        json.dump(result, self.output_file, indent=3)

    def download_content(self) -> str:
        """
        Download html content of given `url_path` then cached in `.cached` folder of local file system
        :param url_path: url of html article
        :return: content of downloaded file
        """
        output_path = pathlib.Path(self.output_dir)
        cached_file_path = output_path.joinpath('.cached', f'{utils.get_hexdigest(self.url)}.html')
        logs.info(self.url, cached_file_path)

        if not cached_file_path.exists():
            # download file from url_path
            self.downloader.download_url(self.url, str(cached_file_path))

        with open(cached_file_path, 'rt', encoding='utf-8') as file_in:
            content = file_in.read()
        return content
