# Changelog


## v0.12.0 (2022-07-24)

### New

* Add new command to crawl an URL. [Nguyen Huu Hoa]

  Crawl an URL (website) to help generate list of URL, mostly story chapters

### Changes

* Add some debug capability. [Nguyen Huu Hoa]

* Add support for new websites. [Nguyen Huu Hoa]

### Other

* Merge branch 'main' of github.com:huuhoa/colusa. [Nguyen Huu Hoa]

* Chg(plugins/truyenfull): clean ads content. [Nguyen Huu Hoa]

* Chg(plugins/truyenfull): clean ads content. [Nguyen Huu Hoa]


## v0.11.0 (2022-02-17)

### Changes

* Support for tangthuvien (#72) [Huu Hoa NGUYEN]

### Fix

* Gitchangelog ignore pattern. [Nguyen Huu Hoa]


## v0.10.0 (2021-10-16)

### Changes

* Update dev requirements. [Nguyen Huu Hoa]

* Improve code coverage (#21) [Huu Hoa NGUYEN]

  Mock up two functions download_image and download_content

  + `download_content` will return existing cached file, so that we don't have to redownload every time
  we run the test
  + `download_image` will just return True, do nothing, so that we don't have to download images

### Other

* Add: support for techtarget.com (#32) [Huu Hoa NGUYEN]

  * chg(asciidoc_visitor): support parsing datasrc and data-srcset for img
  * add(web): support for techtarget.com


## v0.9.0 (2021-08-26)

### New

* Integration tests (#20) [Huu Hoa NGUYEN]

  * chg: add tox.ini for running tox
  * chg(colusa): move colusa source to src folder

* Support parsing site xp123.com (#18) [Huu Hoa NGUYEN]

### Other

* Chore: update setup.cfg for version location. [Nguyen Huu Hoa]

* Prepare for next release. [Nguyen Huu Hoa]

* Refactor(etr): Rework on Extractor (#19) [Huu Hoa NGUYEN]

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

* Support rendering additional book properties (#16) [Huu Hoa NGUYEN]

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

* Render html table as native asciidoc table (#17) [Huu Hoa NGUYEN]

### Other

* Prepare for bump version 0.8. [Nguyen Huu Hoa]

* Add(plugins): support for scrumcrazy.wordpress.com. [Nguyen Huu Hoa]


## v0.7.0 (2021-08-20)

### Changes

* Improve article parsing (#15) [Huu Hoa NGUYEN]

  * add: agilethought support to get article's author
  * add: support website tech.trivago.com

* Metadata rendering (#14) [Huu Hoa NGUYEN]

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

* Support new website https://agilethought.com (#11) [Huu Hoa NGUYEN]

### Changes

* Etr: improve metadata rendering for generated articles (#10) [Huu Hoa NGUYEN]


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

* Yaml configuration (#9) [Huu Hoa NGUYEN]

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

* Update meta information for pypi.org package (#8) [Huu Hoa NGUYEN]

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

* Rename project from symphony to colusa (#7) [Huu Hoa NGUYEN]

  Colusa is not yet existed on pypi.org, so I rename the project
  in order to be able to upload it to pypi.org

  https://pypi.org/project/colusa

* Cleanup code. [Nguyen Huu Hoa]

* Cleanup etr.Transform to remove obsolete methods. [Nguyen Huu Hoa]

* Add coloring log for improved experiences in using app. [Nguyen Huu Hoa]

* Support to render `code` tag in asciidoc_visitor. [Nguyen Huu Hoa]

* Implement Visitor pattern for saving document to asciidoc (#6) [Huu Hoa NGUYEN]

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

* Implement plugin archiecture for Extractor, Transformer (#4) [Huu Hoa NGUYEN]

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

* Update README.md (#1) [Anh Le (Andy)]

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


