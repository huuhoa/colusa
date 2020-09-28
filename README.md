# colusa

Render website to ebook to make it easier to read on devices.

## Installation

```sh
python3 setup.py install
```

## Usage

### Start from scratch

First of all, we need to generate a configuration file for `colusa` to work on.
`colusa` has builtin command to generate a template configuration as starter.
Run following command to generate configuration file:

```bash
$ colusa init new_ebook.json
```

`colusa` will generate a configuration file as below:

```json
{
    "title": "__fill the title__",
    "author": "__fill the author__",
    "version": "v1.0",
    "homepage": "__fill url to home page__",
    "output_dir": "__fill output dir__",
    "urls": []
}
```

We have to modify the configuration file to fill up valid information.

### Add content to ebook

After generating the configuration file, all we need to do is adding (blog posts, articles, webs)' urls to `urls` field in the configuration file.

Example for final configuration:

```json
{
    "title": "The Great Mental Models",
    "author": "Farnam Street Media Inc",
    "version": "v1.0",
    "homepage": "https://fs.blog",
    "output_dir": "fsblog",
    "urls": [
        "https://fs.blog/2018/04/first-principles/",
        "https://fs.blog/2016/04/second-order-thinking/",
        "https://fs.blog/2017/06/thought-experiment/",
        "https://fs.blog/2018/05/probabilistic-thinking/",
        "https://fs.blog/2019/12/survivorship-bias/"
    ]
}
```

### Update ebook content

We can update ebook content by modifying the `urls`, by adding or removing url in the `urls`, the result ebook will be changed.

### Generate ebook content

After adding or removing url in `urls`, we need to invoke `colusa` to have it regenerate ebook content. Run following command at terminal:

```bash
$ colusa generate new_ebook.json
```

By invoking above command, `colusa` will download webpages (specified in `urls`), parse, transform them to asciidoc format, and save them to `output_dir`. `colusa` also create a neccessary information for ebook compilating at later steps.

## Compile ebook for consuming purpose

### Prerequisites
Before generating ebook, we need to install asciidoctor tools. Follow install guideline on following websites:

* for generating html: https://asciidoctor.org 
* for generating epub: https://asciidoctor.org/docs/asciidoctor-epub3/
* for generating pdf: https://asciidoctor.org/docs/asciidoctor-pdf/

### Generating ebooks
To help with generating ebook, `colusa` also create a `Makefile` in the root folder of the ebook. In the `Makefile`, there are three common targets that we can use to generate ebook in html, epub, pdf formats.

```bash
# to generate html
$ make html

# to generate epub
$ make epub

# to generate pdf
$ make pdf
```

Generated ebooks will be saved to `./output` folder.

```
user:output/ $ ls                                                            [10:55:55]
total 3056
drwxr-xr-x  10 320B images
-rw-r--r--   1 699K index.epub
-rw-r--r--   1 131K index.html
-rw-r--r--@  1 694K index.pdf
```

## List of Supported Website

Currently `colusa` supports only limited number of websites. The following list all support websites:

* https://untools.co
* https://unintendedconsequenc.es
* https://blog.acolyer.org
* https://fs.blog
* https://increment.com
* https://slack.engineering
* https://medium.com
* https://www.cs.rutgers.edu/~pxk/
* https://www.preethikasireddy.com
* https://engineering.atspotify.com
* https://truyenfull.vn
* https://avikdas.com
* https://www.infoq.com

## Contribution

Contribution is welcome. You can open issues to request for supporting more websites, open PR to help with those issues, or anything else like documentation, code contribution.


