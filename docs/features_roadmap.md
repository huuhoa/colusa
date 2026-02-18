# Features Roadmap

> Created: 2026-02-18

## User Experience

**1. Progress reporting**
`generate` is silent while running — add a simple `[1/42] Downloading …` counter. Long books feel like they hang.

**2. `--dry-run` flag for `generate`**
Print which URLs would be fetched and which extractor/transformer would be selected, without downloading anything. Useful for debugging configs.

**3. ~~`colusa add-url <config> <url>`~~ ✅ Implemented**
CLI command to append a URL to an existing config file, optionally fetching the page title automatically. Faster than hand-editing JSON/YAML.

---

## Download Reliability

**4. Retry with backoff**
Currently a failed download is fatal. Add configurable retry attempts with exponential backoff in `Downloader`. Sites that rate-limit would succeed on retry.

**5. Rate limiting**
Add a configurable `delay` (seconds) between requests in `Downloader`. Polite for servers; also helps avoid bot-detection.

**6. Stale cache invalidation**
Add a `--refresh` flag (or `max_age_days` config field) to re-download URLs whose cached HTML is older than N days, rather than always using the cache.

---

## Output Formats

**7. Markdown output**
Add a `MarkdownVisitor` alongside `AsciidocVisitor`. Many users prefer Markdown for Obsidian/Notion/static-site imports. The visitor pattern already makes this a clean addition.

**8. Direct EPUB/HTML output**
Shell out to `asciidoctor` if it's on PATH (or use a Python library like `ebooklib`) so users get a finished `.epub` without a separate build step.

---

## Input Sources

**9. RSS/Atom feed support**
`colusa crawl --feed <url>` — parse a feed and emit all article URLs. Natural extension of the existing `crawl` command (which today is hardcoded to a `<table id="chapters">` selector).

**10. Sitemap support**
`colusa crawl --sitemap <url>` — parse a `sitemap.xml` to discover article URLs. Useful for archiving entire blogs.

---

## Developer / Plugin Experience

**11. `colusa validate <config>`**
Parse the config, resolve which extractor/transformer each URL would use, and report any URLs with no matching plugin — without downloading anything.

**12. Plugin scaffold generator**
`colusa new-plugin <domain>` — generate a skeleton `etr_<domain>.py` file with the correct decorators and stub methods, lowering the barrier to adding new sites.
