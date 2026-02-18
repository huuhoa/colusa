import json
import os
import tempfile
import unittest

import yaml
from bs4 import BeautifulSoup

from colusa.config import BookConfig, SiteRule, _parse_site_rule
from colusa.etr import DynamicExtractor
from colusa import Colusa


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def make_bs(html: str) -> BeautifulSoup:
    return BeautifulSoup(html, 'html.parser')


def make_rule(**kwargs) -> SiteRule:
    return SiteRule(pattern=kwargs.pop('pattern', '//example.com'), **kwargs)


# ---------------------------------------------------------------------------
# SiteRule dataclass & _parse_site_rule
# ---------------------------------------------------------------------------

class SiteRuleParsingTestCase(unittest.TestCase):

    def test_parse_minimal(self):
        rule = _parse_site_rule({'pattern': '//example.com'})
        self.assertEqual(rule.pattern, '//example.com')
        self.assertIsNone(rule.content)
        self.assertIsNone(rule.title)
        self.assertIsNone(rule.author)
        self.assertIsNone(rule.published)
        self.assertEqual(rule.cleanup, [])

    def test_parse_full(self):
        rule = _parse_site_rule({
            'pattern': '//example.com',
            'content': 'article.body',
            'title': 'h1.title',
            'author': '.byline',
            'published': 'time.date',
            'cleanup': ['div.ads', 'nav.sidebar'],
        })
        self.assertEqual(rule.content, 'article.body')
        self.assertEqual(rule.title, 'h1.title')
        self.assertEqual(rule.author, '.byline')
        self.assertEqual(rule.published, 'time.date')
        self.assertEqual(rule.cleanup, ['div.ads', 'nav.sidebar'])

    def test_parse_missing_optional_fields_default_to_none(self):
        rule = _parse_site_rule({'pattern': '//x.com', 'content': 'main'})
        self.assertIsNone(rule.title)
        self.assertIsNone(rule.author)
        self.assertIsNone(rule.published)
        self.assertEqual(rule.cleanup, [])


class BookConfigSiteRulesTestCase(unittest.TestCase):

    def _base_config(self, **extra):
        cfg = {
            'title': 'T', 'author': 'A', 'version': 'v1',
            'homepage': 'http://x', 'output_dir': 'out',
        }
        cfg.update(extra)
        return cfg

    def test_no_site_rules_defaults_to_empty(self):
        config = BookConfig.from_dict(self._base_config())
        self.assertEqual(config.site_rules, [])
        self.assertEqual(config.site_rules_file, '')

    def test_site_rules_parsed(self):
        config = BookConfig.from_dict(self._base_config(
            site_rules=[{'pattern': '//example.com', 'content': 'article'}]
        ))
        self.assertEqual(len(config.site_rules), 1)
        self.assertEqual(config.site_rules[0].pattern, '//example.com')
        self.assertEqual(config.site_rules[0].content, 'article')

    def test_site_rules_file_parsed(self):
        config = BookConfig.from_dict(self._base_config(site_rules_file='./rules.yml'))
        self.assertEqual(config.site_rules_file, './rules.yml')


# ---------------------------------------------------------------------------
# DynamicExtractor
# ---------------------------------------------------------------------------

_ARTICLE_HTML = """
<html>
<head>
  <title>Page Title</title>
  <meta property="og:title" content="OG Title"/>
  <meta name="author" content="Meta Author"/>
</head>
<body>
  <header>Site Header</header>
  <div class="ads">Ad content</div>
  <article class="post-body">
    <h1 class="article-title">Real Title</h1>
    <span class="byline">Jane Doe</span>
    <time class="publish-date">2024-01-15</time>
    <p>Article body text.</p>
    <nav class="sidebar">Navigation junk</nav>
  </article>
</body>
</html>
"""


class DynamicExtractorContentTestCase(unittest.TestCase):

    def _extractor(self, html=_ARTICLE_HTML, **rule_kwargs):
        bs = make_bs(html)
        rule = make_rule(**rule_kwargs)
        ext = DynamicExtractor(bs, rule)
        ext.url_path = 'https://example.com/article'
        ext.cached_path = '/tmp'
        return ext

    # --- content selector ---

    def test_content_selector_matches(self):
        ext = self._extractor(content='article.post-body')
        ext.parse()
        self.assertIsNotNone(ext.main_content)
        self.assertIn('Article body text.', ext.main_content.get_text())

    def test_content_selector_no_match_falls_back_to_builtin(self):
        """When the CSS selector finds nothing the base extractor should take over."""
        ext = self._extractor(content='section.nonexistent')
        # Base extractor will find <article> tag
        ext.parse()
        self.assertIsNotNone(ext.main_content)

    def test_content_selector_absent_uses_builtin(self):
        """No content selector at all → base extractor logic."""
        ext = self._extractor()
        ext.parse()
        self.assertIsNotNone(ext.main_content)

    # --- title selector ---

    def test_title_selector_matches(self):
        ext = self._extractor(content='article.post-body', title='h1.article-title')
        ext.parse()
        self.assertEqual(ext.title, 'Real Title')

    def test_title_selector_no_match_falls_back(self):
        ext = self._extractor(content='article.post-body', title='h2.missing')
        ext.parse()
        # Falls back to og:title meta
        self.assertEqual(ext.title, 'OG Title')

    def test_title_selector_absent_falls_back(self):
        ext = self._extractor(content='article.post-body')
        ext.parse()
        self.assertEqual(ext.title, 'OG Title')

    # --- author selector ---

    def test_author_selector_matches(self):
        ext = self._extractor(content='article.post-body', author='.byline')
        ext.parse()
        self.assertEqual(ext.author, 'Jane Doe')

    def test_author_selector_no_match_falls_back(self):
        ext = self._extractor(content='article.post-body', author='.nobody')
        ext.parse()
        # Falls back to <meta name="author">
        self.assertEqual(ext.author, 'Meta Author')

    def test_author_selector_absent_falls_back(self):
        ext = self._extractor(content='article.post-body')
        ext.parse()
        self.assertEqual(ext.author, 'Meta Author')

    # --- published selector ---

    def test_published_selector_matches(self):
        ext = self._extractor(content='article.post-body', published='time.publish-date')
        ext.parse()
        self.assertEqual(ext.published, '2024-01-15')

    def test_published_selector_no_match_falls_back(self):
        ext = self._extractor(content='article.post-body', published='span.never')
        ext.parse()
        # Base extractor finds nothing here either → empty string
        self.assertEqual(ext.published, '')

    # --- cleanup ---

    def test_cleanup_removes_matching_elements(self):
        ext = self._extractor(content='article.post-body', cleanup=['nav.sidebar'])
        ext.parse()
        ext.cleanup()
        self.assertIsNone(ext.main_content.select_one('nav.sidebar'))
        self.assertIn('Article body text.', ext.main_content.get_text())

    def test_cleanup_multiple_selectors(self):
        html = """
        <html><head><title>T</title></head><body>
          <article>
            <p>Keep this.</p>
            <div class="ads">Ad</div>
            <aside class="promo">Promo</aside>
          </article>
        </body></html>
        """
        ext = self._extractor(html=html, content='article', cleanup=['div.ads', 'aside.promo'])
        ext.parse()
        ext.cleanup()
        text = ext.main_content.get_text()
        self.assertIn('Keep this.', text)
        self.assertNotIn('Ad', text)
        self.assertNotIn('Promo', text)

    def test_cleanup_no_selectors_is_harmless(self):
        ext = self._extractor(content='article.post-body', cleanup=[])
        ext.parse()
        ext.cleanup()  # must not raise
        self.assertIsNotNone(ext.main_content)

    def test_cleanup_selector_matches_nothing_is_harmless(self):
        ext = self._extractor(content='article.post-body', cleanup=['div.nonexistent'])
        ext.parse()
        ext.cleanup()  # must not raise
        self.assertIsNotNone(ext.main_content)


# ---------------------------------------------------------------------------
# Colusa rule matching and loading
# ---------------------------------------------------------------------------

class ColusaRuleMatchingTestCase(unittest.TestCase):

    def _make_colusa(self, site_rules=None, site_rules_file=''):
        config = {
            'title': 'T', 'author': 'A', 'version': 'v1',
            'homepage': 'http://x', 'output_dir': 'tests-dist',
            'urls': [],
        }
        if site_rules:
            config['site_rules'] = site_rules
        if site_rules_file:
            config['site_rules_file'] = site_rules_file
        return Colusa(config)

    def test_match_returns_first_matching_rule(self):
        colusa = self._make_colusa(site_rules=[
            {'pattern': '//other.com', 'content': 'div.other'},
            {'pattern': '//example.com', 'content': 'article.body'},
        ])
        rule = colusa._match_site_rule('https://example.com/page')
        self.assertIsNotNone(rule)
        self.assertEqual(rule.content, 'article.body')

    def test_match_returns_none_when_no_rule_matches(self):
        colusa = self._make_colusa(site_rules=[
            {'pattern': '//example.com', 'content': 'article'},
        ])
        rule = colusa._match_site_rule('https://other.com/page')
        self.assertIsNone(rule)

    def test_match_returns_none_with_no_rules(self):
        colusa = self._make_colusa()
        rule = colusa._match_site_rule('https://example.com/page')
        self.assertIsNone(rule)

    def test_load_rules_from_external_json_file(self):
        rules_data = [{'pattern': '//json.example.com', 'content': 'main'}]
        with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as f:
            json.dump(rules_data, f)
            tmp_path = f.name
        try:
            colusa = self._make_colusa(site_rules_file=tmp_path)
            self.assertEqual(len(colusa.site_rules), 1)
            self.assertEqual(colusa.site_rules[0].pattern, '//json.example.com')
        finally:
            os.unlink(tmp_path)

    def test_load_rules_from_external_yaml_file(self):
        rules_data = [{'pattern': '//yaml.example.com', 'content': 'section.content'}]
        with tempfile.NamedTemporaryFile(mode='w', suffix='.yml', delete=False) as f:
            yaml.safe_dump(rules_data, f)
            tmp_path = f.name
        try:
            colusa = self._make_colusa(site_rules_file=tmp_path)
            self.assertEqual(len(colusa.site_rules), 1)
            self.assertEqual(colusa.site_rules[0].pattern, '//yaml.example.com')
        finally:
            os.unlink(tmp_path)

    def test_inline_and_file_rules_are_merged(self):
        rules_data = [{'pattern': '//file.example.com', 'content': 'main'}]
        with tempfile.NamedTemporaryFile(mode='w', suffix='.yml', delete=False) as f:
            yaml.safe_dump(rules_data, f)
            tmp_path = f.name
        try:
            colusa = self._make_colusa(
                site_rules=[{'pattern': '//inline.example.com', 'content': 'article'}],
                site_rules_file=tmp_path,
            )
            self.assertEqual(len(colusa.site_rules), 2)
            patterns = {r.pattern for r in colusa.site_rules}
            self.assertIn('//inline.example.com', patterns)
            self.assertIn('//file.example.com', patterns)
        finally:
            os.unlink(tmp_path)

    def test_inline_rule_takes_priority_over_plugin_registry(self):
        """A dynamic rule matching the URL must be used instead of the built-in plugin."""
        from unittest.mock import patch, MagicMock

        html = """
        <html><head><title>T</title></head>
        <body><article class="dynamic"><p>Dynamic content.</p></article></body>
        </html>
        """
        colusa = self._make_colusa(site_rules=[
            {'pattern': '//example.com', 'content': 'article.dynamic'},
        ])

        with patch.object(colusa, 'download_content', return_value=html), \
             patch('colusa.etr.create_extractor') as mock_create:
            from colusa.config import UrlEntry
            colusa.ebook_generate_content(UrlEntry(path='https://example.com/page'))
            mock_create.assert_not_called()


if __name__ == '__main__':
    unittest.main()
