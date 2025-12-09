from typing import Any, Optional, Union
from bs4 import BeautifulSoup
import pathlib
import json
import yaml
import os

from colusa import logs, etr, utils, fetch, ConfigurationError
from colusa.config import BookConfig, MakeConfig


class Colusa:
    """
    Implementation for initializing book configuration and generating book from configuration
    """
    def __init__(self, configuration: Union[dict[str, Any], BookConfig]) -> None:
        from colusa.etr import populate_extractor_config, populate_transformer_config

        utils.scan('colusa.plugins')
        
        # Support both dict and BookConfig for backward compatibility
        if isinstance(configuration, BookConfig):
            self.config = configuration
        else:
            self.config = BookConfig.from_dict(configuration)
        
        self.output_dir = self.config.output_dir
        self.book_maker = etr.Render(self.config)
        self.downloader = fetch.Downloader(self.config.downloader)
        populate_extractor_config(self.config.extractors)
        populate_transformer_config(self.config.transformers)

    @classmethod
    def generate_new_configuration(cls, file_path: str) -> None:
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
    def generate_book(cls, config_file_path: str) -> None:
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
    def _read_configuration_file(cls, file_path: str) -> BookConfig:
        """
        Read the book configuration file, raise ConfigurationError if `file_path` is unknown format

        :param file_path: path to known format configuration (json, yml)
        :return: BookConfig instance
        """
        p = pathlib.PurePath(file_path)
        if p.suffix == '.json':
            with open(file_path, 'r') as file_in:
                data = json.load(file_in)
                return BookConfig.from_dict(data)
        if p.suffix == '.yml':
            with open(file_path, 'r') as file_in:
                data = yaml.safe_load(file_in)
                return BookConfig.from_dict(data)
        raise ConfigurationError(f'unknown configuration file format: {p.suffix}. '
                                 f'Configuration file format should be either .json or .yml')

    def download_content(self, url_path: str) -> str:
        """
        Download html content of given `url_path` then cached in `.cached` folder of local file system
        :param url_path: url of html article
        :return: content of downloaded file
        """

        import chardet

        output_path = pathlib.Path(self.output_dir)
        cached_file_path = output_path.joinpath('.cached', f'{utils.get_hexdigest(url_path)}.html')
        logs.info(url_path, cached_file_path)

        if not cached_file_path.exists():
            # download file from url_path
            self.downloader.download_url(url_path, str(cached_file_path))

        with open(cached_file_path, 'rb') as f:
            result = chardet.detect(f.read())
            encoding = result['encoding']
        with open(cached_file_path, 'rt', encoding=encoding) as file_in:
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

    def __enter__(self) -> 'Colusa':
        return self

    def __exit__(self, *args: Any) -> None:
        self.close()
    
    def close(self) -> None:
        self.downloader.close()

    def ebook_generate_content(self, url_path: str) -> None:
        content = self.download_content(url_path)
        bs = BeautifulSoup(content, 'html.parser')

        chapter_metadata = self.config.metadata
        title_strip = self.config.title_prefix_trim
        try:
            extractor = etr.create_extractor(url_path, bs)
            extractor.cleanup()
            transformer = etr.create_transformer(url_path, extractor.get_content(), self.output_dir)
            transformer.transform()
            file_path = self.book_maker.render_chapter(extractor, transformer, url_path,
                                           self._get_saved_file_name(url_path),
                                           metadata=chapter_metadata,
                                           title_strip=title_strip)
            for pp in self.config.postprocessing:
                pp_name = pp.processor
                pp_params = pp.params
                pcls = etr.create_postprocessor(pp_name, file_path, pp_params)
                pcls.run()
        except etr.ContentNotFoundError as e:
            logs.error(e, url_path)
            # raise e

    def generate(self) -> None:
        os.makedirs(os.path.join(self.output_dir, ".cached"), exist_ok=True)
        os.makedirs(os.path.join(self.output_dir, "images"), exist_ok=True)
        self.book_maker.generate_makefile(self.config.make)

        if self.config.multi_part:
            self._generate_book_multi_part()
        else:
            self._generate_book_single_part()

        self.book_maker.ebook_generate_master_file()

    def _generate_book_single_part(self) -> None:
        paths = self.config.urls
        if len(paths) == 0:
            raise ConfigurationError('urls field must contain at least one url')
        for url_path in paths:
            self.ebook_generate_content(url_path)

    def _generate_book_multi_part(self) -> None:
        parts = self.config.parts
        if len(parts) == 0:
            raise ConfigurationError('parts field must contain at least one part object')
        for part in parts:
            self.book_maker.render_book_part(part.title, part.description)
            for url_path in part.urls:
                self.ebook_generate_content(url_path)
