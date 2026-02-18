# Spec: Dynamic Site Parsing Configuration

## Problem

Currently, colusa only supports new websites by adding a Python plugin file to the source tree. Users facing an unsupported site must wait for the colusa author to write and release a plugin. There is no way for a user to configure content parsing for a new site without modifying colusa's source code.

## Goal

Allow users to define CSS-selector-based parsing rules directly in their book config (or a separate rules file), without writing or installing any Python code. Dynamic rules take priority over built-in plugins.

---

## User-Facing Behaviour

A new optional `site_rules` list in the book config and/or a `site_rules_file` reference lets users declare per-domain parsing rules.

### Inline in book config

```json
{
  "title": "My Book",
  "urls": ["https://example.com/article"],
  "site_rules": [
    {
      "pattern": "//example.com",
      "content": "article.post-body",
      "title": "h1.article-title",
      "author": ".author-name",
      "published": "time.publish-date",
      "cleanup": ["div.ads", "nav.sidebar"]
    }
  ]
}
```

### Via external rules file

```json
{
  "site_rules_file": "./my-sites.yml"
}
```

`my-sites.yml`:
```yaml
- pattern: "//example.com"
  content: "article.post-body"
  title: "h1.article-title"
  author: ".author-name"
  published: "time.publish-date"
  cleanup:
    - "div.ads"
    - "nav.sidebar"
```

Both can be combined; inline rules are evaluated first, then rules from the file.

---

## Rule Fields

| Field | Required | Description |
|-------|----------|-------------|
| `pattern` | Yes | Regex matched against the full URL (e.g. `//example.com`). Same convention as built-in plugin patterns. |
| `content` | No | CSS selector for the article body. If omitted or selector finds nothing, falls back to built-in detection. |
| `title` | No | CSS selector for the article title. Falls back to built-in defaults if not set or not found. |
| `author` | No | CSS selector for the author name. Falls back to built-in defaults if not set or not found. |
| `published` | No | CSS selector for the published date. Falls back to built-in defaults if not set or not found. |
| `cleanup` | No | List of CSS selectors — all matching elements are removed from the extracted content before transformation. |

---

## Behaviour Details

- **Matching**: rules are checked in order; the first rule whose `pattern` matches the URL is used.
- **Priority**: dynamic rules are evaluated before built-in plugins. If a rule matches, the plugin registry is not consulted.
- **Fallback**: each field (`content`, `title`, `author`, `published`) independently falls back to built-in logic if the CSS selector is absent or finds no element.
- **External file path**: relative paths in `site_rules_file` are resolved relative to the directory containing the book config file.
- **Backward compat**: configs without `site_rules` or `site_rules_file` continue to work unchanged.

---

## Out of Scope

- Transformer/AsciiDoc generation overrides (tag-level HTML→AsciiDoc customisation) — this spec covers extraction only.
- XPath selectors — CSS only.
- Per-URL rule overrides — rules are per-domain (pattern-matched).
