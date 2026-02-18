# Plan: `--dry-run` Flag for `generate`

## Files to Modify

| File | Change |
|------|--------|
| `src/colusa/cli.py` | Add `--dry-run` flag to `generate` subparser; route to `dry_run_book` |
| `src/colusa/colusa.py` | Add `dry_run_book()` classmethod, `dry_run()` method, and two resolver helpers |
| `README.md` | Document the `--dry-run` flag under the `generate` command |
| `docs/features_roadmap.md` | Mark feature 2 as implemented |

No changes to `etr.py`, `config.py`, `fetch.py`, or plugin files are needed.

---

## 1. `src/colusa/cli.py` — Add `--dry-run` flag

### 1a. Add flag to the `generate` subparser

```python
generate_parser.add_argument(
    '--dry-run', action='store_true',
    help='Print what would be done without downloading or writing any files'
)
```

### 1b. Update the `generate` handler

```python
def generate(args: argparse.Namespace) -> None:
    try:
        if args.dry_run:
            Colusa.dry_run_book(args.input)
        else:
            Colusa.generate_book(args.input)
    except ConfigurationError as e:
        logs.error(e)
```

---

## 2. `src/colusa/colusa.py` — Core implementation

### 2a. Two module-level resolver helpers (above the `Colusa` class)

These do URL pattern matching against the registered plugin dictionaries without
instantiating any extractor or transformer:

```python
def _resolve_extractor(url_path: str) -> tuple[str, str]:
    """Return (class_name, kind) for the extractor that would handle url_path.
    kind is 'plugin' or 'base'.
    """
    import re
    for _, ext in etr.get_registered_extractors().items():
        if re.search(ext['pattern'], url_path):
            return ext['cls'].__name__, 'plugin'
    return 'Extractor', 'base'


def _resolve_transformer(url_path: str) -> tuple[str, str]:
    """Return (class_name, kind) for the transformer that would handle url_path.
    kind is 'plugin' or 'base'.
    """
    import re
    for _, trf in etr.get_registered_transformers().items():
        if re.search(trf['pattern'], url_path):
            return trf['cls'].__name__, 'plugin'
    return 'Transformer', 'base'
```

### 2b. `Colusa.dry_run_book()` classmethod

```python
@classmethod
def dry_run_book(cls, config_file_path: str) -> None:
    """Print dispatch plan without downloading or writing any files."""
    configs = cls._read_configuration_file(config_file_path)
    config_dir = str(pathlib.Path(config_file_path).parent)
    with Colusa(configs, config_file_dir=config_dir) as s:
        s.dry_run(config_file_path)
```

### 2c. `Colusa.dry_run()` instance method

```python
def dry_run(self, config_file_path: str = '') -> None:
    """Print a per-URL dispatch summary. No I/O side-effects."""
    # Collect all (entry, part_title) pairs in order
    all_entries: list[tuple[UrlEntry, Optional[str]]] = []
    if self.config.multi_part:
        for part in self.config.parts:
            for entry in part.urls:
                all_entries.append((entry, part.title))
    else:
        for entry in self.config.urls:
            all_entries.append((entry, None))

    print(f'[dry-run] Config: {config_file_path or ""}')
    print(f'[dry-run] Output dir: {self.config.output_dir}')
    print(f'[dry-run] Total URLs: {len(all_entries)}')

    for i, (entry, part_title) in enumerate(all_entries, 1):
        url_path = entry.path
        print(f'\n[{i}/{len(all_entries)}] {url_path}')

        if part_title:
            print(f'      Part       : {part_title}')

        if self._is_local_path(url_path):
            suffix = pathlib.PurePath(url_path).suffix.lower()
            if suffix in ('.adoc', '.asciidoc'):
                print(f'      Type       : local AsciiDoc (passthrough)')
            else:
                print(f'      Type       : local HTML')
                ext_name, ext_kind = _resolve_extractor(url_path)
                trf_name, trf_kind = _resolve_transformer(url_path)
                print(f'      Extractor  : {ext_name} ({ext_kind})')
                print(f'      Transformer: {trf_name} ({trf_kind})')
        else:
            rule = self._match_site_rule(url_path)
            if rule:
                print(f'      Extractor  : DynamicExtractor (rule: {rule.pattern})')
                print(f'      Transformer: Transformer (base)')
            else:
                ext_name, ext_kind = _resolve_extractor(url_path)
                trf_name, trf_kind = _resolve_transformer(url_path)
                print(f'      Extractor  : {ext_name} ({ext_kind})')
                print(f'      Transformer: {trf_name} ({trf_kind})')

        # Show per-entry metadata overrides if any are set
        overrides = {k: v for k, v in [
            ('title', entry.title), ('author', entry.author), ('published', entry.published)
        ] if v}
        if overrides:
            override_str = ', '.join(f'{k}="{v}"' for k, v in overrides.items())
            print(f'      Overrides  : {override_str}')
```

---

## 3. Tests — `tests/test_dry_run.py`

All tests capture stdout with `unittest.mock.patch('builtins.print')` or
`io.StringIO` via `contextlib.redirect_stdout`.

| Test | Description |
|------|-------------|
| `test_dry_run_shows_header` | Output starts with `[dry-run] Config:`, `Output dir:`, `Total URLs:` |
| `test_dry_run_base_extractor` | Unknown URL shows `Extractor (base)` / `Transformer (base)` |
| `test_dry_run_plugin_extractor` | staffeng.com URL shows `StaffEng (plugin)` |
| `test_dry_run_dynamic_rule` | URL matching a `site_rules` entry shows `DynamicExtractor (rule: ...)` |
| `test_dry_run_local_asciidoc` | `.adoc` path shows `local AsciiDoc (passthrough)` |
| `test_dry_run_local_html` | Local `.html` path shows `local HTML` with extractor/transformer lines |
| `test_dry_run_multipart_shows_part` | Multi-part config shows `Part:` label for each URL |
| `test_dry_run_metadata_overrides` | Entry with title/author set shows `Overrides:` line |
| `test_dry_run_no_files_written` | After dry_run, output_dir is not created |
| `test_dry_run_no_download` | `Downloader.download_url` is never called |
| `test_dry_run_exits_0` | Exits with code 0 on success |
| `test_dry_run_exits_1_on_bad_config` | Missing config file exits with code 1 |

---

## 4. `README.md` — Document `--dry-run`

In the **Generate ebook content** section, add a note after the `colusa generate` example:

```markdown
Use `--dry-run` to preview which extractor and transformer would be selected for each URL,
without downloading anything:

```bash
$ colusa generate new_ebook.json --dry-run
```
```

---

## 5. `docs/features_roadmap.md` — Mark feature 2 as implemented

```markdown
**2. ~~`--dry-run` flag for `generate`~~ ✅ Implemented**
```

---

## Verification

1. `pytest tests/test_dry_run.py --no-cov` — all new tests pass.
2. `pytest --no-cov` — all existing tests pass.
3. Manual smoke test:
   ```sh
   colusa generate mybook.json --dry-run
   # Verify output printed, no files created in output_dir
   colusa generate mybook.json
   # Verify normal run still works
   ```
