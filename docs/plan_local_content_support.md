# Plan: Local Content Support

## Files to Modify

| File | Change |
|------|--------|
| `src/colusa/config.py` | Add `UrlEntry` dataclass; update `BookConfig.urls` and `PartConfig.urls` |
| `src/colusa/colusa.py` | Handle local paths in `download_content`; route `.adoc` to passthrough; apply metadata overrides |
| `src/colusa/etr.py` | Add `Render.render_asciidoc_passthrough()` |

---

## 1. `config.py` — Add `UrlEntry`

Add a new dataclass:
```python
@dataclass
class UrlEntry:
    path: str
    title: Optional[str] = None
    author: Optional[str] = None
    published: Optional[str] = None
```

In `BookConfig.from_dict()` and the `PartConfig` list parsing, convert each entry:
- `str` → `UrlEntry(path=str)` (backward compat)
- `dict` → `UrlEntry(path=d['path'], title=d.get('title'), author=d.get('author'), published=d.get('published'))`

Update field types:
- `BookConfig.urls: list[UrlEntry]`
- `PartConfig.urls: list[UrlEntry]`

---

## 2. `colusa.py` — Core changes

### 2a. Helper: detect local paths
```python
@staticmethod
def _is_local_path(path: str) -> bool:
    return not path.startswith(('http://', 'https://'))
```

### 2b. `download_content()` — accept `UrlEntry`, handle local files
- Signature: `download_content(self, url_entry: UrlEntry) -> str`
- If `_is_local_path(url_entry.path)`: read file from disk directly (no cache, no Downloader)
- Otherwise: existing cache + Downloader logic, using `url_entry.path` as the URL

### 2c. `ebook_generate_content()` — accept `UrlEntry`, route by type
- Signature: `ebook_generate_content(self, url_entry: UrlEntry) -> None`
- If path ends with `.adoc` or `.asciidoc`: call `_process_local_asciidoc(url_entry)`
- Otherwise (HTML, remote URL): existing pipeline with metadata override after `extractor.parse()`:
  ```python
  if url_entry.title:     extractor.title = url_entry.title
  if url_entry.author:    extractor.author = url_entry.author
  if url_entry.published: extractor.published = url_entry.published
  ```

### 2d. New: `_process_local_asciidoc(url_entry: UrlEntry)`
1. Read `.adoc` file content from `url_entry.path`
2. Resolve title (in priority order): `url_entry.title` → first `= ...` line → `Path(path).stem`
3. Derive output filename via existing `_get_saved_file_name(url_entry.path)` + `.asciidoc`
4. Copy file to `<output_dir>/<derived_filename>`
5. Call `self.book_maker.render_asciidoc_passthrough(derived_filename)`

### 2e. `_generate_book_single_part()` / `_generate_book_multi_part()`
No structural changes — `config.urls` is now `list[UrlEntry]` so these pass `UrlEntry` objects to `ebook_generate_content()` automatically.

---

## 3. `etr.py` — Add passthrough method to `Render`

```python
def render_asciidoc_passthrough(self, file_name: str) -> None:
    """Register a pre-written AsciiDoc file in the book's include list."""
    self.file_list.append((file_name, 1))
```

The file is already copied to `output_dir` in step 2d, so registering it in `file_list` is sufficient for inclusion in the master `index.asciidoc` via the `include::` directive.

---

## Verification

1. **Remote URL (existing)**: plain string URL in config → no change in behaviour
2. **Local HTML**: plain path to `.html` file → chapter appears with metadata extracted from HTML
3. **Local HTML with metadata override**: dict entry with `title`/`author` → rendered chapter uses overridden values
4. **Local AsciiDoc**: dict entry with `.adoc` path → file copied to output, included in `index.asciidoc`
5. **AsciiDoc title resolution**: no `title` in config → title parsed from `= ...` line in file
6. **Run tests**: `pytest` — all existing tests pass
