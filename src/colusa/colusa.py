from bs4 import BeautifulSoup
import pathlib
import json
import yaml
import os

from colusa import logs, etr, utils, fetch, ConfigurationError


class Colusa(object):
    """
    Implementation for initializing book configuration and generating book from configuration
    """
    def __init__(self, configuration: dict):
        from colusa.etr import populate_extractor_config, populate_transformer_config

        utils.scan('colusa.plugins')
        self.config = configuration
        self.output_dir = configuration.get('output_dir', '.')
        self.book_maker = etr.Render(configuration)
        self.downloader = fetch.Downloader(configuration.get('downloader', {}))
        populate_extractor_config(configuration.get('extractors', {}))
        populate_transformer_config(configuration.get('transformers', {}))

    @classmethod
    def generate_new_configuration(cls, file_path: str):
        """
        Generate initial content for book configuration, raise ConfigurationError if
        `file_path` is not end with supported format (json, yml)

        :param file_path: path of new configuration file, must end with either .json or .yml
        """
        template = {
            "title": "__fill the title__",
            "author": "__fill the author__",
            "version": "v1.0",
            "homepage": "__fill url to home page__",
            "output_dir": "__fill output dir__",
            "book_file_name": "index.asciidoc",
            "multi_part": False,
            "metadata": True,
            "make": {
                'html': '',
                'epub': '',
                'pdf': '',
            },
            'postprocessing': [],
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

    @classmethod
    def generate_book(cls, config_file_path):
        """
        Generate book from existing input configuration `config_file_path`,
        raise ConfigurationError if cannot parse configuration file

        :param config_file_path: Path to input configuration
        :return: None
        """
        configs = cls._read_configuration_file(config_file_path)
        with Colusa(configs) as s:
            s.generate()

    @classmethod
    def _read_configuration_file(cls, file_path: str) -> dict:
        """
        Read the book configuration file, raise ConfigurationError if `file_path` is unknown format

        :param file_path: path to known format configuration (json, yml)
        :return: dict for configurations
        """
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

    def download_content(self, url_path):
        """
        Download html content of given `url_path` then cached in `.cached` folder of local file system
        :param url_path: url of html article
        :return: content of downloaded file
        """
        output_path = pathlib.Path(self.output_dir)
        cached_file_path = output_path.joinpath('.cached', f'{utils.get_hexdigest(url_path)}.html')
        logs.info(url_path, cached_file_path)

        if not cached_file_path.exists():
            # download file from url_path
            self.downloader.download_url(url_path, str(cached_file_path))

        with open(cached_file_path, 'rt', encoding='utf-8') as file_in:
            content = file_in.read()
        return content

    @staticmethod
    def _get_saved_file_name(url_path: str) -> str:
        """
        calculates the name on local file system based on given article url.
        The calculation is based on ending name of url and url's short digest

        saved_file_name =  f'{pathlib.PurePath(url_path).name}_{get_short_hexdigest(url_path)}'

        Args:
            url_path (str): url

        Returns:
            str: calculated file name
        """
        p = pathlib.PurePath(url_path)
        return f'{p.name}_{utils.get_short_hexdigest(url_path)}'

    def __enter__(self):
        return self

    def __exit__(self, *args):
        self.close()
    
    def close(self):
        self.downloader.close()

    def ebook_generate_content(self, url_path):
        content = self.download_content(url_path)
        bs = BeautifulSoup(content, 'html.parser')

        chapter_metadata = self.config.get('metadata', True)
        title_strip = self.config.get('title_prefix_trim', '')
        try:
            extractor = etr.create_extractor(url_path, bs)
            extractor.cleanup()
            transformer = etr.create_transformer(url_path, extractor.get_content(), self.output_dir)
            transformer.transform()
            file_path = self.book_maker.render_chapter(extractor, transformer, url_path,
                                           self._get_saved_file_name(url_path),
                                           metadata=chapter_metadata,
                                           title_strip=title_strip)
            postprocessors = self.config.get('postprocessing', [])
            for pp in postprocessors:
                pp_name = pp.get('processor')
                pp_params = pp.get('params')
                pcls = etr.create_postprocessor(pp_name, file_path, pp_params)
                pcls.run()
        except etr.ContentNotFoundError as e:
            logs.error(e, url_path)
            # raise e

    def generate(self):
        os.makedirs(os.path.join(self.output_dir, ".cached"), exist_ok=True)
        os.makedirs(os.path.join(self.output_dir, "images"), exist_ok=True)
        self.book_maker.generate_makefile(self.config.get('make', {}))

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

    