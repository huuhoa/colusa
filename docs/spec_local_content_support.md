# Spec: Local Content Support

## Overview

Allow `colusa` to include locally stored files (HTML or AsciiDoc) as input sources alongside remote URLs, so users can incorporate pre-downloaded or hand-written content into ebooks without needing to host or re-upload files.

## Requirements

### URL Entry Format

Entries in the `urls` field (and `parts[].urls`) support two forms:

**Plain string** (existing, unchanged):
```json
"https://example.com/article"
```

**Rich object** (new):
```json
{"path": "/home/user/article.html", "title": "My Title", "author": "Jane", "published": "2024-01-01"}
{"path": "./notes.adoc"}
```

All metadata fields (`title`, `author`, `published`) are optional. Plain strings remain fully backward-compatible.

### Local File Detection

A path is treated as local if it does not start with `http://` or `https://`.

### HTML Local Files

- File is read directly from disk (no download, no cache)
- Passed through the existing Extractor → Transformer → Render pipeline
- Metadata (title, author, published) is extracted from the HTML as normal
- If the user provides metadata in the config entry, it overrides extracted values

### AsciiDoc Local Files

Files with `.adoc` or `.asciidoc` extensions are passed through directly:
- Content is **not** parsed by BeautifulSoup
- Extractor and Transformer stages are **skipped**
- The file is copied to the output directory as-is
- Included in the master `index.asciidoc` via an `include::` directive
- Title is resolved in order: config entry → first `= ...` line in the file → filename stem

### Backward Compatibility

All existing configs using plain URL strings continue to work without any changes.

## Example Config

```json
{
    "title": "My Ebook",
    "author": "Jane",
    "version": "v1.0",
    "homepage": "https://example.com",
    "output_dir": "output",
    "urls": [
        "https://example.com/remote-article",
        {"path": "/home/user/saved-article.html"},
        {"path": "./notes.adoc", "title": "My Notes"},
        {"path": "/tmp/draft.html", "title": "Draft", "author": "John", "published": "2025-06-01"}
    ]
}
```
