# Feature Research: Top 10 Needed Features for Web-to-Ebook Tools

> Researched: 2026-02-18
> Sources: Calibre, percollate, wallabag, Shiori, newspaper3k, readability tools,
> r/selfhosted, r/DataHoarder, r/ebooks, Hacker News, GitHub issue trackers,
> cross-referenced against colusa codebase gaps.

---

## Summary Ranking

| Rank | Feature | Ecosystem Signal | Colusa Gap Today |
|------|---------|-----------------|-----------------|
| 1 | Universal CSS-selector extraction (no-code site rules) | Highest — every comparable tool | Partially addressed by `site_rules`; XPath and transformer overrides missing |
| 2 | Parallel downloads + rate limiting | Very high | Not implemented; sequential only |
| 3 | Progress reporting | Very high | Not implemented; silent |
| 4 | Retry with backoff + failure reporting | High | Download retry absent; extraction failure reporting added v0.17.0 |
| 5 | RSS/Atom feed + sitemap ingestion | High | `crawl` is hardcoded to one site structure |
| 6 | Markdown output format | High (developer audience) | Not implemented; architecture ready |
| 7 | Stale cache invalidation / selective refresh | Medium-high | Binary exists-or-download; no age checking |
| 8 | Paywall / cookie / session auth | Medium-high | One hardcoded Substack plugin; no general mechanism |
| 9 | Code block + technical content quality | Medium (developer audience) | `pre > code` nesting, language detection, AsciiDoc escaping gaps |
| 10 | Plugin scaffolding + `validate` command | Medium (developer experience) | No scaffolding; `--dry-run` is partial; no plugin docs |

---

## Recommended Roadmap Sequencing

**Immediate (next 1–2 releases):**
- Feature 3 (progress reporting): one afternoon of work, massively improves perceived quality
- Feature 4 (retry with backoff): `requests` supports this natively; high reliability gain for low effort
- Feature 7 (stale cache): `os.path.getmtime()` check; avoids full cache deletion frustration

**Short-term (next quarter):**
- Feature 2 (parallel downloads): `concurrent.futures.ThreadPoolExecutor` with a per-domain semaphore
- Feature 5 (RSS/Atom feed): `feedparser` library; extends existing `crawl` command cleanly
- Feature 6 (Markdown output): `MarkdownVisitor` class following existing pattern

**Medium-term (next 6 months):**
- Feature 1 (extend site rules): XPath support, transformer override fields in `SiteRule`, community rules file
- Feature 8 (generic auth): `cookies_file` config field; document `Fetch` subclass API
- Feature 9 (code block quality): audit all `visit_tag_pre/code` paths; AsciiDoc escape passthrough
- Feature 10 (plugin tooling): `colusa validate` and `colusa new-plugin` commands

---

## Detailed Findings

### 1. Universal Content Extraction Without Site-Specific Code

**Why:** The fundamental frustration is that a tool works for 30 websites but fails silently on the 31st. Users want to express "the article body is in this CSS selector" without writing Python or filing issues.

**What they ask for:**
- CSS selector config without touching code (partially done via `site_rules`)
- XPath support (explicitly out of scope in current spec — a gap)
- Automatic CSS-selector suggestion via HTML inspection
- Community-maintained site rule repositories (a "recipe" hub like Calibre's)

**Colusa evidence:** 37 plugin files each represent a prior extraction failure. `DynamicExtractor` and `site_rules` were the direct response to this pain.

---

### 2. Parallel / Concurrent Downloads with Rate Limiting

**Why:** A 100-article book at 2s per download is a 3+ minute sequential wait. Users building engineering blog compilations regularly process 50–150 URLs.

**What they ask for:**
- `--concurrency N` flag
- Per-domain rate limiting (not just a global delay)
- Exponential backoff on transient failures
- Async/await download layer

**Colusa evidence:** `_generate_book_single_part()` is a plain `for` loop; `Downloader` has no thread pool, no asyncio, no semaphore.

---

### 3. Progress Reporting During Long Runs

**Why:** "Tool hangs with no output for 5 minutes" appears in percollate, monolith, httrack issue trackers. Users cannot distinguish "working" from "hung on a bad URL."

**What they ask for:**
- `[1/42] Fetching https://...` per-URL progress line
- Elapsed time estimate
- `--quiet` flag for piping
- Optional rich/tqdm progress bar

**Colusa evidence:** `generate()` calls `ebook_generate_content()` in a loop with zero stdout output.

---

### 4. Retry Logic and Graceful Failure Handling

**Why:** A single 503 or timeout should not require a manual full re-run. Users want transient failures retried automatically.

**What they ask for:**
- `retry_count: 3` and `retry_delay: 2` config fields
- Exponential backoff (1s, 2s, 4s)
- Distinguish permanent (404) vs transient (503, timeout) — no retry on 404
- Per-URL failure log written to disk for selective re-run

**Colusa evidence:** `download_url()` has zero retry logic. The v0.17.0 collect-and-report only covers extraction failures, not download failures.

---

### 5. RSS/Atom Feed and Sitemap Ingestion

**Why:** The primary use case for many users is "follow a blog and compile it periodically into an ebook." Manual URL curation is tedious. Calibre's entire news recipe system is built around this.

**Especially needed for:** Substack newsletters (Atom feeds), tech blogs with sitemaps, Wikipedia series, serialised fiction (RoyalRoad).

**What they ask for:**
- `colusa crawl --feed <url>` emitting a URL list
- Date-range filtering (`--from 2024-01-01 --to 2024-12-31`)
- `colusa crawl --sitemap <url>` with `--filter-pattern`
- Auto-detection of feed URL from homepage (`<link rel="alternate">`)

**Colusa evidence:** `Crawler.run()` is hardcoded to `table#chapters` — only works for Vietnamese fiction sites (truyenfull structure).

---

### 6. Markdown Output Format

**Why:** AsciiDoc is niche. Obsidian, Notion, Logseq, Roam, Bear, Foam, Hugo, Jekyll, Eleventy, Astro all use Markdown. Percollate's most-starred enhancement request is Markdown export.

**What they ask for:**
- `colusa generate mybook.json --output-format markdown` producing `.md` files
- CommonMark-compliant output
- YAML frontmatter with title/author/published/url per file
- Flat directory of per-article `.md` files for Obsidian vaults

**Colusa evidence:** `NodeVisitor` + `AsciidocVisitor` pattern is architected for exactly this extension — a `MarkdownVisitor` class requires no structural changes.

---

### 7. Stale Cache Invalidation / Selective Refresh

**Why:** The cache is binary: file exists → use it, file missing → download. Users updating a living book must delete the entire `.cached/` directory to refresh anything.

**What they ask for:**
- `--refresh` flag (force re-download all)
- `--refresh-url <url>` (force one URL)
- `max_age_days: 7` config field
- ETag/Last-Modified conditional requests

**Colusa evidence:** `download_content()` is `if not cached_file_path.exists(): download(...)` — zero age checking.

---

### 8. Paywall / Cookie / Session Authentication

**Why:** Significant high-quality content (Pragmatic Engineer, HBR, Stratechery, Medium members) is behind soft or hard paywalls. Without auth, these URLs silently return paywall HTML.

**What they ask for:**
- `cookies_file` config field accepting Netscape-format cookie files (wget/curl-style)
- Generic per-domain request header injection (`Cookie:`, `Authorization:`)
- Documentation for writing a `Fetch` subclass for new paywalled sites

**Colusa evidence:** `etr_pragmatic_engineer.py` is a 180-line Substack login/cookie implementation hardcoded to one newsletter. The `register_fetch` decorator supports per-site fetcher plugins but is undocumented.

---

### 9. Code Block and Technical Content Rendering Quality

**Why:** Technical blogs are the primary colusa use case. Poor code block rendering (missing language hints, double-wrapping, AsciiDoc special character escaping) makes the ebook unusable.

**Specific gaps in colusa:**
- `visit_tag_pre()` wraps in `[listing]\n....\n` regardless of `<code>` child — `pre > code` nesting (GitHub-style) produces double-wrapped listings
- Language detection reads `language-{lang}` CSS class — fails for sites with custom class names or no class
- `visit_tag_h5` / `visit_tag_h6` use `**bold**` instead of heading markers
- AsciiDoc special characters (`+`, `=`, `[`) inside code blocks cause rendering errors

**What they ask for:**
- Correct `[source, python]` annotations on fenced code blocks
- Proper handling of `<pre><code class="language-python">` nesting
- AsciiDoc passthrough blocks for content with special characters

---

### 10. Plugin Scaffolding and `validate` Command

**Why:** The plugin system is colusa's biggest strength but the barrier to writing a new plugin is high — only documentation is "read existing files." Every new site still requires understanding BeautifulSoup, the `Extractor` template-method contract, `NodeVisitor` dispatch, and decorator registration.

**What they ask for:**
- `colusa validate mybook.json` — table showing URL | extractor | transformer | status; flags URLs with no matching plugin
- `colusa new-plugin medium.com` — generates starter `etr_medium.py` with all stubs
- Public plugin API documentation (docstrings on `Extractor`, `Transformer`, `NodeVisitor`)
- `colusa test-plugin etr_mystuff.py --url https://example.com/article`

**Colusa evidence:** `--dry-run` partially addresses dispatch inspection but does not flag unmatched URLs. `tech_debts.md` lists "No documented API contract for creating plugins" as open debt.
