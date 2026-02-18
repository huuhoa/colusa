# Plan: Fix High Severity Technical Debt

## Context

The technical debt assessment (`docs/tech_debts.md`) identified 10 high-severity issues across
type safety, error handling, and test coverage. This plan fixes all of them in one focused branch.

User decision: when `ContentNotFoundError` occurs, log and continue processing all URLs, then
print a failure summary at the end and exit with code 1.

---

## Files to Modify

| File | Changes |
|------|---------|
| `src/colusa/etr.py` | Fix `Optional` annotations; add public registry accessors |
| `src/colusa/fetch.py` | Fix mutable defaults; narrow broad exception |
| `src/colusa/colusa.py` | Fix silent exception; implement collect-and-report for failed URLs |
| `tests/test_plugin_registry.py` | New — smoke tests for plugin registration and `create_extractor` dispatch |

---

## Detailed Changes

### 1. `src/colusa/etr.py` — Fix type annotations + expose registry accessors

**Line 83** in `create_extractor()`:
```python
# Before
extractor: Extractor = None
# After
extractor: Optional[Extractor] = None
```

**Lines 145–146** in `Extractor.__init__()`:
```python
# Before
self.url_path: str = None
self.cached_path: str = None
# After
self.url_path: Optional[str] = None
self.cached_path: Optional[str] = None
```

(`Optional` is already imported at line 3 — no new import needed.)

**Add two public accessors** at module level (after the registry dicts) so tests can inspect registered plugins without touching name-mangled internals:
```python
def get_registered_extractors() -> dict:
    return dict(__EXTRACTORS)

def get_registered_transformers() -> dict:
    return dict(__TRANSFORMERS)
```

---

### 2. `src/colusa/fetch.py` — Fix mutable defaults and narrow exception

**Line 17** — `Fetch.__init__`:
```python
# Before
def __init__(self, config: dict[str, Any] = {}) -> None:
    self.config: dict[str, Any] = config
# After
def __init__(self, config: Optional[dict[str, Any]] = None) -> None:
    self.config: dict[str, Any] = config if config is not None else {}
```

**Line ~177** — `Downloader.__init__`:
```python
# Before
def __init__(self, downloader_config: dict[str, Any] = {}) -> None:
# After
def __init__(self, downloader_config: Optional[dict[str, Any]] = None) -> None:
    downloader_config = downloader_config or {}
```

**Line ~248** — `download_image()` — narrow broad `except Exception`:
```python
# Before
except Exception as ex:
    logs.error(f'error with URL: {url_path}. Exception: {ex}')
# After
except (requests.exceptions.RequestException, OSError) as ex:
    logs.error(f'error with URL: {url_path}. Exception: {ex}')
```

(`requests` is already imported in `fetch.py`.)

---

### 3. `src/colusa/colusa.py` — Fix exception handling

#### 3a. Silent `except Exception: pass` in `_process_local_asciidoc()`

Replace the bare except with specific types and a warning log:
```python
# Before
        except Exception:
            pass
# After
        except (OSError, UnicodeDecodeError) as e:
            logs.warn(f'could not read title from {src_path}: {e}')
```

#### 3b. Collect-and-report for `ContentNotFoundError`

**Add `_failed_urls` list to `__init__`** (after existing attribute setup):
```python
self._failed_urls: list[str] = []
```

**In `ebook_generate_content()` — replace commented-out raise:**
```python
# Before
    except etr.ContentNotFoundError as e:
        logs.error(e, url_path)
        # raise e
# After
    except etr.ContentNotFoundError as e:
        logs.error(e, url_path)
        self._failed_urls.append(url_path)
```

**In `generate()` — report failures after all URLs are processed:**
```python
    self.book_maker.ebook_generate_master_file()

    if self._failed_urls:
        print(f'\n[colusa] WARNING: content extraction failed for {len(self._failed_urls)} URL(s):')
        for url in self._failed_urls:
            print(f'  - {url}')
        raise SystemExit(1)
```

---

### 4. `tests/test_plugin_registry.py` — New smoke tests

```python
import unittest
from colusa import utils, etr


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
        from colusa.plugins.etr_staffeng import StaffEng
        self.assertIsInstance(extractor, StaffEng)

    def test_create_extractor_falls_back_to_base_for_unknown_url(self):
        from bs4 import BeautifulSoup
        bs = BeautifulSoup('<html><body></body></html>', 'html.parser')
        extractor = etr.create_extractor(bs, 'https://unknown-site-xyz.com/page', '/tmp')
        self.assertIs(type(extractor), etr.Extractor)
```

Note: `etr_staffeng.py` uses `@register_extractor('//staffeng.com')` which registers under the
class name as key. The test imports the class directly to use `assertIsInstance`.

---

## Verification

1. `pytest --no-cov` — all 32 existing tests plus new plugin registry tests pass.
2. Confirm the three `Optional` fixes remove type-checker warnings.
3. Run `colusa generate` against a config containing a URL whose content cannot be found
   — confirm failure summary is printed to stdout and process exits with code 1.
4. Run `colusa generate` against a valid config — confirm exit code is 0 and no summary printed.
