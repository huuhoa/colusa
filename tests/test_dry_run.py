import io
import json
import unittest
from contextlib import redirect_stdout
from pathlib import Path
from unittest.mock import patch

from colusa import ConfigurationError
from colusa.colusa import Colusa


def _make_config(tmp_path: Path, extra: dict = None) -> Path:
    data = {
        'title': 'Test Book',
        'author': 'Tester',
        'version': 'v1.0',
        'homepage': 'https://example.com',
        'output_dir': str(tmp_path / 'output'),
        'urls': ['https://unknown-site-xyz.com/page'],
    }
    if extra:
        data.update(extra)
    config = tmp_path / 'book.json'
    config.write_text(json.dumps(data, indent=4))
    return config


def _dry_run_output(config_path: str) -> str:
    buf = io.StringIO()
    with redirect_stdout(buf):
        Colusa.dry_run_book(config_path)
    return buf.getvalue()


class DryRunHeaderTestCase(unittest.TestCase):

    def setUp(self):
        import tempfile
        self.tmp_path = Path(tempfile.mkdtemp())

    def test_dry_run_shows_header(self):
        config = _make_config(self.tmp_path)
        output = _dry_run_output(str(config))
        self.assertIn('[dry-run] Config:', output)
        self.assertIn('[dry-run] Output dir:', output)
        self.assertIn('[dry-run] Total URLs: 1', output)

    def test_dry_run_shows_url(self):
        config = _make_config(self.tmp_path)
        output = _dry_run_output(str(config))
        self.assertIn('https://unknown-site-xyz.com/page', output)


class DryRunDispatchTestCase(unittest.TestCase):

    def setUp(self):
        import tempfile
        self.tmp_path = Path(tempfile.mkdtemp())

    def test_dry_run_base_extractor_for_unknown_url(self):
        config = _make_config(self.tmp_path)
        output = _dry_run_output(str(config))
        self.assertIn('Extractor  : Extractor (base)', output)
        self.assertIn('Transformer: Transformer (base)', output)

    def test_dry_run_plugin_extractor_for_staffeng(self):
        config = _make_config(self.tmp_path, extra={
            'urls': ['https://staffeng.com/guides/overview']
        })
        output = _dry_run_output(str(config))
        self.assertIn('(plugin)', output)
        self.assertNotIn('(base)', output.split('Extractor')[1].split('\n')[0])

    def test_dry_run_dynamic_rule(self):
        config = _make_config(self.tmp_path, extra={
            'urls': ['https://mysite.example.com/post'],
            'site_rules': [{'pattern': '//mysite.example.com', 'content': 'article'}],
        })
        output = _dry_run_output(str(config))
        self.assertIn('DynamicExtractor', output)
        self.assertIn('rule: //mysite.example.com', output)

    def test_dry_run_local_asciidoc(self):
        adoc = self.tmp_path / 'notes.adoc'
        adoc.write_text('= My Notes\n\nContent.')
        config = _make_config(self.tmp_path, extra={'urls': [str(adoc)]})
        output = _dry_run_output(str(config))
        self.assertIn('local AsciiDoc (passthrough)', output)
        self.assertNotIn('Extractor', output.split(str(adoc))[1])

    def test_dry_run_local_html(self):
        html = self.tmp_path / 'article.html'
        html.write_text('<html><body><p>Hello</p></body></html>')
        config = _make_config(self.tmp_path, extra={'urls': [str(html)]})
        output = _dry_run_output(str(config))
        self.assertIn('local HTML', output)
        self.assertIn('Extractor', output)
        self.assertIn('Transformer', output)


class DryRunMultiPartTestCase(unittest.TestCase):

    def setUp(self):
        import tempfile
        self.tmp_path = Path(tempfile.mkdtemp())

    def test_dry_run_multipart_shows_part(self):
        config = _make_config(self.tmp_path, extra={
            'multi_part': True,
            'urls': [],
            'parts': [
                {'title': 'Chapter 1', 'description': '', 'urls': ['https://example.com/a']},
                {'title': 'Chapter 2', 'description': '', 'urls': ['https://example.com/b']},
            ],
        })
        output = _dry_run_output(str(config))
        self.assertIn('Part       : Chapter 1', output)
        self.assertIn('Part       : Chapter 2', output)
        self.assertIn('[dry-run] Total URLs: 2', output)


class DryRunMetadataTestCase(unittest.TestCase):

    def setUp(self):
        import tempfile
        self.tmp_path = Path(tempfile.mkdtemp())

    def test_dry_run_metadata_overrides_shown(self):
        config = _make_config(self.tmp_path, extra={
            'urls': [{'path': 'https://example.com/post', 'title': 'Custom Title', 'author': 'Jane'}]
        })
        output = _dry_run_output(str(config))
        self.assertIn('Overrides  :', output)
        self.assertIn('title="Custom Title"', output)
        self.assertIn('author="Jane"', output)

    def test_dry_run_no_overrides_line_when_no_metadata(self):
        config = _make_config(self.tmp_path)
        output = _dry_run_output(str(config))
        self.assertNotIn('Overrides', output)


class DryRunSideEffectsTestCase(unittest.TestCase):

    def setUp(self):
        import tempfile
        self.tmp_path = Path(tempfile.mkdtemp())

    def test_dry_run_no_files_written(self):
        output_dir = self.tmp_path / 'output'
        config = _make_config(self.tmp_path, extra={'output_dir': str(output_dir)})
        _dry_run_output(str(config))
        self.assertFalse(output_dir.exists())

    def test_dry_run_download_never_called(self):
        config = _make_config(self.tmp_path)
        with patch('colusa.fetch.Downloader.download_url') as mock_dl:
            _dry_run_output(str(config))
        mock_dl.assert_not_called()


class DryRunExitCodeTestCase(unittest.TestCase):

    def setUp(self):
        import tempfile
        self.tmp_path = Path(tempfile.mkdtemp())

    def test_dry_run_exits_1_on_missing_config(self):
        with self.assertRaises((ConfigurationError, FileNotFoundError, SystemExit)):
            Colusa.dry_run_book(str(self.tmp_path / 'nonexistent.json'))
