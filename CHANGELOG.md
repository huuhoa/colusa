# Changelog


## Unreleased

### New

* Support configuration file in YAML format. [Nguyen Huu Hoa]

  + Configuration file format is determined by extension, i.e json or yml

### Changes

* Add logs statements in various place. [Nguyen Huu Hoa]

* Add help str to make error report more concise. [Nguyen Huu Hoa]


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


