from typing import Any, Optional, Union
from bs4 import BeautifulSoup
import pathlib
import json
import yaml
import os

from colusa import logs, etr, utils, fetch, ConfigurationError
from colusa.config import BookConfig, MakeConfig, UrlEntry, SiteRule, _parse_site_rule


_TOOL_MAP: dict[str, str] = {
    'html': 'asciidoctor',
    'epub': 'asciidoctor-epub3',
    'pdf':  'asciidoctor-pdf',
}

_TOOL_INSTALL_URL: dict[str, str] = {
    'html': 'https://asciidoctor.org',
    'epub': 'https://asciidoctor.org/docs/asciidoctor-epub3/',
    'pdf':  'https://asciidoctor.org/docs/asciidoctor-pdf/',
}


def _resolve_extractor(url_path: str) -> tuple[str, str]:
    """Return (class_name, kind) for the extractor that would handle url_path.
    kind is 'plugin' or 'base'.
    """
    import re
    for _, ext in etr.get_registered_extractors().items():
        if re.search(ext['pattern'], url_path):
            return ext['cls'].__name__, 'plugin'
    return 'Extractor', 'base'


def _resolve_transformer(url_path: str) -> tuple[str, str]:
    """Return (class_name, kind) for the transformer that would handle url_path.
    kind is 'plugin' or 'base'.
    """
    import re
    for _, trf in etr.get_registered_transformers().items():
        if re.search(trf['pattern'], url_path):
            return trf['cls'].__name__, 'plugin'
    return 'Transformer', 'base'


def _load_rules_file(path: str) -> list[SiteRule]:
    p = pathlib.PurePath(path)
    with open(path, 'r', encoding='utf-8') as f:
        data = yaml.safe_load(f) if p.suffix == '.yml' else json.load(f)
    return [_parse_site_rule(r) for r in (data or [])]


class Colusa:
    """
    Implementation for initializing book configuration and generating book from configuration
    """
    def __init__(self, configuration: Union[dict[str, Any], BookConfig], config_file_dir: str = '') -> None:
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
        self.site_rules: list[SiteRule] = self._load_site_rules(config_file_dir)
        self._failed_urls: list[str] = []

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

    def _load_site_rules(self, config_file_dir: str) -> list[SiteRule]:
        rules = list(self.config.site_rules)
        rules_file = self.config.site_rules_file
        if rules_file:
            if not os.path.isabs(rules_file) and config_file_dir:
                rules_file = os.path.join(config_file_dir, rules_file)
            rules.extend(_load_rules_file(rules_file))
        return rules

    def _match_site_rule(self, url_path: str) -> Optional[SiteRule]:
        import re
        for rule in self.site_rules:
            if re.search(rule.pattern, url_path):
                return rule
        return None

    @classmethod
    def generate_book(cls, config_file_path: str) -> None:
        """
        Generate book from existing input configuration `config_file_path`,
        raise ConfigurationError if cannot parse configuration file

        :param config_file_path: Path to input configuration
        :return: None
        """
        configs = cls._read_configuration_file(config_file_path)
        config_dir = str(pathlib.Path(config_file_path).parent)
        with Colusa(configs, config_file_dir=config_dir) as s:
            s.generate()

    @classmethod
    def dry_run_book(cls, config_file_path: str) -> None:
        """Print dispatch plan without downloading or writing any files."""
        configs = cls._read_configuration_file(config_file_path)
        config_dir = str(pathlib.Path(config_file_path).parent)
        with Colusa(configs, config_file_dir=config_dir) as s:
            s.dry_run(config_file_path)

    @classmethod
    def build_book(cls, config_file_path: str, formats: Optional[list[str]] = None) -> None:
        """Compile an already-generated book using asciidoctor tools.

        Args:
            config_file_path: Path to the book config file.
            formats: List of formats to build ('html', 'epub', 'pdf').
                     Defaults to all three if None.
        """
        configs = cls._read_configuration_file(config_file_path)
        config_dir = str(pathlib.Path(config_file_path).parent)
        with Colusa(configs, config_file_dir=config_dir) as s:
            s._build_formats(formats or ['html', 'epub', 'pdf'])

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

    @staticmethod
    def _is_local_path(path: str) -> bool:
        return not path.startswith(('http://', 'https://'))

    def download_content(self, url_entry: UrlEntry) -> str:
        """
        Return html content for the given entry.
        For local paths, reads the file directly.
        For remote URLs, downloads and caches as before.
        :param url_entry: UrlEntry with path and optional metadata
        :return: content of the file
        """
        url_path = url_entry.path

        if self._is_local_path(url_path):
            import chardet
            with open(url_path, 'rb') as f:
                result = chardet.detect(f.read())
                encoding = result['encoding']
            with open(url_path, 'rt', encoding=encoding) as file_in:
                return file_in.read()

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

    def _process_local_asciidoc(self, url_entry: UrlEntry) -> None:
        """Copy a local .adoc file into the output dir and register it in the book."""
        import shutil
        src_path = pathlib.Path(url_entry.path)
        file_name = self._get_saved_file_name(url_entry.path) + '.asciidoc'
        dest_path = pathlib.Path(self.output_dir) / file_name
        shutil.copy2(src_path, dest_path)

        if url_entry.title:
            title = url_entry.title
        else:
            # Try to parse from first `= ...` line
            title = src_path.stem
            try:
                with open(src_path, 'r', encoding='utf-8') as f:
                    for line in f:
                        line = line.strip()
                        if line.startswith('= '):
                            title = line[2:].strip()
                            break
            except (OSError, UnicodeDecodeError) as e:
                logs.warn(f'could not read title from {src_path}: {e}')

        self.book_maker.render_asciidoc_passthrough(file_name, title)

    def ebook_generate_content(self, url_entry: UrlEntry) -> None:
        url_path = url_entry.path

        # Route local .adoc files directly — no HTML extraction needed
        if self._is_local_path(url_path) and pathlib.PurePath(url_path).suffix in ('.adoc', '.asciidoc'):
            self._process_local_asciidoc(url_entry)
            return

        content = self.download_content(url_entry)
        bs = BeautifulSoup(content, 'html.parser')

        chapter_metadata = self.config.metadata
        title_strip = self.config.title_prefix_trim
        try:
            rule = self._match_site_rule(url_path)
            if rule:
                extractor = etr.DynamicExtractor(bs, rule)
                extractor.url_path = url_path
                extractor.cached_path = os.path.join(self.output_dir, '.cached')
            else:
                extractor = etr.create_extractor(bs, url_path, os.path.join(self.output_dir, '.cached'))
            extractor.parse()
            extractor.cleanup()
            # Apply per-entry metadata overrides
            if url_entry.title:
                extractor.title = url_entry.title
            if url_entry.author:
                extractor.author = url_entry.author
            if url_entry.published:
                extractor.published = url_entry.published
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
            self._failed_urls.append(url_path)

    def generate(self) -> None:
        os.makedirs(os.path.join(self.output_dir, ".cached"), exist_ok=True)
        os.makedirs(os.path.join(self.output_dir, "images"), exist_ok=True)
        self.book_maker.generate_makefile(self.config.make)

        if self.config.multi_part:
            self._generate_book_multi_part()
        else:
            self._generate_book_single_part()

        self.book_maker.ebook_generate_master_file()

        if self._failed_urls:
            print(f'\n[colusa] WARNING: content extraction failed for {len(self._failed_urls)} URL(s):')
            for url in self._failed_urls:
                print(f'  - {url}')
            raise SystemExit(1)

    def _build_formats(self, formats: list[str]) -> None:
        """Invoke asciidoctor tools for each requested format."""
        import shutil
        import subprocess

        make = self.config.make
        extra_params: dict[str, str] = {
            'html': make.html,
            'epub': make.epub,
            'pdf':  make.pdf,
        }
        book_file = self.config.book_file_name
        failed: list[str] = []

        for fmt in formats:
            tool = _TOOL_MAP[fmt]
            if not shutil.which(tool):
                logs.error(
                    f'{tool} not found on PATH.\n'
                    f'        Install: {_TOOL_INSTALL_URL[fmt]}'
                )
                failed.append(fmt)
                continue

            cmd = self._build_command(fmt, book_file, extra_params[fmt])
            print(f'[build] Building {fmt}...')
            result = subprocess.run(cmd, cwd=self.output_dir)
            if result.returncode != 0:
                logs.error(f'Build failed for format: {fmt}')
                failed.append(fmt)
            else:
                stem = pathlib.PurePath(book_file).stem
                ext_map = {'html': '.html', 'epub': '.epub', 'pdf': '.pdf'}
                out_file = pathlib.Path(self.output_dir) / 'output' / f'{stem}{ext_map[fmt]}'
                print(f'[build] {fmt} → {out_file}  ✓')

        if failed:
            raise SystemExit(1)

    @staticmethod
    def _build_command(fmt: str, book_file: str, extra_params: str) -> list[str]:
        """Build the subprocess argument list for an asciidoctor invocation."""
        cmd = [_TOOL_MAP[fmt], book_file, '-d', 'book', '-D', 'output']
        if fmt == 'html':
            cmd += ['-b', 'html5']
        if extra_params:
            cmd += extra_params.split()
        return cmd

    def dry_run(self, config_file_path: str = '') -> None:
        """Print a per-URL dispatch summary. No I/O side-effects."""
        all_entries: list[tuple[UrlEntry, Optional[str]]] = []
        if self.config.multi_part:
            for part in self.config.parts:
                for entry in part.urls:
                    all_entries.append((entry, part.title))
        else:
            for entry in self.config.urls:
                all_entries.append((entry, None))

        print(f'[dry-run] Config: {config_file_path}')
        print(f'[dry-run] Output dir: {self.config.output_dir}')
        print(f'[dry-run] Total URLs: {len(all_entries)}')

        for i, (entry, part_title) in enumerate(all_entries, 1):
            url_path = entry.path
            print(f'\n[{i}/{len(all_entries)}] {url_path}')

            if part_title:
                print(f'      Part       : {part_title}')

            if self._is_local_path(url_path):
                suffix = pathlib.PurePath(url_path).suffix.lower()
                if suffix in ('.adoc', '.asciidoc'):
                    print(f'      Type       : local AsciiDoc (passthrough)')
                else:
                    print(f'      Type       : local HTML')
                    ext_name, ext_kind = _resolve_extractor(url_path)
                    trf_name, trf_kind = _resolve_transformer(url_path)
                    print(f'      Extractor  : {ext_name} ({ext_kind})')
                    print(f'      Transformer: {trf_name} ({trf_kind})')
            else:
                rule = self._match_site_rule(url_path)
                if rule:
                    print(f'      Extractor  : DynamicExtractor (rule: {rule.pattern})')
                    print(f'      Transformer: Transformer (base)')
                else:
                    ext_name, ext_kind = _resolve_extractor(url_path)
                    trf_name, trf_kind = _resolve_transformer(url_path)
                    print(f'      Extractor  : {ext_name} ({ext_kind})')
                    print(f'      Transformer: {trf_name} ({trf_kind})')

            overrides = {k: v for k, v in [
                ('title', entry.title), ('author', entry.author), ('published', entry.published)
            ] if v}
            if overrides:
                override_str = ', '.join(f'{k}="{v}"' for k, v in overrides.items())
                print(f'      Overrides  : {override_str}')

    def _generate_book_single_part(self) -> None:
        entries = self.config.urls
        if len(entries) == 0:
            raise ConfigurationError('urls field must contain at least one url')
        for entry in entries:
            self.ebook_generate_content(entry)

    def _generate_book_multi_part(self) -> None:
        parts = self.config.parts
        if len(parts) == 0:
            raise ConfigurationError('parts field must contain at least one part object')
        for part in parts:
            self.book_maker.render_book_part(part.title, part.description)
            for entry in part.urls:
                self.ebook_generate_content(entry)

    @staticmethod
    def add_url(
        config_path: str,
        url: str,
        title: Optional[str] = None,
        author: Optional[str] = None,
        published: Optional[str] = None,
        part: Optional[str] = None,
        fetch_title: bool = False,
    ) -> None:
        """Append a URL to an existing config file.

        Args:
            config_path: Path to an existing JSON or YAML config file.
            url: URL or local file path to add.
            title: Optional title override.
            author: Optional author override.
            published: Optional published date override.
            part: For multi-part books, the title of the part to add the URL to.
            fetch_title: If True, download the page and auto-extract the title.
        """
        path = pathlib.Path(config_path)
        if not path.exists():
            raise ConfigurationError(f'Config file not found: {config_path}')

        ext = path.suffix.lower()
        if ext == '.json':
            data = json.loads(path.read_text(encoding='utf-8'))
        elif ext in ('.yml', '.yaml'):
            data = yaml.safe_load(path.read_text(encoding='utf-8'))
        else:
            raise ConfigurationError(
                f'Unsupported config format: {ext}. Use .json, .yml, or .yaml'
            )

        # Duplicate check across all urls and parts[].urls
        existing: set[str] = set()
        for entry in data.get('urls', []):
            existing.add(entry if isinstance(entry, str) else entry.get('path', ''))
        for p in data.get('parts', []):
            for entry in p.get('urls', []):
                existing.add(entry if isinstance(entry, str) else entry.get('path', ''))

        if url in existing:
            logs.warn(f'URL already exists in config: {url}')
            return

        # Optional: fetch title from the live page
        if fetch_title:
            try:
                import tempfile
                from bs4 import BeautifulSoup as _BS
                output_dir = data.get('output_dir') or tempfile.mkdtemp()
                downloader = fetch.Downloader()
                cached = (
                    pathlib.Path(output_dir) / '.cached'
                    / f'{utils.get_hexdigest(url)}.html'
                )
                if not cached.exists():
                    downloader.download_url(url, str(cached))
                html = cached.read_text(encoding='utf-8', errors='replace')
                soup = _BS(html, 'html.parser')
                fetched_title = None
                og = soup.find('meta', property='og:title')
                if og and og.get('content'):
                    fetched_title = og['content'].strip()
                elif soup.title and soup.title.string:
                    fetched_title = soup.title.string.strip()
                elif soup.find('h1'):
                    fetched_title = soup.find('h1').get_text(strip=True)
                if fetched_title:
                    logs.info(f'Fetched title: "{fetched_title}"')
                    title = title or fetched_title  # explicit --title takes precedence
            except Exception as e:
                logs.warn(f'Could not fetch title for {url}: {e}')

        # Build the new entry — plain string when no metadata, dict otherwise
        if title or author or published:
            new_entry: Any = {'path': url}
            if title:
                new_entry['title'] = title
            if author:
                new_entry['author'] = author
            if published:
                new_entry['published'] = published
        else:
            new_entry = url

        # Append to the correct list
        if not data.get('multi_part'):
            data.setdefault('urls', []).append(new_entry)
            logs.info(f'Added: {url}')
        else:
            parts = data.get('parts', [])
            if not part:
                part_titles = ', '.join(f'"{p["title"]}"' for p in parts)
                raise ConfigurationError(
                    f'This is a multi-part book. Use --part <title> to specify a part. '
                    f'Available parts: {part_titles}'
                )
            matched = next(
                (p for p in parts if p.get('title', '').lower() == part.lower()), None
            )
            if matched is None:
                part_titles = ', '.join(f'"{p["title"]}"' for p in parts)
                raise ConfigurationError(
                    f'Part not found: "{part}". Available parts: {part_titles}'
                )
            matched.setdefault('urls', []).append(new_entry)
            logs.info(f'Added to part "{matched["title"]}": {url}')

        # Write back preserving the original format
        with path.open('w', encoding='utf-8') as f:
            if ext == '.json':
                json.dump(data, f, indent=4, ensure_ascii=False)
                f.write('\n')
            else:
                yaml.dump(data, f, default_flow_style=False, allow_unicode=True)
