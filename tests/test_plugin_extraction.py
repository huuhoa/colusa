import unittest
from bs4 import BeautifulSoup

from colusa import utils, etr


def _bs(html: str) -> BeautifulSoup:
    return BeautifulSoup(html, 'html.parser')


class StaffEngExtractionTestCase(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        utils.scan('colusa.plugins')

    def _extractor(self, html: str) -> etr.Extractor:
        return etr.create_extractor(_bs(html), 'https://staffeng.com/guides/x', '/tmp')

    def test_dispatches_to_staffeng_plugin(self):
        html = '<html><body><div class="blog-post-content"><p>x</p></div></body></html>'
        self.assertEqual(type(self._extractor(html)).__name__, 'StaffEng')

    def test_finds_blog_post_content_div(self):
        html = '<html><body><div class="blog-post-content"><p>hello</p></div></body></html>'
        content = self._extractor(html)._find_main_content()
        self.assertIsNotNone(content)
        self.assertIn('blog-post-content', content.get('class', []))

    def test_returns_none_when_content_div_absent(self):
        html = '<html><body><article><p>no matching div</p></article></body></html>'
        content = self._extractor(html)._find_main_content()
        self.assertIsNone(content)


class MediumExtractionTestCase(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        utils.scan('colusa.plugins')

    def _extractor(self, html: str) -> etr.Extractor:
        return etr.create_extractor(_bs(html), 'https://medium.com/@user/post', '/tmp')

    def test_dispatches_to_medium_plugin(self):
        html = '<html><body><article><p>body</p></article></body></html>'
        self.assertEqual(type(self._extractor(html)).__name__, 'MediumExtractor')

    def test_finds_article_tag(self):
        html = '<html><body><article><p>body</p></article></body></html>'
        content = self._extractor(html)._find_main_content()
        self.assertIsNotNone(content)
        self.assertEqual(content.name, 'article')

    def test_parses_title_from_h1_inside_article(self):
        html = '<html><body><article><h1>My Title</h1><p>body</p></article></body></html>'
        extractor = self._extractor(html)
        extractor.main_content = extractor._find_main_content()
        self.assertEqual(extractor._parse_title(), 'My Title')

    def test_parses_title_from_og_meta_when_no_h1(self):
        html = ('<html><head><meta property="og:title" content="OG Title"/></head>'
                '<body><article><p>body</p></article></body></html>')
        extractor = self._extractor(html)
        extractor.main_content = extractor._find_main_content()
        self.assertEqual(extractor._parse_title(), 'OG Title')

    def test_returns_none_when_no_article_tag(self):
        html = '<html><body><div><p>no article tag</p></div></body></html>'
        content = self._extractor(html)._find_main_content()
        self.assertIsNone(content)


class WikipediaExtractionTestCase(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        utils.scan('colusa.plugins')

    def _extractor(self, html: str) -> etr.Extractor:
        return etr.create_extractor(_bs(html), 'https://en.wikipedia.org/wiki/Test', '/tmp')

    def test_dispatches_to_wikipedia_plugin(self):
        html = '<html><body><div id="bodyContent"><p>x</p></div></body></html>'
        self.assertEqual(type(self._extractor(html)).__name__, 'WikipediaExtractor')

    def test_finds_body_content_div(self):
        html = '<html><body><div id="bodyContent"><p>wiki content</p></div></body></html>'
        content = self._extractor(html)._find_main_content()
        self.assertIsNotNone(content)
        self.assertEqual(content.get('id'), 'bodyContent')

    def test_parses_title_from_first_heading(self):
        html = ('<html><body><h1 id="firstHeading">Test Article</h1>'
                '<div id="bodyContent"><p>text</p></div></body></html>')
        self.assertEqual(self._extractor(html)._parse_title(), 'Test Article')

    def test_returns_none_when_no_body_content_div(self):
        html = '<html><body><p>no bodyContent div here</p></body></html>'
        content = self._extractor(html)._find_main_content()
        self.assertIsNone(content)
