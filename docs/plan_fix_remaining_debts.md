# Plan: Fix Remaining Technical Debts

## Context

After PR #235, 2 high-severity and 33 medium-severity issues remain (total 43).
This plan addresses them in two focused, low-risk PRs ordered by impact.

Remaining open items from `docs/tech_debts.md`:
- **HIGH**: download failure test coverage; post-processor test coverage
- **MEDIUM**: debug prints in production code; dead commented code; torpy unused
  dependency; wrong Python version floor; `BookConfig.to_dict()` data loss;
  `DownloaderConfig` dead dataclass

---

## PR A — Quick fixes and cleanup

**Branch:** `fix/debt-cleanup`

### Files to modify

| File | Changes |
|------|---------|
| `src/colusa/etr.py` | Remove debug `print` and commented-out prints |
| `src/colusa/fetch.py` | Remove commented-out dead code |
| `src/colusa/config.py` | Fix `to_dict()` serialisation; remove `DownloaderConfig` |
| `pyproject.toml` | Move `torpy` to optional extra; bump `requires-python` to `>=3.9` |

---

### 1. `src/colusa/etr.py` — Remove debug prints

**Line 412** in `Transformer.tag_wrapper_pre()`:
```python
# Before
if len(content) == 0:
    print('PRE ====', text)
    content.append(...)

# After
if len(content) == 0:
    content.append(...)
```

**Lines 429, 431** in `transform()` — delete the two commented-out print lines:
```python
# Before
    visitor = self.create_visitor()
    # print(self.site)
    self.value = visitor.visit(...)
    # print(value)

# After
    visitor = self.create_visitor()
    self.value = visitor.visit(...)
```

---

### 2. `src/colusa/fetch.py` — Remove commented-out dead code

**Line 237** — delete commented-out print in `download_image()`:
```python
# Before
    # logs.info(f'call download_image with url_path is {url_path}')
    result = urllib.parse.urlsplit(url_path)

# After
    result = urllib.parse.urlsplit(url_path)
```

**Lines 202–203** — delete commented-out code in `get_fetch_instance()`:
```python
# Before
        if fetch_obj.can_process(url_path):
            return fetch_obj
        # if re.match(pattern, url_path):
        #     return fetch_obj

# After
        if fetch_obj.can_process(url_path):
            return fetch_obj
```

---

### 3. `src/colusa/config.py` — Fix `to_dict()` and remove dead `DownloaderConfig`

**`to_dict()` lines 208, 204–206** — serialise `UrlEntry` and `PartConfig.urls` correctly:
```python
# Before
'parts': [
    {'title': p.title, 'description': p.description, 'urls': p.urls}
    for p in self.parts
],
'urls': self.urls,

# After
'parts': [
    {
        'title': p.title,
        'description': p.description,
        'urls': [{'path': e.path, 'title': e.title,
                  'author': e.author, 'published': e.published}
                 for e in p.urls],
    }
    for p in self.parts
],
'urls': [{'path': e.path, 'title': e.title,
           'author': e.author, 'published': e.published}
         for e in self.urls],
```

**`DownloaderConfig` (line 52–56)** — delete the unused empty dataclass entirely.

---

### 4. `pyproject.toml` — Move `torpy` to optional; fix Python floor

**Move `torpy` from `dependencies` to a new optional extra:**
```toml
# Remove from dependencies:
"torpy~=1.1.6",

# Add new optional group:
[project.optional-dependencies]
tor = [
    "torpy~=1.1.6",
]
```

**Bump `requires-python`:**
```toml
# Before
requires-python = ">=3.8"

# After
requires-python = ">=3.9"
```

**Update `classifiers`** — remove the `Python :: 3.8` classifier line.

---

### Verification for PR A

```sh
.venv/bin/pytest --no-cov   # 41 tests still pass
grep -r 'torpy' src/        # no references in source
python -c "from colusa.config import BookConfig; ..."  # to_dict roundtrip test
```

---

## PR B — Test coverage for download failures and post-processing

**Branch:** `fix/debt-test-coverage`

### Files to create / modify

| File | Changes |
|------|---------|
| `tests/test_downloader.py` | New — tests for `Downloader.download_url()` and `download_image()` error paths |
| `tests/test_postprocessor.py` | New — tests for `PostProcessor` and `create_postprocessor()` |
| `tests/test_plugin_extraction.py` | New — fixture-based extraction tests for representative plugins |

---

### 1. `tests/test_downloader.py` — Download failure coverage

```python
import unittest
from unittest.mock import patch, MagicMock
import requests
from colusa import fetch


class DownloaderDownloadUrlTestCase(unittest.TestCase):

    @patch('colusa.fetch.Fetch.get')
    def test_non_200_response_logs_error_and_writes_temp_file(self, mock_get):
        mock_resp = MagicMock()
        mock_resp.status_code = 404
        mock_resp.content = b'not found'
        mock_get.return_value = mock_resp

        with fetch.Downloader() as dl:
            dl.download_url('https://example.com/page', '/tmp/colusa_test_out.html')

        import os
        self.assertTrue(os.path.exists('/tmp/colusa_test_out.html.temp'))
        os.remove('/tmp/colusa_test_out.html.temp')

    @patch('colusa.fetch.Fetch.get')
    def test_successful_download_writes_file(self, mock_get):
        import io
        mock_resp = MagicMock()
        mock_resp.status_code = 200
        mock_resp.raw = io.BytesIO(b'<html>ok</html>')
        mock_get.return_value = mock_resp

        import tempfile, os
        with tempfile.NamedTemporaryFile(delete=False, suffix='.html') as f:
            out = f.name
        try:
            with fetch.Downloader() as dl:
                dl.download_url('https://example.com/page', out)
            with open(out, 'rb') as f:
                self.assertEqual(f.read(), b'<html>ok</html>')
        finally:
            os.remove(out)


class DownloadImageTestCase(unittest.TestCase):

    @patch('colusa.fetch.Downloader.download_url')
    @patch('os.path.exists', return_value=False)
    def test_connection_error_logs_warning(self, mock_exists, mock_dl):
        mock_dl.side_effect = requests.exceptions.ConnectionError('refused')
        # Should not raise
        fetch.download_image('https://example.com/img.png', '/tmp')

    @patch('colusa.fetch.Downloader.download_url')
    @patch('os.path.exists', return_value=False)
    def test_request_exception_logs_error(self, mock_exists, mock_dl):
        mock_dl.side_effect = requests.exceptions.Timeout('timed out')
        # Should not raise
        fetch.download_image('https://example.com/img.png', '/tmp')

    @patch('os.path.exists', return_value=True)
    def test_skips_download_when_image_already_cached(self, mock_exists):
        with patch('colusa.fetch.Downloader.download_url') as mock_dl:
            fetch.download_image('https://example.com/img.png', '/tmp')
            mock_dl.assert_not_called()
```

---

### 2. `tests/test_postprocessor.py` — PostProcessor coverage

```python
import unittest
from colusa import etr


class PostProcessorTestCase(unittest.TestCase):

    def test_base_run_is_noop(self):
        pp = etr.PostProcessor('/some/file.asciidoc', [])
        pp.run()   # must not raise

    def test_create_postprocessor_raises_for_unknown_name(self):
        with self.assertRaises(etr.PostProcessorNotFoundError) as ctx:
            etr.create_postprocessor('does-not-exist', '/tmp/f.asciidoc', [])
        self.assertIn('does-not-exist', str(ctx.exception))

    def test_postprocessor_not_found_error_message(self):
        err = etr.PostProcessorNotFoundError('my-proc')
        self.assertEqual(str(err), 'Post Processor my-proc is not registered')
```

---

### 3. `tests/test_plugin_extraction.py` — Representative plugin tests

Strategy: inline minimal HTML fixture for each plugin; assert that `_find_main_content()`
returns a non-None tag, and that the extracted title is correct.

```python
import unittest
from bs4 import BeautifulSoup
from colusa import utils


def _load_plugins():
    utils.scan('colusa.plugins')


class StaffEngExtractionTestCase(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        _load_plugins()

    def test_finds_main_content(self):
        from colusa.etr import create_extractor
        html = '<html><body><div class="blog-post-content"><p>hello</p></div></body></html>'
        bs = BeautifulSoup(html, 'html.parser')
        extractor = create_extractor(bs, 'https://staffeng.com/guides/x', '/tmp')
        extractor.url_path = 'https://staffeng.com/guides/x'
        extractor.cached_path = '/tmp'
        content = extractor._find_main_content()
        self.assertIsNotNone(content)


class MediumExtractionTestCase(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        _load_plugins()

    def test_finds_article_tag(self):
        from colusa.etr import create_extractor
        html = '<html><head><meta property="og:title" content="My Post"/></head><body><article><p>text</p></article></body></html>'
        bs = BeautifulSoup(html, 'html.parser')
        extractor = create_extractor(bs, 'https://medium.com/@user/my-post', '/tmp')
        content = extractor._find_main_content()
        self.assertIsNotNone(content)
        self.assertEqual(content.name, 'article')

    def test_parses_title_from_h1(self):
        from colusa.etr import create_extractor
        html = '<html><body><article><h1>My Article</h1><p>body</p></article></body></html>'
        bs = BeautifulSoup(html, 'html.parser')
        extractor = create_extractor(bs, 'https://medium.com/@user/my-post', '/tmp')
        extractor.main_content = extractor._find_main_content()
        title = extractor._parse_title()
        self.assertEqual(title, 'My Article')


class WikipediaExtractionTestCase(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        _load_plugins()

    def test_finds_main_content(self):
        from colusa.etr import create_extractor
        html = '<html><body><div id="mw-content-text"><p>wiki content</p></div></body></html>'
        bs = BeautifulSoup(html, 'html.parser')
        extractor = create_extractor(bs, 'https://en.wikipedia.org/wiki/Test', '/tmp')
        content = extractor._find_main_content()
        self.assertIsNotNone(content)
```

Note: for plugins that use the old `utils.scan` import path (no `sys.modules` registration),
use `type(extractor).__name__` rather than `assertIsInstance` — same pattern as
`test_plugin_registry.py`.

---

### Verification for PR B

```sh
.venv/bin/pytest --no-cov   # all tests pass including new ones
```

---

## Remaining medium-severity debt (deferred)

The following items are tracked but deferred — they require broader refactoring
and should each get their own focused PR when prioritised:

| Item | Effort | Notes |
|------|--------|-------|
| Split `download_content()` into local vs remote | Medium | `colusa.py` L133–166 |
| Decompose `Colusa` class | Large | config loading, dispatch, download, render |
| Remove v1 `register_extractor()` dead code | Small | `etr.py` L29–38 |
| Rename `Transformer.site` → `main_content` | Small | consistency with `Extractor` |
| Thread-safety for plugin registries | Medium | or document single-thread constraint |
| Late/deferred imports (`chardet`, `json`, etc.) | Small | move to module level |
| `BookConfig.to_dict()` roundtrip test | Small | add to PR A verification |
| `crawlers.py` stray `logs.info("hello")` | Trivial | remove in any passing PR |

---

## Implementation order

```
PR A  →  PR B
```

PR A is a prerequisite to establish a clean baseline. PR B adds the test coverage
for the two remaining HIGH-severity gaps and lays the pattern for per-plugin tests.
