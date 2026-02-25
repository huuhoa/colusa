# Changelog


## v0.19.1 (2026-02-25)

### Fix

* Convert PR references to explicit Markdown links in changelog [#253](https://github.com/huuhoa/colusa/pull/253) [Huu Hoa NGUYEN]

  Adds a ReSub to subject_process that rewrites (#N) to
  [#N](https://github.com/huuhoa/colusa/pull/N) so PR links are
  explicit hyperlinks rather than relying on GitHub auto-linking.


## v0.19.0 (2026-02-25)

### Changes

* Bump version to 0.19.0 [#252](https://github.com/huuhoa/colusa/pull/252) [Huu Hoa NGUYEN]

### Fix

* Create temp tag before gitchangelog in release skill [#251](https://github.com/huuhoa/colusa/pull/251) [Huu Hoa NGUYEN]

  gitchangelog needs the tag to exist to group commits under the new
  version. Create a local tag before running it, then delete it so it
  can be re-created on the correct squash-merge commit on main.


## v0.18.0 (2026-02-25)

### New

* Add feature research report for web-to-ebook tools [#249](https://github.com/huuhoa/colusa/pull/249) [Huu Hoa NGUYEN]

  Top 10 features ranked by cross-source frequency across Calibre,
  percollate, wallabag, Shiori, newspaper3k and community discussions.
  Includes sequencing recommendations and detailed colusa-specific evidence.

* Add direct epub/html/pdf output via asciidoctor [#247](https://github.com/huuhoa/colusa/pull/247) [Huu Hoa NGUYEN]

  Adds --build flag to generate and a standalone build subcommand that
  shell out to asciidoctor, asciidoctor-epub3, and asciidoctor-pdf.
  Tool presence checked via shutil.which with helpful install URLs on
  error. All formats attempted before failing; extra make params from
  config passed through as-is.

* Add spec and plan docs for add-url and dry-run features [#246](https://github.com/huuhoa/colusa/pull/246) [Huu Hoa NGUYEN]

* Add --dry-run flag to colusa generate [#245](https://github.com/huuhoa/colusa/pull/245) [Huu Hoa NGUYEN]

  Adds `colusa generate <config> --dry-run` that prints a per-URL dispatch
  summary (extractor, transformer, dynamic rule, local file type, metadata
  overrides) without downloading, writing, or creating any files.

* Add colusa add-url command [#244](https://github.com/huuhoa/colusa/pull/244) [Huu Hoa NGUYEN]

  Adds `colusa add-url <config> <url>` CLI subcommand that appends a URL
  to an existing JSON or YAML config file. Supports:
  - Auto title fetching via --fetch-title (og:title, <title>, <h1>)
  - Explicit metadata overrides (--title, --author, --published)
  - Multi-part books via --part <title> (case-insensitive)
  - Duplicate detection with warning
  - Plain string entry when no metadata, dict entry when metadata present

* Add features roadmap [#243](https://github.com/huuhoa/colusa/pull/243) [Huu Hoa NGUYEN]

* Add release-next-version Claude Code command [#242](https://github.com/huuhoa/colusa/pull/242) [Huu Hoa NGUYEN]

### Fix

* Use shlex.split for extra build params to handle quoted values [#248](https://github.com/huuhoa/colusa/pull/248) [Huu Hoa NGUYEN]

  Simple .split() broke params containing quoted strings with spaces,
  e.g. pdf-page-margin="[0.15in, 0.17in, 0.40in, 0.17in]". shlex.split
  handles shell quoting correctly, keeping such values as single tokens.

### Other

* Release: v0.18.0 [#250](https://github.com/huuhoa/colusa/pull/250) [Huu Hoa NGUYEN]

  * improve: enhance CLI help text and exit code consistency for AI invocation

  - Add top-level description and workflow epilog to main parser
  - Add per-subcommand descriptions and examples to all subcommands
  - Use RawDescriptionHelpFormatter for clean multi-line help rendering
  - Change crawl url from --url flag to positional argument
  - Rename --output_dir to --output-dir for CLI convention consistency
  - Fix exit codes: init, generate, crawl now raise SystemExit(1) on error


## v0.17.0 (2026-02-18)

### Changes

* Bump version to 0.17.0 and update changelog [#241](https://github.com/huuhoa/colusa/pull/241) [Huu Hoa NGUYEN]

  * chg: bump version to 0.17.0

  * chg: doc: update changelog for v0.17.0

* Regenerate changelog for unreleased changes [#239](https://github.com/huuhoa/colusa/pull/239) [Huu Hoa NGUYEN]

  Includes PRs #235–#238: high-severity debt fixes, cleanup, test
  coverage expansion, and tech debt assessment updates.

### Fix

* Suppress UNKNOWN Node Type warning for HTML comment nodes [#240](https://github.com/huuhoa/colusa/pull/240) [Huu Hoa NGUYEN]

  BeautifulSoup represents HTML comments as Comment objects, which are
  NavigableString subclasses. The visitor's get_visitor() used an exact
  type check (type(node) is NavigableString), so Comment fell through to
  visit_unknown() and produced a spurious [WARN] UNKNOWN Node Type: Comment
  on every HTML comment encountered during extraction.

  Add an isinstance(node, NavigableString) branch between the exact-type
  check and the Tag branch to silently return an empty string for all
  non-text NavigableString subclasses (Comment, Script, Stylesheet, CData,
  Doctype, etc.). Plain NavigableString text nodes are unaffected because
  the exact-type check runs first.

  Add tests/test_visitor.py to verify comment nodes produce no output and
  no UNKNOWN Node Type warning.

* PR A debt cleanup — prints, dead code, torpy, Python floor, to_dict [#236](https://github.com/huuhoa/colusa/pull/236) [Huu Hoa NGUYEN]

  * docs: update tech debt assessment after PR #235

  Mark all 10 high-severity items as resolved (type safety ×3, error
  handling ×3, test coverage ×2 fully + ×1 partially). Update summary
  totals (HIGH 10→2, total 51→43) and reprioritise remaining work.

  Co-Authored-By: Claude Sonnet 4.6 <noreply@anthropic.com>

  * docs: add plan for remaining technical debt fixes

  Two-PR plan covering:
  - PR A: debug print removal, dead code, torpy→optional, Python floor >=3.9,
    BookConfig.to_dict() UrlEntry serialisation, DownloaderConfig removal
  - PR B: download failure tests, post-processor tests, representative
    per-plugin extraction tests

  Co-Authored-By: Claude Sonnet 4.6 <noreply@anthropic.com>

  * fix: PR A debt cleanup — prints, dead code, torpy, Python floor, to_dict

  - etr.py: remove live print('PRE ====') and two commented-out prints
  - fetch.py: remove commented-out dead code in get_fetch_instance() and
    download_image()
  - config.py: fix BookConfig.to_dict() to serialise UrlEntry objects in
    urls and parts[].urls as dicts instead of raw objects; remove unused
    empty DownloaderConfig dataclass
  - pyproject.toml: move torpy to optional [tor] extra (not used in source);
    bump requires-python to >=3.9 (code uses 3.9+ syntax throughout);
    remove Python 3.8 classifier

* Resolve all high-severity technical debts [#235](https://github.com/huuhoa/colusa/pull/235) [Huu Hoa NGUYEN]

  * docs: add technical debt assessment

  Co-Authored-By: Claude Sonnet 4.6 <noreply@anthropic.com>

  * fix: resolve all high-severity technical debts

  - Fix Optional type annotations in etr.py (create_extractor, Extractor.__init__)
  - Add get_registered_extractors/get_registered_transformers public accessors
  - Fix mutable default arguments in Fetch.__init__ and Downloader.__init__
  - Narrow broad except Exception to specific types in download_image()
  - Fix silent except Exception: pass in _process_local_asciidoc()
  - Collect ContentNotFoundError failures and report summary at end of generate(),
    exiting with code 1 if any URLs failed (per user decision)
  - Add tests/test_plugin_registry.py smoke tests for plugin registration dispatch
  - Update CLAUDE.md to document local .venv/ usage

### Other

* Docs: update tech debt assessment after PRs #236 and #237 [#238](https://github.com/huuhoa/colusa/pull/238) [Huu Hoa NGUYEN]

  PR #236 (cleanup): mark debug prints, dead code, DownloaderConfig,
  BookConfig.to_dict(), torpy, Python floor all as resolved.

  PR #237 (test coverage): mark all four HIGH test-coverage items as
  resolved (download failures, post-processor, plugin dispatch,
  plugin extraction).

  Summary: HIGH 2→0, MEDIUM 33→23, LOW 8→5, total 43→28.
  Reprioritise remaining work.

* Test: PR B — download failures, post-processor, plugin extraction [#237](https://github.com/huuhoa/colusa/pull/237) [Huu Hoa NGUYEN]

  Close remaining HIGH test-coverage gaps identified in tech_debts.md:

  tests/test_downloader.py (9 tests):
  - Downloader.download_url(): non-200 writes .temp file with response body;
    200 calls shutil.copyfileobj and sets decode_content on raw stream
  - download_image(): ConnectionError and Timeout do not propagate;
    cached image skips download; returns filename with correct extension

  tests/test_postprocessor.py (8 tests):
  - PostProcessor base: run() is a no-op; file_path and params stored correctly
  - create_postprocessor(): raises PostProcessorNotFoundError for unknown names
    with correct message format; registered processor is instantiated with
    correct file_path and params

  tests/test_plugin_extraction.py (12 tests):
  - StaffEng: dispatches correctly; finds blog-post-content div; returns None
    when div absent
  - Medium: dispatches correctly; finds article tag; parses title from h1 or
    og:title meta; returns None when no article tag
  - Wikipedia: dispatches correctly; finds bodyContent div; parses title from
    firstHeading h1; returns None when bodyContent absent


## v0.16.0 (2026-02-18)

### New

* Dynamic site parsing rules via CSS selectors [#232](https://github.com/huuhoa/colusa/pull/232) [Huu Hoa NGUYEN]

  * feat: dynamic site parsing rules via CSS selectors in book config

  Allow users to define per-domain content-extraction rules directly in
  their book config (or an external YAML/JSON file) using CSS selectors,
  without writing a Python plugin. Dynamic rules take priority over
  built-in plugins.

  - Add `SiteRule` dataclass and `_parse_site_rule()` to config.py
  - Add `site_rules` and `site_rules_file` fields to `BookConfig`
  - Add `DynamicExtractor` to etr.py driven by `SiteRule` selectors
  - Update `Colusa` to load rules from config and external file, match
    them before the plugin registry in `ebook_generate_content`
  - Add spec and plan docs for the feature

  Co-Authored-By: Claude Sonnet 4.6 <noreply@anthropic.com>

  * test: add tests for dynamic site parsing rules

  28 tests covering:
  - SiteRule dataclass and _parse_site_rule() parsing (minimal, full, defaults)
  - BookConfig.from_dict() with site_rules and site_rules_file fields
  - DynamicExtractor: content/title/author/published selectors with match,
    no-match fallback, and absent-selector fallback
  - DynamicExtractor cleanup: single selector, multiple selectors, empty
    list, selector matching nothing
  - Colusa._match_site_rule(): first-match, no-match, no-rules cases
  - Colusa rule loading: JSON file, YAML file, inline+file merge
  - Priority: dynamic rules bypass create_extractor() plugin registry

* Local content support for HTML and AsciiDoc files [#231](https://github.com/huuhoa/colusa/pull/231) [Huu Hoa NGUYEN]

  * chg: add local content support for HTML and AsciiDoc files

  Allow urls/parts[].urls entries to be local file paths (as plain strings
  or dicts with path + optional title/author/published overrides). Local
  .adoc/.asciidoc files are copied to output_dir and included directly
  without HTML extraction. Local HTML files go through the normal
  extractor/transformer pipeline with optional metadata overrides applied
  after parsing.

### Changes

* Bump version to 0.16.0 [#234](https://github.com/huuhoa/colusa/pull/234) [Huu Hoa NGUYEN]

* Add extractor for federicopereiro.com and update CLAUDE.md [#230](https://github.com/huuhoa/colusa/pull/230) [Huu Hoa NGUYEN]

  * chg: add extractor for federicopereiro.com and fix element removal

  - Add site-specific extractor for federicopereiro.com
  - Fix Extractor.remove_tag to use decompose() instead of extract(),
    and correct the None guard logic

  Co-Authored-By: Claude Sonnet 4.6 <noreply@anthropic.com>

  * chg: note git workflow in CLAUDE.md

  Document that direct push to main is not allowed and PRs must be
  merged with squash option.

* Cache the content download from hbr.org [#227](https://github.com/huuhoa/colusa/pull/227) [Huu Hoa NGUYEN]

  So that we don't have to redownload everytime we rebuild our content

* Add some new extractors [#226](https://github.com/huuhoa/colusa/pull/226) [Huu Hoa NGUYEN]

  * chg: add some new extractors
  + seths.blog
  + stratechery.com
  + newsweek.com
  + rework on hbr.org

* Refactor code to introduce type safety [#225](https://github.com/huuhoa/colusa/pull/225) [Huu Hoa NGUYEN]

  + Add type hints
  + Use `dataclasses` for configuration objects
  + Update integration tests + golden test files

### Other

* Docs: update README with dynamic site rules and modern install [#233](https://github.com/huuhoa/colusa/pull/233) [Huu Hoa NGUYEN]

  - Replace deprecated `setup.py install` with `pip install colusa`
  - Add "Supporting Unsupported Websites" section documenting site_rules
    and site_rules_file config fields with examples for JSON and YAML
  - Add field reference table for all site rule options
  - Update supported websites section to link to the dynamic rules section

* Add CLAUDE.md with architecture guide for Claude Code [#229](https://github.com/huuhoa/colusa/pull/229) [Huu Hoa NGUYEN]

  Documents build/test commands, the extract-transform-render pipeline,
  plugin registration conventions, and how to add support for new websites.


## v0.15 (2025-12-07)

### Other

* Upgrade project settings (using pyproject.toml) [#224](https://github.com/huuhoa/colusa/pull/224) [Huu Hoa NGUYEN]

  * chg: change project build tool from setup.py to pyproject.toml
  * Bump version: 0.14.0 -> 0.15.0


## v0.14 (2025-12-07)

### Other

* Feature/release 2025 [#223](https://github.com/huuhoa/colusa/pull/223) [Huu Hoa NGUYEN]

  * Bump version: 0.12.0 → 0.14.0


## v0.14.0 (2025-12-07)

### Changes

* Bump dependencies. [Huu Hoa NGUYEN]


## v0.13.0 (2025-12-07)

### Changes

* Support download local file [#219](https://github.com/huuhoa/colusa/pull/219) [Huu Hoa NGUYEN]

  Support download local file instead of from URL
  This is for the case we want to create a book from mix set of sources, both local and remote ones.

* Allow external configuration for extractors, transformers [#202](https://github.com/huuhoa/colusa/pull/202) [Huu Hoa NGUYEN]

  This change allows end-user to specify which extractor/transformer to be used for given url.
  Previously, the url patterns are hard code into plugin (extractor/transformer). Which make it
  very hard to adapt to multiple blog sites, such as blogs from substack.

* Support multi urls in extractor, transformer [#201](https://github.com/huuhoa/colusa/pull/201) [Huu Hoa NGUYEN]

* Ability to name the generated book instead of default index.asciidoc [#200](https://github.com/huuhoa/colusa/pull/200) [Huu Hoa NGUYEN]

  Add new setting `book_file_name`, default value is `index.asciidoc` to specify file name of generated book

  Requires:

  * book_file_name ending with `.asciidoc`

  If `book_file_name` is different from `index.asciidoc` then the generated Makefile will be `basename{book_file_name}_Makefile`
  and to generate book, run command `make -f newmakefile pdf`

* Heading level for output asciidoc [#184](https://github.com/huuhoa/colusa/pull/184) [Huu Hoa NGUYEN]

* Refactor package structure and introduce Fetch for extending fetchers [#182](https://github.com/huuhoa/colusa/pull/182) [Huu Hoa NGUYEN]

  Refactor:
  + Move Colusa class to separate module colusa, previously within __init__.py
  + Move download_url and download_image from utils to fetch

  New Extension Point:
  + Introduce Fetch class which replicate the requests methods and allow inheritance
  so that plugins can implement extended functionalities if needed

### Other

* Fix setup. [Huu Hoa NGUYEN]

* Create codeql.yml [#203](https://github.com/huuhoa/colusa/pull/203) [Huu Hoa NGUYEN]

* Feature/pragmatic engineer [#183](https://github.com/huuhoa/colusa/pull/183) [Huu Hoa NGUYEN]

  * chg(plugins): update PragmaticEngineer

  Produce more clean document
  Support loading existing cookies to by pass paywall

* Feature/pragmatic engineer [#181](https://github.com/huuhoa/colusa/pull/181) [Huu Hoa NGUYEN]

  * chg(asciidoc_visitor): fix parsing srcset
  * chg(etr): change in Transformer to make it easier to extent
  * chg(plugins): add support for new site newsletter.pragmaticengineer.com
  * chg: add custom target parameters for Makefile
  * chg(plugins): remove warning from PEAsciidoctorVisitor

* Add: post processing workers [#170](https://github.com/huuhoa/colusa/pull/170) [Huu Hoa NGUYEN]

  Allow to do post processing on entire chapter content.
  Post processing can be:
  + Search and replace using regex

* Add: support lethain.com [#149](https://github.com/huuhoa/colusa/pull/149) [Huu Hoa NGUYEN]

  Cleanup article's header to make final output more clean


## v0.12.0 (2022-07-24)

### New

* Add new command to crawl an URL. [Nguyen Huu Hoa]

  Crawl an URL (website) to help generate list of URL, mostly story chapters

### Changes

* Add some debug capability. [Nguyen Huu Hoa]

* Add support for new websites. [Nguyen Huu Hoa]

### Other

* Release new version 0.12.0 [#103](https://github.com/huuhoa/colusa/pull/103) [Huu Hoa NGUYEN]

  * @minor: prepare to release 0.12.0
  * Bump version: 0.11.0 → 0.12.0

* Merge branch 'main' of github.com:huuhoa/colusa. [Nguyen Huu Hoa]

* Chg(plugins/truyenfull): clean ads content. [Nguyen Huu Hoa]

* Chg(plugins/truyenfull): clean ads content. [Nguyen Huu Hoa]


## v0.11.0 (2022-02-17)

### Changes

* Support for tangthuvien [#72](https://github.com/huuhoa/colusa/pull/72) [Huu Hoa NGUYEN]

### Fix

* Gitchangelog ignore pattern. [Nguyen Huu Hoa]


## v0.10.0 (2021-10-16)

### Changes

* Update dev requirements. [Nguyen Huu Hoa]

* Improve code coverage [#21](https://github.com/huuhoa/colusa/pull/21) [Huu Hoa NGUYEN]

  Mock up two functions download_image and download_content

  + `download_content` will return existing cached file, so that we don't have to redownload every time
  we run the test
  + `download_image` will just return True, do nothing, so that we don't have to download images

### Other

* Add: support for techtarget.com [#32](https://github.com/huuhoa/colusa/pull/32) [Huu Hoa NGUYEN]

  * chg(asciidoc_visitor): support parsing datasrc and data-srcset for img
  * add(web): support for techtarget.com


## v0.9.0 (2021-08-26)

### New

* Integration tests [#20](https://github.com/huuhoa/colusa/pull/20) [Huu Hoa NGUYEN]

  * chg: add tox.ini for running tox
  * chg(colusa): move colusa source to src folder

* Support parsing site xp123.com [#18](https://github.com/huuhoa/colusa/pull/18) [Huu Hoa NGUYEN]

### Other

* Chore: update setup.cfg for version location. [Nguyen Huu Hoa]

* Prepare for next release. [Nguyen Huu Hoa]

* Refactor(etr): Rework on Extractor [#19](https://github.com/huuhoa/colusa/pull/19) [Huu Hoa NGUYEN]

  * refactor(etr): move _parse_yoast from a plugin extract to base Extractor
  * refactor(etr): rename methods for clarification

    + rename `internal_init` to `_find_main_content`
    + rename `get_author` to field `author` and `_parse_author` for parsing value
    + rename `get_published` to field `published` and `_parse_published` for parsing value
    + rename `get_title` to field `title` and `_parse_title` for parsing value
    + add `_parse_metadata` for parsing all related metadata from html

  * refactor(etr): change signature of Extractor._find_main_content

    + `_find_main_content` is now return bs.Tag instead of setting value for field `main_content`. The change make it more clear for purpose of `_find_main_content`, i.e. only to find the main content, does not modify anything
    + `_parse_metadata` will be executed after we found the main content


## v0.8.0 (2021-08-22)

### New

* Support rendering additional book properties [#16](https://github.com/huuhoa/colusa/pull/16) [Huu Hoa NGUYEN]

  In the book configuration file, add new array `book_properties`
  with content is list of strings. Those strings will be render as
  book properties on master file (index.asciidoc)

  Example:

  ```json
  "book_properties": [
      "ifdef::backend-pdf[]",
      ":front-cover-image: image:cover.pdf[]",
      ":notitle:",
      "endif::[]",
      "ifdef::backend-epub3[]",
      ":front-cover-image: image:cover.png[]",
      "endif::[]"
  ]
  ```

  Above example will instruct asciidoctor processor to use:
  + cover.pdf as front cover image when generating pdf
  + cover.png as front cover image when generating epub3

### Changes

* Render html table as native asciidoc table [#17](https://github.com/huuhoa/colusa/pull/17) [Huu Hoa NGUYEN]

### Other

* Prepare for bump version 0.8. [Nguyen Huu Hoa]

* Add(plugins): support for scrumcrazy.wordpress.com. [Nguyen Huu Hoa]


## v0.7.0 (2021-08-20)

### Changes

* Improve article parsing [#15](https://github.com/huuhoa/colusa/pull/15) [Huu Hoa NGUYEN]

  * add: agilethought support to get article's author
  * add: support website tech.trivago.com

* Metadata rendering [#14](https://github.com/huuhoa/colusa/pull/14) [Huu Hoa NGUYEN]

  render metadata in a more clean way, the format should be

  `by **{author}** on {published_date} at {url | domain}`

### Other

* Chore: refactor project's setup configurations. [Nguyen Huu Hoa]

* Setup codeql-analysis. [Huu Hoa NGUYEN]

* Setup dependabot. [Huu Hoa NGUYEN]

* Dev: update requirements_dev.txt. [Nguyen Huu Hoa]

* Docs: update CHANGELOG. [Nguyen Huu Hoa]


## v0.6.0 (2021-08-18)

### New

* Support new website https://agilethought.com [#11](https://github.com/huuhoa/colusa/pull/11) [Huu Hoa NGUYEN]

### Changes

* Etr: improve metadata rendering for generated articles [#10](https://github.com/huuhoa/colusa/pull/10) [Huu Hoa NGUYEN]


## v0.5.1 (2021-08-14)

### Changes

* Update requirements for package and dev. [Nguyen Huu Hoa]


## v0.5.0 (2021-08-14)

### New

* Support new website https://staffeng.com. [Nguyen Huu Hoa]

### Changes

* Initial configuration for bumpversion. [Nguyen Huu Hoa]

* Add comments at the beginning of included files. [Nguyen Huu Hoa]

  new version of asciidoctor removes leading and trailing empty lines of included files
  therefore the beginning of new section in the included files will not
  be separated as expected. The work around is to add comment line
  at the very beginning of included files.

* Support for parsing some common webblogs. [Nguyen Huu Hoa]

* Support for parsing hbr.org. [Nguyen Huu Hoa]

* Support parsing content for blog-content and wikipedia. [Nguyen Huu Hoa]

* Support parsing srcset dimension with 'x' specification. [Nguyen Huu Hoa]

* Add suffix to generated file name to prevent name colliding. [Nguyen Huu Hoa]

* Support detecting webpage content inside `main` tag. [Nguyen Huu Hoa]

* Passthrough the table tag content. [Nguyen Huu Hoa]

* Special treatment for image inside an anchor tag. [Nguyen Huu Hoa]

* Cleanup code to get content class of a website. [Nguyen Huu Hoa]

* Heading level of generated asciidoc. [Nguyen Huu Hoa]

* Add support for parsing new websites. [Nguyen Huu Hoa]

  + https://cadenceworkflow.io
  + https://softwareengineeringdaily.com

### Fix

* Correct config for bumpversion. [Nguyen Huu Hoa]

* Slugify that import non existing unicode from idna. [Nguyen Huu Hoa]

* Get correct image suffix by parsing url first to get only `path` in URL. [Nguyen Huu Hoa]

### Other

* Docs: add some documents. [Nguyen Huu Hoa]

* Add: proper configuration for packaging. [Nguyen Huu Hoa]

  + add bump_version support


## v0.4.0 (2020-10-14)

### New

* Support new website https://www.infoq.com. [Nguyen Huu Hoa]

* Yaml configuration [#9](https://github.com/huuhoa/colusa/pull/9) [Huu Hoa NGUYEN]

  * feat: support configuration file in YAML format
  + Configuration file format is determined by extension, i.e json or yml

  * chg: add help str to make error report more concise
  * chg: add logs statements in various place
  * chg: dev: add CHANGELOG.md to record changes

### Changes

* Cleanup output for content from truyenfull.vn. [Nguyen Huu Hoa]

* Tolerate for some non-comforms htmls. [Nguyen Huu Hoa]

* Add customization options for generated ebook. [Nguyen Huu Hoa]

  + metadata: type bool, default is True. Metadata such as published_date, source url are generated after article (chapter) title if True
  + title_prefix_trim: type string, default is empty. When specified, string value in `title_prefix_trim` will be removed from article (chapter) title

### Other

* Docs: Prepare for release v0.4.0. [Nguyen Huu Hoa]


## v0.3.1 (2020-09-26)

### Changes

* Update meta information for pypi.org package [#8](https://github.com/huuhoa/colusa/pull/8) [Huu Hoa NGUYEN]

  + Add long description
  + Add classifiers
  + Prepare for release version 0.3.1


## v0.3.0 (2020-09-26)

### New

* Support book parts. [Nguyen Huu Hoa]

  Render additional information for book parts

* Support website truyenfull.vn, avikdas.com. [Nguyen Huu Hoa]

* Support web engineering.atspotify.com. [Nguyen Huu Hoa]

* Support website www.preethikasireddy.com. [Nguyen Huu Hoa]

* Support website cs.rutgers.edu. [Nguyen Huu Hoa]

* Support website medium.com. [Nguyen Huu Hoa]

* Support website slack.engineering. [Nguyen Huu Hoa]

* Support website increment.com. [Nguyen Huu Hoa]

* Add pdf target to Makefile for generating pdf format. [Nguyen Huu Hoa]

### Changes

* Rename project from symphony to colusa [#7](https://github.com/huuhoa/colusa/pull/7) [Huu Hoa NGUYEN]

  Colusa is not yet existed on pypi.org, so I rename the project
  in order to be able to upload it to pypi.org

  https://pypi.org/project/colusa

* Cleanup code. [Nguyen Huu Hoa]

* Cleanup etr.Transform to remove obsolete methods. [Nguyen Huu Hoa]

* Add coloring log for improved experiences in using app. [Nguyen Huu Hoa]

* Support to render `code` tag in asciidoc_visitor. [Nguyen Huu Hoa]

* Implement Visitor pattern for saving document to asciidoc [#6](https://github.com/huuhoa/colusa/pull/6) [Huu Hoa NGUYEN]

  + implement visitor pattern for writing asciidoc file format
  + implement visit methods for various tags
  + suppress empty text in anchor tag
  + add support for knowledgegraph.today
  + all unknown PageElement are classified to visit_unknown
  + support pre tag

* Update gitignore to exclude PyCharm IDE generated files. [Nguyen Huu Hoa]

* Update usage for symphony. [Nguyen Huu Hoa]

  + to initialize new ebook: symphony init <output configuration file>
  + to generate ebook contents: symphony generate <input configuration file>

* Add setup.py for easier installation. [Nguyen Huu Hoa]

* Implement plugin archiecture for Extractor, Transformer [#4](https://github.com/huuhoa/colusa/pull/4) [Huu Hoa NGUYEN]

* Update requirements.txt. [Nguyen Huu Hoa]

* Ignore empty heading. [Nguyen Huu Hoa]

* Support getting metadata from opengraph and getting main content from microformats - hentry. [Nguyen Huu Hoa]

* Report error when cannot understand a website. [Nguyen Huu Hoa]

* Update format for ul, ol. [Nguyen Huu Hoa]

* Default get_title for Extractor to get information from meta tag og:title or get from header>title. [Nguyen Huu Hoa]

* Support rendering code block. [Nguyen Huu Hoa]

* Don't use Renderer any more, since Transformer is enough to render asciidoc content. [Nguyen Huu Hoa]

* Transform tags: table, pre. [Nguyen Huu Hoa]

* Change encoding when saving content to cache and loading from cache. [Nguyen Huu Hoa]

* Correct rendering table code. [Nguyen Huu Hoa]

* Remove line break in heading tags. [Nguyen Huu Hoa]

* Add more information to README. [Nguyen Huu Hoa]

* Update README.md for Usage. [Nguyen Huu Hoa]

### Fix

* Error when check for existent of `paragraph-image` in `figure` class. [Nguyen Huu Hoa]

  Error occurs when tag `figure` does not have any classes, the node.get('class') will return None.
  Therefore when checking for existent of a text in None will throw exception.

* Remove extra line separators in truyenfull.vn. [Nguyen Huu Hoa]

* Generating new configuration. [Nguyen Huu Hoa]

* Rendering image in asciidoc. [Nguyen Huu Hoa]

* Parsing url and dimension in srcset attribute of img tag. [Nguyen Huu Hoa]

### Other

* Refactor: remove classmethods inside Transformer to make it open for extension. [Nguyen Huu Hoa]

* Refactor: move etr register extractor, transformer and their factory functions from etr_factory to etr. [Nguyen Huu Hoa]

  + Cleanup code
  + Make it more clean in using register decorators

* Docs: Update README.md. [Nguyen Huu Hoa]

* Docs: Update README.md for installing tools to generate ebooks. [Nguyen Huu Hoa]

* Tests: add skeleton for unit testing. [Nguyen Huu Hoa]

* Refactor: remove unused params in Transformer. [Nguyen Huu Hoa]

* Refactor: cleanup code. [Nguyen Huu Hoa]

* Refactor: create Symphony class to handle all business logics. [Nguyen Huu Hoa]

  + downloading urls
  + transform and generating ebook contents
  + generating ebook master file
  + generating Makefile

* Refactor: create symphony package and move all etr related to symphony. [Nguyen Huu Hoa]

* Docs: Update README.md. [Nguyen Huu Hoa]

* Wip: new way to transform html content to asciidoc format. [Nguyen Huu Hoa]

* Update README.md [#1](https://github.com/huuhoa/colusa/pull/1) [Anh Le (Andy)]

  Add installation script

* Cleanup ads on fsblog. [Nguyen Huu Hoa]

* Add support for fs.blog. [Nguyen Huu Hoa]

* Refactor code to make it easier to support new websites. [Nguyen Huu Hoa]

* Cleanup code and support rendering article's metadata. [Nguyen Huu Hoa]

* Change string formats to use f-string style. [Nguyen Huu Hoa]

* Add requirements.txt. [Nguyen Huu Hoa]

* Cleanup. [Nguyen Huu Hoa]

* Fix factory creator for unintendedconsequences. [Nguyen Huu Hoa]

* Generate makefile to generate ebook. [Nguyen Huu Hoa]

* Support render pre tag. [Nguyen Huu Hoa]

* Support config file to make it more general in supporting more repetitive works. [Nguyen Huu Hoa]

* Update ignote patterns. [Nguyen Huu Hoa]

* Generalize to accept new webblog. [hoanh]

* Update tool to generate index.asciidoc from template. [hoanh]

* Tools to download unintendedsequences. [hoanh]

* First version. [hoanh]

* Initial commit. [Huu Hoa NGUYEN]


