# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

**colusa** is a CLI tool that downloads web articles, extracts their content, and converts them to AsciiDoc format for compiling into ebooks (HTML, EPUB, PDF via asciidoctor).

## Git Workflow

Direct push to `main` is not allowed. Always work on a feature branch and open a PR:

```sh
git checkout -b my-branch
# make changes, commit
gh pr create
gh pr merge <number> --squash
```

## Development Setup

```sh
# Install in development mode with test dependencies
pip install -e ".[test]"

# Or with all dev dependencies
pip install -e ".[all]"
```

## Commands

```sh
# Run all tests
pytest

# Run a single test file
pytest tests/test_transformer.py

# Run a single test
pytest tests/test_transformer.py::TransformerTestCase::test_tag_p_1

# Run tests without coverage (faster)
pytest --no-cov

# Run colusa CLI
colusa init new_ebook.json       # generate a config template
colusa generate new_ebook.json   # process URLs and generate AsciiDoc
colusa crawl --url <URL>         # crawl a URL to discover article links
```

## Architecture

The pipeline for converting a URL to AsciiDoc:

1. **Config** (`config.py`) — `BookConfig` dataclass (loaded from JSON or YAML) drives everything
2. **Download** (`fetch.py`) — `Downloader` fetches URLs; supports pluggable `Fetch` subclasses (registered via `@register_fetch`) for sites requiring special handling (e.g., Tor)
3. **Extract** (`etr.py`) — `Extractor` isolates the article body from HTML soup; matched to URLs via `@register_extractor_v2(id, pattern)` decorator
4. **Transform** (`etr.py`) — `Transformer` calls `AsciidocVisitor` to walk the BeautifulSoup tree and emit AsciiDoc markup; matched via `@register_transformer_v2(id, pattern)`
5. **Render** (`etr.py`) — `Render` writes individual `.asciidoc` chapter files and generates `index.asciidoc` + `Makefile`

### Plugin System

All site-specific logic lives in `src/colusa/plugins/etr_*.py`. Each plugin file:
- Registers an `Extractor` subclass with `@register_extractor_v2(id, '//domain.com')` to override content detection/metadata parsing
- Registers a `Transformer` subclass with `@register_transformer_v2(id, '//domain.com')` to override AsciiDoc generation for site-specific HTML structures

Plugins are loaded automatically at startup via `utils.scan('colusa.plugins')`.

### Visitor Pattern

`NodeVisitor` (`visitor.py`) drives the HTML-to-AsciiDoc conversion. `AsciidocVisitor` (`asciidoc_visitor.py`) implements `visit_tag_<tagname>` methods for each HTML tag. To add handling for a new HTML tag, add a `visit_tag_<tagname>` method to `AsciidocVisitor` or override it in a site-specific `Transformer` subclass.

### Adding Support for a New Website

1. Create `src/colusa/plugins/etr_<sitename>.py`
2. Subclass `Extractor` and decorate with `@register_extractor_v2('unique_id', '//domain.com')` — override `_find_main_content()`, `_parse_title()`, etc. as needed
3. Optionally subclass `Transformer` and decorate with `@register_transformer_v2('unique_id', '//domain.com')` — override `transform()` or add `visit_tag_*` methods for site-specific HTML

### Configuration Schema

Key fields in the JSON/YAML config beyond the basic title/author/urls:
- `multi_part: true` + `parts: [{title, description, urls}]` — for books with multiple sections
- `postprocessing: [{processor, params}]` — run registered `PostProcessor` subclasses on output files
- `extractors`/`transformers` — key-value config passed to registered plugins at startup
- `downloader` — per-fetcher configuration (key must match a `@register_fetch(name, pattern)` name)
- `book_file_name` — name of the master AsciiDoc file (default: `index.asciidoc`)
- `title_prefix_trim` — strip a common prefix from all article titles

### Caching

Downloaded HTML is cached in `<output_dir>/.cached/<sha256>.html`. Delete this directory to force re-download.
