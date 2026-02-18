# Technical Debt Assessment — colusa

> Assessed: 2026-02-18
> Last updated: 2026-02-18 (after PR #235 — fix high-severity technical debts)

## Summary

| Category | High | Medium | Low | Total |
|----------|:----:|:------:|:---:|:-----:|
| Type Safety | ~~3~~ 0 | 2 | 0 | 2 |
| Error Handling | ~~3~~ 0 | 2 | 0 | 2 |
| Code Quality / Duplication | 0 | 4 | 3 | 7 |
| Architecture / Coupling | 0 | 4 | 2 | 6 |
| Naming / Clarity | 0 | 4 | 2 | 6 |
| Late / Deferred Imports | 0 | 4 | 0 | 4 |
| Test Coverage | ~~4~~ 2 | 2 | 0 | 4 |
| Documentation | 0 | 4 | 0 | 4 |
| Dependencies / Packaging | 0 | 3 | 0 | 3 |
| Miscellaneous | 0 | 4 | 1 | 5 |
| **Total** | **~~10~~ 2** | **33** | **8** | **43** |

---

## HIGH Severity

### Type Safety

> All three high-severity type-safety issues were resolved in PR #235.

| File | Lines | Issue | Status |
|------|-------|-------|--------|
| `src/colusa/etr.py` | 145–146 | `self.url_path: str = None` and `self.cached_path: str = None` violate their own type hints. | ✅ Fixed — changed to `Optional[str] = None` |
| `src/colusa/etr.py` | 83 | `extractor: Extractor = None` annotated as non-optional but initialised to `None`. | ✅ Fixed — changed to `Optional[Extractor] = None` |
| `src/colusa/fetch.py` | 17, 177 | `def __init__(self, config: dict[str, Any] = {})` mutable default argument in both `Fetch` and `Downloader`. | ✅ Fixed — changed to `Optional[dict] = None` with safe init |

### Error Handling

> All three high-severity error-handling issues were resolved in PR #235.

| File | Lines | Issue | Status |
|------|-------|-------|--------|
| `src/colusa/colusa.py` | 214–215 | `except Exception: pass` silently swallows all errors when reading an AsciiDoc title. | ✅ Fixed — narrowed to `(OSError, UnicodeDecodeError)` with `logs.warn()` |
| `src/colusa/colusa.py` | 260–262 | `ContentNotFoundError` caught and logged but `raise e` was commented out — broken URLs silently skipped. | ✅ Fixed — failures collected in `_failed_urls`; summary printed and `SystemExit(1)` raised after all URLs processed |
| `src/colusa/fetch.py` | 248 | `except Exception as ex:` in `download_image()` overly broad. | ✅ Fixed — narrowed to `(requests.exceptions.RequestException, OSError)` |

### Test Coverage

| Area | Issue | Status |
|------|-------|--------|
| Plugin files | 37 plugin files under `src/colusa/plugins/` have no tests for extraction logic or AsciiDoc output. | ⚠️ Partially addressed — smoke tests added in PR #235 verify registration shape and dispatch; per-plugin extraction logic remains untested |
| Plugin registry | `create_extractor()` and `create_transformer()` fallback logic untested. | ✅ Fixed — dispatch and fallback covered in `tests/test_plugin_registry.py` |
| Download failures | HTTP errors, connection timeouts, and file I/O errors have zero test coverage. | ❌ Still open |
| Post-processing | `PostProcessor` base class and `create_postprocessor()` are never tested. | ❌ Still open |

---

## MEDIUM Severity

### Architecture / Coupling

| File | Lines | Issue |
|------|-------|-------|
| `src/colusa/etr.py` | 16–26 | Module-level dicts `__EXTRACTORS`, `__TRANSFORMERS`, `__POSTPROCESSORS` are global mutable state. Not thread-safe; state bleeds between test runs. |
| `src/colusa/colusa.py` | — | `Colusa` class mixes config loading, URL dispatching, downloading, and rendering. Should be decomposed into focused collaborators. |
| `src/colusa/colusa.py` | 133–166 | `download_content()` handles both local files and remote URLs in one method. These are separate concerns and should be split. |
| `src/colusa/fetch.py` | 174–186 | `Downloader` constructor imperatively instantiates fetcher classes from config. A factory pattern would be cleaner and more testable. |

### Code Quality / Duplication

| File | Lines | Issue |
|------|-------|-------|
| `src/colusa/asciidoc_visitor.py` | ~404 | Debug `print('PRE ====', text)` left in production code. |
| `src/colusa/etr.py` | 421–423 | Three commented-out `print` debug statements in `transform()`. |
| `src/colusa/colusa.py` | 133–166 | `chardet.detect()` called twice on the same file bytes in `download_content()` — read, detect encoding, read again. |
| `src/colusa/etr.py` | 29–48 | `register_extractor()` (v1) and `register_extractor_v2()` are nearly identical. The v1 version is effectively dead code. |

### Naming / Clarity

| File | Lines | Issue |
|------|-------|-------|
| `src/colusa/etr.py` | 385–389 | `Transformer` uses `self.site` for the content tag; `Extractor` uses `self.main_content` for the same concept — inconsistent. |
| `src/colusa/asciidoc_visitor.py` | 76 | `visit_heading_node(level)` is a function factory but reads like an ordinary method. |
| `src/colusa/visitor.py` | 37–40 | Method naming convention is mixed: `visit_text`, `visit_tag_{name}`, `visit_BeautifulSoup`, `visit_unknown` — no single clear pattern. |
| `src/colusa/colusa.py` | — | Class name `Colusa` gives no indication of its purpose or responsibilities. |

### Late / Deferred Imports

| File | Lines | Issue |
|------|-------|-------|
| `src/colusa/colusa.py` | 144, 151, 196 | `chardet` imported inside methods multiple times; should be at module level. |
| `src/colusa/etr.py` | 297–298 | `json` and `dateutil.parser` imported inside `_parse_yoast_data()`. |
| `src/colusa/crawlers.py` | 33 | `json` imported inside `run()`. |
| `src/colusa/colusa.py` | 24, 89 | Heavy `etr` sub-imports deferred to `__init__` at runtime. |

### Configuration / Serialisation

| File | Lines | Issue |
|------|-------|-------|
| `src/colusa/config.py` | 179–180 | `BookConfig.to_dict()` serialises `urls` as raw `UrlEntry` objects rather than dicts — would fail or produce wrong output if the result were re-parsed. `SiteRule` objects in `site_rules` have the same problem. |
| `src/colusa/config.py` | 56 | `DownloaderConfig` dataclass has no fields and is never used anywhere. |

### Dependencies / Packaging

| Issue | Details |
|-------|---------|
| Unused hard dependency | `torpy~=1.1.6` is in `pyproject.toml` as a required dependency but does not appear to be used in the installed codebase. Should be optional or removed. |
| Broken Python version floor | `requires-python = ">=3.8"` is declared, but the codebase uses bare generic annotations (`dict[str, Any]`, `list[str]`) which require Python 3.9+. Python 3.8 support is silently broken. |
| bumpversion out of sync | `[tool.bumpversion] current_version` was `0.14.0` while the actual files were at `0.15.0` (now corrected to `0.16.0`). |

### Test Coverage (medium)

| Area | Issue |
|------|-------|
| Visitor / transformer | Only one test (`test_tag_p_1`) exercises the visitor pattern — a vast surface area is uncovered. |
| Local file handling | Encoding detection and "file not found" error paths are not tested. |

### Documentation

| File | Issue |
|------|-------|
| `src/colusa/etr.py` | Many public methods (`cleanup()`, `transform()`, `create_extractor()`) lack docstrings. |
| `src/colusa/visitor.py` | No explanation of how visitor method names are constructed from tag names. |
| `src/colusa/config.py` | `to_dict()` data-loss behaviour (UrlEntry objects not serialised) is not documented. |
| Plugin system | No documented API contract for creating plugins beyond reading example files. |

---

## LOW Severity

| File | Lines | Issue |
|------|-------|-------|
| `src/colusa/asciidoc_visitor.py` | 247–254 | Complex `srcset` dimension-parsing logic where `default_dim` is `","` (invalid) — likely dead or broken path. |
| `src/colusa/crawlers.py` | 21 | `logs.info()` called with the message `"hello"` — stray debug log. |
| `src/colusa/etr.py` | 134–135 | `ContentNotFoundError.__init__` accepts `*args, **kwargs` but ignores them all with `pass`. |
| `src/colusa/fetch.py` | 237 | Commented-out `print` debug statement. |
| `src/colusa/fetch.py` | 202–203 | Commented-out dead code in `get_fetch_instance()`. |
| `src/colusa/plugins/etr_knowledgegraph.py` | 10 | Unresolved `TODO` comment about metadata access when `main_content` is unavailable. |
| `src/colusa/plugins/etr_pragmatic_engineer.py` | ~143 | `pass` statement suggests incomplete post-processing implementation. |

---

## Recommended Priorities

1. **Add per-plugin extraction tests** — smoke tests exist for registration; fixture-based tests for each plugin's HTML-to-AsciiDoc output are still missing.
2. **Test download failure paths** — HTTP errors, timeouts, and I/O errors have no coverage.
3. **Test post-processing** — `PostProcessor` base class and `create_postprocessor()` are untested.
4. **Drop or make `torpy` optional** — it should not be a mandatory install dependency.
5. **Fix the Python version floor** — bump `requires-python` to `>=3.9` or add `from __future__ import annotations`.
6. **Remove debug `print` statement** in `asciidoc_visitor.py`.
7. **Fix `BookConfig.to_dict()`** to properly serialise `UrlEntry` and `SiteRule` objects.
8. **Thread-safety for plugin registries** — or explicitly document that colusa is single-threaded only.
