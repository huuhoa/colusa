# -*- coding: utf-8 -*-
"""Top-level package for colusa.

Copyright (c) 2020-2021 Huu Hoa NGUYEN

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.
"""

from colusa import _version
__author__ = _version.__author__
__email__ = _version.__email__
__version__ = _version.__version__
__copyright__ = _version.__copyright__
__license__ = _version.__license__


import json
import os
import pathlib

import yaml
from bs4 import BeautifulSoup

from colusa import logs
from colusa.etr import ContentNotFoundError, Render, create_extractor, create_transformer


def create_book_maker(config: dict):
    return Render(config)


class ConfigurationError(Exception):
    def __init__(self, reason: str):
        self.reason = reason

    def __str__(self):
        return f'ConfigurationError: {self.reason}'


class Colusa(object):
    def __init__(self, configuration: dict):
        from colusa.utils import scan
        scan('colusa.plugins')
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
                "multi_part": False,
                "parts": [],
                "urls": []
            }
        p = pathlib.PurePath(file_path)
        if p.suffix == '.json':
            with open(file_path, 'w') as file_out:
                json.dump(template, file_out, indent=4)
                return
        if p.suffix == '.yml':
            with open(file_path, 'w') as file_in:
                yaml.safe_dump(template, file_in)
                return
        raise ConfigurationError(f'unknown configuration file format: {p.suffix}. '
                                 f'Configuration file format should be either .json or .yml')

    def download_content(self, url_path):
        from .utils import download_url, get_hexdigest, get_short_hexdigest

        output_path = pathlib.Path(self.output_dir)
        cached_file_path = output_path.joinpath('.cached', f'{get_hexdigest(url_path)}.html')
        p = pathlib.PurePath(url_path)
        logs.info(url_path, p.name, cached_file_path)

        if not cached_file_path.exists():
            # download file from url_path
            download_url(url_path, str(cached_file_path))

        with open(cached_file_path, 'rt', encoding='utf-8') as file_in:
            content = file_in.read()
        return content, f'{p.name}_{get_short_hexdigest(url_path)}'

    def ebook_generate_content(self, url_path):
        content, file_basename = self.download_content(url_path)
        bs = BeautifulSoup(content, 'html.parser')

        chapter_metadata = self.config.get('metadata', True)
        title_strip = self.config.get('title_prefix_trim', '')
        try:
            extractor = create_extractor(url_path, bs)
            extractor.cleanup()
            transformer = create_transformer(url_path, extractor.get_content(), self.output_dir)
            transformer.transform()
            self.book_maker.render_chapter(extractor, transformer, url_path, file_basename,
                                           metadata=chapter_metadata,
                                           title_strip=title_strip)
        except ContentNotFoundError as e:
            logs.error(e, url_path)
            # raise e

    def generate(self):
        os.makedirs(os.path.join(self.output_dir, ".cached"), exist_ok=True)
        os.makedirs(os.path.join(self.output_dir, "images"), exist_ok=True)
        self.book_maker.generate_makefile()

        multi_part = self.config.get('multi_part', False)
        if multi_part:
            self._generate_book_multi_part()
        else:
            self._generate_book_single_part()

        self.book_maker.ebook_generate_master_file()

    def _generate_book_single_part(self):
        paths = self.config.get('urls', [])
        if len(paths) == 0:
            raise ConfigurationError('urls field must contain at least one url')
        for url_path in paths:
            self.ebook_generate_content(url_path)

    def _generate_book_multi_part(self):
        parts = self.config.get('parts', [])
        if len(parts) == 0:
            raise ConfigurationError('parts field must contain at least one part object')
        for part in parts:
            self.book_maker.render_book_part(part['title'], part.get('description', ''))
            urls = part.get('urls', [])
            for url_path in urls:
                self.ebook_generate_content(url_path)


def read_configuration_file(file_path):
    p = pathlib.PurePath(file_path)
    if p.suffix == '.json':
        with open(file_path, 'r') as file_in:
            data = json.load(file_in)
            return data
    if p.suffix == '.yml':
        with open(file_path, 'r') as file_in:
            data = yaml.safe_load(file_in)
            return data
    raise ConfigurationError(f'unknown configuration file format: {p.suffix}. '
                             f'Configuration file format should be either .json or .yml')
