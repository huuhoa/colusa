import json
import unittest
from pathlib import Path
from unittest.mock import patch

import yaml

from colusa import ConfigurationError
from colusa.colusa import Colusa
from colusa.utils import get_hexdigest


def _make_config(tmp_path: Path, extra: dict = None) -> Path:
    """Write a minimal single-part config and return its path."""
    data = {
        'title': 'Test Book',
        'author': 'Tester',
        'version': 'v1.0',
        'homepage': 'https://example.com',
        'output_dir': str(tmp_path),
        'urls': [],
    }
    if extra:
        data.update(extra)
    config = tmp_path / 'book.json'
    config.write_text(json.dumps(data, indent=4))
    return config


class AddUrlJsonTestCase(unittest.TestCase):

    def setUp(self):
        import tempfile
        self._tmp = tempfile.mkdtemp()
        self.tmp_path = Path(self._tmp)

    def test_add_plain_url_to_json(self):
        config = _make_config(self.tmp_path)
        Colusa.add_url(str(config), 'https://example.com/article')
        data = json.loads(config.read_text())
        self.assertEqual(data['urls'], ['https://example.com/article'])

    def test_add_url_with_metadata(self):
        config = _make_config(self.tmp_path)
        Colusa.add_url(str(config), 'https://example.com/article', title='My Post', author='Jane')
        data = json.loads(config.read_text())
        self.assertEqual(data['urls'][0], {
            'path': 'https://example.com/article',
            'title': 'My Post',
            'author': 'Jane',
        })

    def test_add_url_with_published_only(self):
        config = _make_config(self.tmp_path)
        Colusa.add_url(str(config), 'https://example.com/article', published='2025-01-01')
        data = json.loads(config.read_text())
        entry = data['urls'][0]
        self.assertIsInstance(entry, dict)
        self.assertEqual(entry['published'], '2025-01-01')
        self.assertNotIn('title', entry)
        self.assertNotIn('author', entry)

    def test_duplicate_url_is_skipped(self):
        config = _make_config(self.tmp_path, extra={'urls': ['https://example.com/article']})
        original = config.read_text()
        with patch('colusa.colusa.logs.warn') as mock_warn:
            Colusa.add_url(str(config), 'https://example.com/article')
        self.assertEqual(config.read_text(), original)
        mock_warn.assert_called_once()
        self.assertIn('already exists', mock_warn.call_args[0][0])

    def test_config_not_found(self):
        with self.assertRaises(ConfigurationError):
            Colusa.add_url(str(self.tmp_path / 'nonexistent.json'), 'https://example.com')

    def test_unsupported_extension(self):
        bad = self.tmp_path / 'config.txt'
        bad.write_text('{}')
        with self.assertRaises(ConfigurationError):
            Colusa.add_url(str(bad), 'https://example.com')


class AddUrlYamlTestCase(unittest.TestCase):

    def setUp(self):
        import tempfile
        self._tmp = tempfile.mkdtemp()
        self.tmp_path = Path(self._tmp)

    def test_add_url_to_yaml(self):
        config = self.tmp_path / 'book.yml'
        config.write_text(yaml.dump({
            'title': 'Test', 'author': 'Me', 'version': 'v1',
            'homepage': '', 'output_dir': str(self.tmp_path), 'urls': [],
        }))
        Colusa.add_url(str(config), 'https://example.com/article')
        data = yaml.safe_load(config.read_text())
        self.assertIn('https://example.com/article', data['urls'])


class AddUrlMultiPartTestCase(unittest.TestCase):

    def setUp(self):
        import tempfile
        self._tmp = tempfile.mkdtemp()
        self.tmp_path = Path(self._tmp)
        self.config = self.tmp_path / 'book.json'
        data = {
            'title': 'Multi Book', 'author': 'Me', 'version': 'v1',
            'homepage': '', 'output_dir': str(self.tmp_path),
            'multi_part': True,
            'urls': [],
            'parts': [
                {'title': 'Chapter 1', 'description': '', 'urls': []},
                {'title': 'Chapter 2', 'description': '', 'urls': []},
            ],
        }
        self.config.write_text(json.dumps(data, indent=4))

    def test_multipart_requires_part_flag(self):
        with self.assertRaises(ConfigurationError) as ctx:
            Colusa.add_url(str(self.config), 'https://example.com/article')
        self.assertIn('--part', str(ctx.exception))

    def test_multipart_part_not_found(self):
        with self.assertRaises(ConfigurationError) as ctx:
            Colusa.add_url(str(self.config), 'https://example.com/article', part='Chapter 99')
        self.assertIn('Part not found', str(ctx.exception))

    def test_multipart_adds_to_correct_part(self):
        Colusa.add_url(str(self.config), 'https://example.com/article', part='Chapter 2')
        data = json.loads(self.config.read_text())
        self.assertEqual(data['parts'][0]['urls'], [])
        self.assertEqual(data['parts'][1]['urls'], ['https://example.com/article'])

    def test_multipart_part_matching_is_case_insensitive(self):
        Colusa.add_url(str(self.config), 'https://example.com/article', part='chapter 1')
        data = json.loads(self.config.read_text())
        self.assertIn('https://example.com/article', data['parts'][0]['urls'])

    def test_multipart_duplicate_check_across_parts(self):
        Colusa.add_url(str(self.config), 'https://example.com/article', part='Chapter 1')
        original = self.config.read_text()
        with patch('colusa.colusa.logs.warn') as mock_warn:
            Colusa.add_url(str(self.config), 'https://example.com/article', part='Chapter 2')
        self.assertEqual(self.config.read_text(), original)
        mock_warn.assert_called_once()


class AddUrlFetchTitleTestCase(unittest.TestCase):

    def setUp(self):
        import tempfile
        self._tmp = tempfile.mkdtemp()
        self.tmp_path = Path(self._tmp)
        self.config = _make_config(self.tmp_path)

    def _write_cached(self, url: str, html: str) -> None:
        cached_dir = self.tmp_path / '.cached'
        cached_dir.mkdir(exist_ok=True)
        (cached_dir / f'{get_hexdigest(url)}.html').write_text(html, encoding='utf-8')

    def test_fetch_title_from_og_meta(self):
        url = 'https://example.com/article'
        self._write_cached(url, '<html><head>'
                                '<meta property="og:title" content="OG Title"/>'
                                '</head><body></body></html>')
        Colusa.add_url(str(self.config), url, fetch_title=True)
        data = json.loads(self.config.read_text())
        self.assertEqual(data['urls'][0]['title'], 'OG Title')

    def test_fetch_title_from_title_tag(self):
        url = 'https://example.com/article'
        self._write_cached(url, '<html><head><title>Page Title</title></head><body></body></html>')
        Colusa.add_url(str(self.config), url, fetch_title=True)
        data = json.loads(self.config.read_text())
        self.assertEqual(data['urls'][0]['title'], 'Page Title')

    def test_fetch_title_from_h1(self):
        url = 'https://example.com/article'
        self._write_cached(url, '<html><body><h1>H1 Title</h1></body></html>')
        Colusa.add_url(str(self.config), url, fetch_title=True)
        data = json.loads(self.config.read_text())
        self.assertEqual(data['urls'][0]['title'], 'H1 Title')

    def test_fetch_title_explicit_overrides_fetched(self):
        url = 'https://example.com/article'
        self._write_cached(url, '<html><head><title>Fetched Title</title></head><body></body></html>')
        Colusa.add_url(str(self.config), url, title='Explicit Title', fetch_title=True)
        data = json.loads(self.config.read_text())
        self.assertEqual(data['urls'][0]['title'], 'Explicit Title')

    def test_fetch_title_network_error_continues(self):
        url = 'https://example.com/article'
        with patch('colusa.fetch.Downloader.download_url', side_effect=Exception('network error')):
            with patch('colusa.colusa.logs.warn'):
                Colusa.add_url(str(self.config), url, fetch_title=True)
        data = json.loads(self.config.read_text())
        # Entry still added as a plain string (no title was fetched)
        self.assertEqual(data['urls'][0], url)
