import unittest
from unittest.mock import patch
from colusa import utils, etr
from colusa.config import UrlEntry


class PluginRegistryTestCase(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        utils.scan('colusa.plugins')

    def test_plugins_load_without_error(self):
        # setUpClass would have raised if any plugin failed to import
        pass

    def test_all_registered_extractors_have_required_keys(self):
        for id, entry in etr.get_registered_extractors().items():
            self.assertIn('pattern', entry, f'Extractor "{id}" missing pattern')
            self.assertIn('cls', entry, f'Extractor "{id}" missing cls')

    def test_all_registered_transformers_have_required_keys(self):
        for id, entry in etr.get_registered_transformers().items():
            self.assertIn('pattern', entry, f'Transformer "{id}" missing pattern')
            self.assertIn('cls', entry, f'Transformer "{id}" missing cls')

    def test_known_extractors_are_registered(self):
        patterns = {v['pattern'] for v in etr.get_registered_extractors().values()}
        self.assertTrue(any('staffeng.com' in p for p in patterns))
        self.assertTrue(any('medium.com' in p for p in patterns))
        self.assertTrue(any('wikipedia.org' in p for p in patterns))

    def test_create_extractor_returns_correct_class_for_known_url(self):
        from bs4 import BeautifulSoup
        bs = BeautifulSoup('<html><body><div class="blog-post-content">x</div></body></html>', 'html.parser')
        extractor = etr.create_extractor(bs, 'https://staffeng.com/guides/overview', '/tmp')
        self.assertEqual(type(extractor).__name__, 'StaffEng')

    def test_create_extractor_falls_back_to_base_for_unknown_url(self):
        from bs4 import BeautifulSoup
        bs = BeautifulSoup('<html><body></body></html>', 'html.parser')
        extractor = etr.create_extractor(bs, 'https://unknown-site-xyz.com/page', '/tmp')
        self.assertIs(type(extractor), etr.Extractor)


class GenerateFailureReportingTestCase(unittest.TestCase):
    """Tests for collect-and-report behaviour when ContentNotFoundError occurs."""

    BASE_CONFIG = {
        "title": "Test Book",
        "author": "tester",
        "version": "v1.0",
        "homepage": "http://example.com",
        "output_dir": "tests-dist",
        "multi_part": False,
        "parts": [],
    }

    # HTML with no detectable content structure — triggers ContentNotFoundError
    EMPTY_HTML = '<html><body><p>no article here</p></body></html>'

    # HTML with a valid article element — extracted successfully
    VALID_HTML = '<html><head><title>Hello</title></head><body><article><p>content</p></article></body></html>'

    @patch('colusa.fetch.download_image')
    @patch('colusa.Colusa.download_content')
    def test_generate_exits_with_code_1_on_content_not_found(self, mock_dl, mock_img):
        """generate() raises SystemExit(1) when a URL yields no extractable content."""
        mock_dl.return_value = self.EMPTY_HTML
        mock_img.return_value = ''

        from colusa import Colusa
        config = {**self.BASE_CONFIG, "urls": ["https://unknown-site-xyz.com/no-content"]}
        runner = Colusa(config)
        with self.assertRaises(SystemExit) as ctx:
            runner.generate()
        self.assertEqual(ctx.exception.code, 1)

    @patch('colusa.fetch.download_image')
    @patch('colusa.Colusa.download_content')
    def test_generate_collects_all_failed_urls(self, mock_dl, mock_img):
        """All failed URLs are recorded, not just the first one."""
        mock_dl.return_value = self.EMPTY_HTML
        mock_img.return_value = ''

        from colusa import Colusa
        urls = [
            "https://unknown-site-xyz.com/page-one",
            "https://unknown-site-xyz.com/page-two",
        ]
        config = {**self.BASE_CONFIG, "urls": urls}
        runner = Colusa(config)
        with self.assertRaises(SystemExit):
            runner.generate()
        self.assertEqual(runner._failed_urls, urls)

    @patch('colusa.fetch.download_image')
    @patch('colusa.Colusa.download_content')
    def test_generate_succeeds_with_valid_content(self, mock_dl, mock_img):
        """generate() does not raise SystemExit when all URLs extract successfully."""
        mock_dl.return_value = self.VALID_HTML
        mock_img.return_value = ''

        from colusa import Colusa
        config = {**self.BASE_CONFIG, "urls": ["https://unknown-site-xyz.com/valid-page"]}
        runner = Colusa(config)
        # Should complete without raising SystemExit
        runner.generate()
        self.assertEqual(runner._failed_urls, [])
