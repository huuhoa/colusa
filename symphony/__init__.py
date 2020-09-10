__author__ = "Huu Hoa NGUYEN (huuhoa@gmail.com)"
__version__ = "0.2.0"
__copyright__ = "Copyright (c) 2020 Huu Hoa NGUYEN"
# Use of this source code is governed by the MIT license.
__license__ = "MIT"


import argparse
import json
import os
import pathlib

from bs4 import BeautifulSoup

from symphony.etr import ContentNotFoundError, Render


def create_book_maker(config: dict):
    return Render(config)


class ConfigurationError(Exception):
    def __init__(self, reason: str):
        self.reason = reason

    def __str__(self):
        return f'ConfigurationError: {self.reason}'


class Symphony(object):
    def __init__(self, configuration: dict):
        self.config = configuration
        self.output_dir = configuration.get('output_dir', '.')
        self.book_maker = create_book_maker(configuration)

    @classmethod
    def generate_new_configuration(cls, file_path):
        template = {
                "title": "__fill the title__",
                "author": "__fill the author__",
                "version": "v1.0",
                "homepage": "__fill url to home page__",
                "output_dir": "__fill output dir__",
                "urls": [
                ]
            }
        with open(file_path, 'w') as file_out:
            json.dump(template, file_out, indent=4)

    def download_content(self, url_path):
        from .utils import download_url, get_hexdigest

        output_path = pathlib.Path(self.output_dir)
        cached_file_path = output_path.joinpath('.cached', f'{get_hexdigest(url_path)}.html')
        p = pathlib.PurePath(url_path)
        print(url_path, p.name, cached_file_path)

        if not cached_file_path.exists():
            # download file from url_path
            download_url(url_path, str(cached_file_path))

        with open(cached_file_path, 'rt', encoding='utf-8') as file_in:
            content = file_in.read()
        return content, p.name

    def ebook_generate_content(self, url_path):
        from .etr_factory import create_extractor, create_transformer

        content, file_basename = self.download_content(url_path)
        bs = BeautifulSoup(content, 'html.parser')

        try:
            extractor = create_extractor(url_path, bs)
            extractor.cleanup()
            transformer = create_transformer(url_path, extractor.get_content(), self.output_dir)
            transformer.transform()
            self.book_maker.render_chapter(extractor, transformer, url_path, file_basename)
        except ContentNotFoundError as e:
            print(e, url_path)
            # raise e

    def main(self):
        os.makedirs(os.path.join(self.output_dir, ".cached"), exist_ok=True)
        os.makedirs(os.path.join(self.output_dir, "images"), exist_ok=True)
        self.book_maker.generate_makefile()

        paths = self.config.get('urls', None)
        if paths is None:
            parts = self.config.get('parts', None)
            if parts is None:
                raise ConfigurationError('cannot find either urls or parts field')
            else:
                for part in parts:
                    self.book_maker.render_book_part(part['title'], part.get('description', ''))
                    urls = part.get('urls', [])
                    for url_path in urls:
                        self.ebook_generate_content(url_path)
        else:
            for url_path in paths:
                self.ebook_generate_content(url_path)

        self.book_maker.ebook_generate_master_file()


def read_configuration_file(file_path):
    with open(file_path, 'r') as file_in:
        data = json.load(file_in)
        return data


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--new', '-n', type=bool, default=False,
                        help='Generate new configuration file. '
                             'File name will be specified in the --input parameter')
    parser.add_argument('--input', '-i', type=str, help='Configuration file')
    args = parser.parse_args()
    if args.new:
        Symphony.generate_new_configuration(args.input)
        exit(0)

    configs = read_configuration_file(args.input)
    symp = Symphony(configs)
    symp.main()
