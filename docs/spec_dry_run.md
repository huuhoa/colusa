# Spec: `--dry-run` Flag for `generate`

## Overview

Add a `--dry-run` flag to `colusa generate` that prints a human-readable summary of what
would happen — which URLs would be fetched, which extractor and transformer would be selected
for each — without downloading anything, writing any files, or creating the output directory.

Useful for debugging configs, verifying plugin dispatch, and checking that site rules match
the intended URLs before committing to a full run.

---

## CLI Syntax

```
colusa generate <config> --dry-run
```

The flag has no value; it is a boolean switch.

---

## Output Format

```
[dry-run] Config: mybook.json
[dry-run] Output dir: output/
[dry-run] Total URLs: 5

[1/5] https://staffeng.com/guides/overview
      Extractor  : StaffEng (plugin)
      Transformer: StaffEng (plugin)

[2/5] https://medium.com/@user/some-article
      Extractor  : Medium (plugin)
      Transformer: Transformer (base)

[3/5] https://unknown-site.com/article
      Extractor  : Extractor (base)
      Transformer: Transformer (base)

[4/5] https://example.com/article
      Extractor  : DynamicExtractor (rule: //example.com)
      Transformer: Transformer (base)

[5/5] /home/user/notes.adoc
      Type       : local AsciiDoc (passthrough)
```

### Multi-part books

For multi-part books each URL also shows its part:

```
[1/8] https://example.com/intro
      Part       : Chapter 1
      Extractor  : Extractor (base)
      Transformer: Transformer (base)
```

### Metadata overrides

If a URL entry has metadata overrides set (via `title`, `author`, or `published` in the
config), they are shown beneath the extractor/transformer lines:

```
[2/8] https://example.com/post
      Extractor  : Extractor (base)
      Transformer: Transformer (base)
      Overrides  : title="Custom Title", author="Jane"
```

---

## Dispatch Resolution Rules

The dry-run resolves each URL using the same priority order as a real run:

1. **Local AsciiDoc** (path ends with `.adoc` / `.asciidoc` and is not a URL) → `local AsciiDoc (passthrough)`
2. **Local HTML** (non-URL path, other extension) → resolves extractor/transformer as normal
3. **Dynamic site rule** (first matching `site_rules` / `site_rules_file` entry) → `DynamicExtractor (rule: <pattern>)`
4. **Plugin** (first matching registered extractor/transformer) → `<ClassName> (plugin)`
5. **Base** (no match) → `Extractor (base)` / `Transformer (base)`

Extractor and transformer are resolved independently, so one can be a plugin while the other
falls back to base.

---

## Side Effects

A dry-run **must not**:
- Download any URLs
- Read cached HTML files
- Create the output directory or any subdirectories
- Write any `.asciidoc`, `Makefile`, or image files

A dry-run **may**:
- Load and parse the config file
- Load plugins (`utils.scan`)
- Load dynamic site rules (reads the rules file from disk if `site_rules_file` is set)

---

## Exit Codes

| Situation | Exit code |
|-----------|-----------|
| Dry-run completes successfully | 0 |
| Config file cannot be parsed | 1 |
| Config file not found | 1 |

A dry-run never exits 1 due to URL-level issues (missing content, bad URLs) — it only
resolves dispatch, it does not fetch pages.

---

## Non-Goals

- Validating that URLs are reachable.
- Checking whether cached HTML already exists.
- Showing estimated download size or time.
