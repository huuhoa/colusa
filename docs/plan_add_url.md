# Plan: `colusa add-url` Command

## Files to Modify

| File | Change |
|------|--------|
| `src/colusa/cli.py` | Add `add_url` subcommand and argument parser |
| `src/colusa/colusa.py` | Add `Colusa.add_url()` static method with all logic |
| `README.md` | Document the new `add-url` subcommand |
| `docs/features_roadmap.md` | Mark feature 3 as implemented |

No changes to `config.py`, `etr.py`, or `fetch.py` are needed.

---

## 1. `src/colusa/cli.py` — Add subcommand

### 1a. Register the subcommand in `parse_args()`

```python
add_url_parser = commands.add_parser(
    'add-url',
    help='Append a URL to an existing config file'
)
add_url_parser.set_defaults(func=add_url)
add_url_parser.add_argument('input', type=str, help='Config file (JSON or YAML)')
add_url_parser.add_argument('url', type=str, help='URL or local file path to add')
add_url_parser.add_argument('--title', type=str, default=None, help='Override title')
add_url_parser.add_argument('--author', type=str, default=None, help='Override author')
add_url_parser.add_argument('--published', type=str, default=None, help='Override published date')
add_url_parser.add_argument('--part', type=str, default=None,
                            help='Part title to add to (multi-part books only)')
add_url_parser.add_argument('--fetch-title', action='store_true',
                            help='Download the page and extract the title automatically')
```

### 1b. Add the handler function

```python
def add_url(args: argparse.Namespace) -> None:
    try:
        Colusa.add_url(
            config_path=args.input,
            url=args.url,
            title=args.title,
            author=args.author,
            published=args.published,
            part=args.part,
            fetch_title=args.fetch_title,
        )
    except ConfigurationError as e:
        logs.error(e)
        raise SystemExit(1)
```

---

## 2. `src/colusa/colusa.py` — Add `Colusa.add_url()`

Add as a `@staticmethod` on the `Colusa` class. Keep all logic inside this one method to
avoid unnecessary helpers.

### 2a. Load config file

```python
import json, pathlib
import yaml  # already in deps via PyYAML

path = pathlib.Path(config_path)
if not path.exists():
    raise ConfigurationError(f'Config file not found: {config_path}')

ext = path.suffix.lower()
if ext == '.json':
    data = json.loads(path.read_text(encoding='utf-8'))
elif ext in ('.yml', '.yaml'):
    data = yaml.safe_load(path.read_text(encoding='utf-8'))
else:
    raise ConfigurationError(f'Unsupported config format: {ext}. Use .json, .yml, or .yaml')
```

### 2b. Duplicate check

Collect all existing paths across top-level `urls` and all `parts[].urls`:

```python
def _existing_paths(data: dict) -> set[str]:
    paths: set[str] = set()
    for entry in data.get('urls', []):
        paths.add(entry if isinstance(entry, str) else entry.get('path', ''))
    for part in data.get('parts', []):
        for entry in part.get('urls', []):
            paths.add(entry if isinstance(entry, str) else entry.get('path', ''))
    return paths

if url in _existing_paths(data):
    logs.warn(f'URL already exists in config: {url}')
    return
```

### 2c. Optional title fetch (`--fetch-title`)

```python
if fetch_title:
    try:
        from colusa.fetch import Downloader
        from bs4 import BeautifulSoup
        import tempfile

        output_dir = data.get('output_dir') or tempfile.mkdtemp()
        downloader = Downloader()
        cached = pathlib.Path(output_dir) / '.cached' / f'{utils.get_hexdigest(url)}.html'
        if not cached.exists():
            downloader.download_url(url, str(cached))
        html = cached.read_text(encoding='utf-8', errors='replace')
        soup = BeautifulSoup(html, 'html.parser')

        fetched_title = None
        og = soup.find('meta', property='og:title')
        if og and og.get('content'):
            fetched_title = og['content'].strip()
        elif soup.title and soup.title.string:
            fetched_title = soup.title.string.strip()
        elif soup.find('h1'):
            fetched_title = soup.find('h1').get_text(strip=True)

        if fetched_title:
            logs.info(f'Fetched title: "{fetched_title}"')
            title = title or fetched_title   # explicit --title takes precedence
    except Exception as e:
        logs.warn(f'Could not fetch title for {url}: {e}')
```

### 2d. Build the new entry

```python
if title or author or published:
    entry: Any = {'path': url}
    if title:     entry['title'] = title
    if author:    entry['author'] = author
    if published: entry['published'] = published
else:
    entry = url   # plain string — no metadata
```

### 2e. Append to the right list

**Single-part book:**
```python
if not data.get('multi_part'):
    data.setdefault('urls', []).append(entry)
    logs.info(f'Added: {url}')
```

**Multi-part book:**
```python
else:
    parts = data.get('parts', [])
    if not part:
        part_titles = ', '.join(f'"{p["title"]}"' for p in parts)
        raise ConfigurationError(
            f'This is a multi-part book. Use --part <title> to specify a part. '
            f'Available parts: {part_titles}'
        )
    matched = next(
        (p for p in parts if p.get('title', '').lower() == part.lower()), None
    )
    if matched is None:
        part_titles = ', '.join(f'"{p["title"]}"' for p in parts)
        raise ConfigurationError(
            f'Part not found: "{part}". Available parts: {part_titles}'
        )
    matched.setdefault('urls', []).append(entry)
    logs.info(f'Added to part "{matched["title"]}": {url}')
```

### 2f. Write back

```python
with path.open('w', encoding='utf-8') as f:
    if ext == '.json':
        json.dump(data, f, indent=4, ensure_ascii=False)
        f.write('\n')
    else:
        yaml.dump(data, f, default_flow_style=False, allow_unicode=True)
```

---

## 3. Tests — `tests/test_add_url.py`

| Test | Description |
|------|-------------|
| `test_add_plain_url_to_json` | Plain URL appended as string when no metadata |
| `test_add_url_with_metadata` | Entry written as dict when `--title` supplied |
| `test_add_url_to_yaml` | YAML config loaded and saved correctly |
| `test_duplicate_url_is_skipped` | Duplicate URL → warning, file unchanged |
| `test_multipart_requires_part_flag` | Multi-part without `--part` → `ConfigurationError` |
| `test_multipart_part_not_found` | `--part` with unknown title → `ConfigurationError` |
| `test_multipart_adds_to_correct_part` | URL appended to correct part's `urls` list |
| `test_config_not_found` | Missing config file → `ConfigurationError` |
| `test_unsupported_extension` | `.txt` config → `ConfigurationError` |
| `test_fetch_title_sets_title` | `--fetch-title` with mock downloader → title extracted and stored |
| `test_fetch_title_explicit_overrides_fetched` | `--title` takes precedence over `--fetch-title` result |
| `test_fetch_title_network_error_continues` | Network error during fetch → warning logged, entry still added |

---

## 4. `README.md` — Document the new command

Add an `add-url` entry to the CLI commands section. The entry should show:
- Basic usage (plain URL)
- Usage with `--fetch-title`
- Usage with explicit metadata flags
- Usage for multi-part books with `--part`

Place it after the existing `colusa init` / `colusa generate` / `colusa crawl` entries so the
documented command order matches the typical workflow: init → add-url → generate.

---

## 5. `docs/features_roadmap.md` — Mark feature 3 as implemented

Update the entry for feature 3 to indicate it is done:

```markdown
**3. ~~`colusa add-url <config> <url>`~~ ✅ Implemented**
```

---

## Verification

1. `pytest tests/test_add_url.py --no-cov` — all new tests pass.
2. `pytest --no-cov` — all existing tests still pass.
3. Manual smoke test:
   ```sh
   colusa init /tmp/test.json
   colusa add-url /tmp/test.json https://staffeng.com/guides/overview --fetch-title
   # Verify entry appears in /tmp/test.json with fetched title
   colusa add-url /tmp/test.json https://staffeng.com/guides/overview
   # Verify: "[warn] URL already exists in config"
   ```
