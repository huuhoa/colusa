# Spec: `colusa add-url` Command

## Overview

Add a `colusa add-url` CLI subcommand that appends a URL (or local file path) to an existing
config file. Optionally fetches the page title automatically. Reduces friction for users who
build up a book config incrementally.

---

## CLI Syntax

```
colusa add-url <config> <url> [options]
```

| Argument / Option | Description |
|-------------------|-------------|
| `config` | Path to an existing JSON or YAML config file |
| `url` | URL or local file path to add |
| `--title TEXT` | Override the article title |
| `--author TEXT` | Override the article author |
| `--published TEXT` | Override the publication date |
| `--part TEXT` | For multi-part books: title of the part to add the URL to |
| `--fetch-title` | Download the page and auto-extract its `<title>` or `<h1>` |

---

## Behaviour

### Entry format

- If **no metadata** flags are supplied (and `--fetch-title` is not used), the entry is written
  as a **plain string**:
  ```json
  "https://example.com/article"
  ```
- If **any metadata** is present (from flags or `--fetch-title`), the entry is written as a
  **dict**:
  ```json
  {"path": "https://example.com/article", "title": "My Article", "author": "Jane"}
  ```
  Null/empty fields are omitted from the written dict.

### Config file format

The format (JSON / YAML) is inferred from the file extension (`.json` → JSON, `.yml` / `.yaml`
→ YAML). The file is loaded as raw data, the new entry appended, and the file written back —
preserving the existing structure. YAML files are written with `default_flow_style=False`.

### Single-part books (`multi_part: false` or absent)

The entry is appended to the top-level `urls` list.

### Multi-part books (`multi_part: true`)

- If `--part <title>` is supplied, the entry is appended to the `urls` list of the matching
  part. Matching is case-insensitive. If no part with that title exists, the command exits with
  an error.
- If `--part` is **not** supplied, the command prints the list of available parts and exits with
  an error asking the user to specify one.

### Duplicate detection

Before appending, the command checks whether the URL/path is already present anywhere in the
config (top-level `urls` and all `parts[].urls`). If a duplicate is found:
- A warning is printed to stderr: `[warn] URL already exists in config: <url>`
- The command exits with code 0 without modifying the file.

### `--fetch-title`

1. Downloads the page using the existing `Downloader` (respects cache in the config's
   `output_dir`, falling back to a temp directory if `output_dir` is not set).
2. Parses the HTML with BeautifulSoup.
3. Resolves the title in order:
   - `<meta property="og:title">` content
   - `<title>` tag text (stripped)
   - First `<h1>` tag text
   - If none found: no title is set.
4. The resolved title can be overridden by a simultaneous `--title` flag.

### Errors

| Situation | Exit code | Message |
|-----------|-----------|---------|
| Config file not found | 1 | `[error] Config file not found: <path>` |
| Multi-part book, `--part` missing | 1 | `[error] This is a multi-part book. Use --part <title> to specify a part. Available parts: …` |
| Multi-part book, `--part` not found | 1 | `[error] Part not found: "<title>". Available parts: …` |
| Network error during `--fetch-title` | 0 (warn) | `[warn] Could not fetch title for <url>: <reason>` — entry is still added without a title |
| Unsupported file extension | 1 | `[error] Unsupported config format: <ext>. Use .json, .yml, or .yaml` |

---

## Example Session

```sh
# Minimal — plain string entry
$ colusa add-url mybook.json https://staffeng.com/guides/overview
[info] Added: https://staffeng.com/guides/overview

# With auto-fetched title
$ colusa add-url mybook.json https://staffeng.com/guides/overview --fetch-title
[info] Fetched title: "Overview - StaffEng"
[info] Added: https://staffeng.com/guides/overview

# With explicit metadata
$ colusa add-url mybook.yaml https://example.com/post --title "My Post" --author "Jane"
[info] Added: https://example.com/post

# Multi-part book
$ colusa add-url multipart.json https://example.com/intro --part "Chapter 1"
[info] Added to part "Chapter 1": https://example.com/intro

# Duplicate
$ colusa add-url mybook.json https://staffeng.com/guides/overview
[warn] URL already exists in config: https://staffeng.com/guides/overview
```

---

## Non-Goals

- Creating a new config file (use `colusa init` for that).
- Removing or reordering URLs.
- Editing existing URL entries.
