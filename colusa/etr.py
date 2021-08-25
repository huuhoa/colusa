import os
import re

from bs4 import Tag
from dateutil.parser import parse

from .asciidoc_visitor import AsciidocVisitor
from .utils import slugify

"""
Dictionary of extractor
"""
__EXTRACTORS = {}

"""
Dictionary of transformer
"""
__TRANSFORMERS = {}


def register_extractor(pattern):
    def decorator(cls):
        __EXTRACTORS[pattern] = cls
        return cls

    return decorator


def register_transformer(pattern):
    def decorator(cls):
        __TRANSFORMERS[pattern] = cls
        return cls

    return decorator


def create_extractor(url_path, bs):
    for p in __EXTRACTORS.keys():
        if p in url_path:
            cls = __EXTRACTORS[p]
            return cls(bs)
    return Extractor(bs)


def create_transformer(url_path, content, root):
    config = {
        "src_url": url_path,
        "output_dir": root
    }
    for p in __TRANSFORMERS.keys():
        if p in url_path:
            cls = __TRANSFORMERS[p]
            return cls(config, content)

    return Transformer(config, content)


class ContentNotFoundError(Exception):
    def __init__(self, *args, **kwargs):
        pass

    def __str__(self):
        return 'cannot detect content of the site'


class Extractor(object):
    """Extractor extract real article content from sea of other contents"""
    def __init__(self, bs):
        self.bs = bs
        self.content = None
        self.author = None
        self.published = None
        self.title = None
        self.extra_metadata = ''

        self.main_content = self._find_main_content()
        if self.main_content is None:
            raise ContentNotFoundError()

        self._parse_metadata()

    def _parse_title(self) -> str:
        """
        Parse known tags in html for article's title
        :return: title if found
        """
        meta = self.bs.find('meta', attrs={'property': 'og:title'})
        if meta is not None:
            return meta.get('content')
        else:
            return self.bs.title.text

    def _parse_published(self) -> str:
        """
        Parse known tags in html for article's published date
        :return: str value for date in format `%Y-%m-%d`
        """
        meta = self.bs.find('meta', attrs={'property': 'article:published_time'})
        value = meta.get('content') if meta else None
        if value is not None:
            published = parse(value)
            return str(published.date())

        time_published = self.bs.find('time', attrs={'class': 'entry-date published'})
        if time_published is not None:
            return time_published.text

        return ''

    def _parse_author(self) -> str:
        """
        Parse known tags in html for article's author
        :return: author name if found
        """
        meta = self.bs.find('meta', attrs={'name': 'author'})
        if meta is not None:
            value = meta.get('content')
            if value is not None:
                return value
        return ''

    def _parse_extra_metadata(self) -> str:
        return ''

    @classmethod
    def remove_tag(cls, site, tag, attrs):
        elements = site.find_all(tag, attrs=attrs)
        if elements is not None:
            for e in elements:
                e.extract()

    def cleanup(self):
        """
        Cleanup extra content (mostly ads) within main content
        """
        self.remove_tag(self.main_content, 'div', attrs={'class': 'site-branding'})
        self.remove_tag(self.main_content, 'div', attrs={'class': 'navigation-top'})
        self.remove_tag(self.main_content, 'footer', attrs={})
        # self.remove_tag(self.site, 'footer', attrs={'class': 'site-footer'})
        self.remove_tag(self.main_content, 'div', attrs={'class': 'searchsettings'})
        self.remove_tag(self.main_content, 'section', attrs={'id': 'ajaxsearchlitewidget-2'})
        self.remove_tag(self.main_content, 'aside', attrs={'id': 'secondary'})
        self.remove_tag(self.main_content, 'nav', attrs={'class': 'post-navigation'})
        self.remove_tag(self.main_content, 'header', attrs={'id': 'masthead'})

    def get_content(self):
        """
        :return: handle to main content of website
        """
        return self.main_content

    def _find_main_content(self) -> Tag:
        """
        The purpose of internal_init is to find the main content of website
        and set the member self.site to handle of that content

        Default implementation tries to cover as much as possible the commonly
        known web structure such as blog, hentry, article

        :return: Tag of main content
        """
        def is_content_class(css_class):
            return css_class is not None and css_class in [
                'postcontent',
                'entry-content',
                'article-content',
                'blog-content',
            ]
        # h-entry from microformat
        site = self.bs.find(class_='hentry')
        if site is not None:
            role_main = site.find('div', attrs={'role': 'main'})
            if role_main is not None:
                site = role_main
            role_main = site.find('div', attrs={'class': 'td-post-content'})
            if role_main is not None:
                site = role_main

            return site

        tag = self.bs.find('div', class_=is_content_class)
        if tag is not None:
            return tag
        hs_blog_post = self.bs.find(attrs={'class': 'hs-blog-post'})
        if hs_blog_post is not None:
            blog_content = hs_blog_post.find(attrs={'class': 'post-body'})
            return blog_content
        tag = self.bs.find('article')
        if tag is not None:
            return tag
        tag = self.bs.find('main')
        if tag is not None:
            return tag

    def _parse_yoast_data(self) -> dict:
        """
        Parse yoast json data to get some metadata such as author, published date
        :return: dict of metadata found in yoast data
        """
        yoast_data = self.bs.find('script', attrs={
            'type': "application/ld+json",
            'class': "yoast-schema-graph",
        })

        return_data = {}
        if yoast_data is None:
            return return_data

        import json
        from dateutil import parser
        data = json.loads(yoast_data.string)
        graph = data.get('@graph', [])
        persons = {}
        author = None
        for g in graph:
            if type(g) is not dict:
                continue
            g_type = g.get('@type', '')
            if g_type == 'Article':
                author = g.get('author', {}).get('@id')
                published_value = g.get('datePublished')
                if published_value:
                    published = parser.parse(published_value)
                    return_data['published'] = str(published.date())
                headline = g.get('headline')
                if headline:
                    return_data['title'] = headline

            if (type(g_type) is list and 'Person' in g_type) or (type(g_type) is str and g_type == 'Person'):
                person_id = g.get('@id', '')
                person_name = g.get('name', '')
                persons[person_id] = person_name
        if author in persons:
            return_data['author'] = persons[author]

        return return_data

    def _parse_metadata(self):
        """
        Parse existing web metadata to get value for `title`, `author`, `published`
        """
        self.title = self._parse_title()
        self.author = self._parse_author()
        self.published = self._parse_published()
        self.extra_metadata = self._parse_extra_metadata()
        data = self._parse_yoast_data()
        self.title = data.get('title', self.title)
        self.author = data.get('author', self.author)
        self.published = data.get('published', self.published)


class Transformer(object):
    """Transformer transform some html tags into asciidoc syntax"""
    def __init__(self, config, site):
        self.value = ''
        self.config = config
        self.site = site

    @classmethod
    def tag_wrapper_pre(cls, tag: Tag, text: str, indent: int):
        code_pattern = r"^\[code\s+lang=(?P<lang>.*)\](?P<content>.*)\[\/code\]$"
        matches = re.finditer(code_pattern, tag.text, re.MULTILINE | re.DOTALL)
        content = []
        for matchNum, match in enumerate(matches, start=1):
            ascii_content = f'''[source, {match.group('lang')}]
----
{match.group('content')}
----
'''
            content.append(ascii_content)

        if len(content) == 0:
            print('PRE ====', text)
            content.append(f'''[listing]
....
{text}
....

''')
        return ''.join(content)

    def transform(self):
        visitor = AsciidocVisitor()
        # print(self.site)
        self.value = visitor.visit(self.site, src_url=self.config['src_url'], output_dir=self.config['output_dir'])
        # print(value)
        # cleanup large whitespace
        self.value = re.sub(r'(\n\s*){3,}', '\n\n', self.value)
        return self.value


class Render(object):
    """
        Render book metadata, structure
    """
    def __init__(self, config: dict):
        self.output_dir = config.get('output_dir', '.')
        self.config = config
        self.file_list = []

    def render_book_part(self, title: str, description: str):
        file_name = f'part_{slugify(title)}.asciidoc'
        self.file_list.append(file_name)
        file_path = os.path.join(self.output_dir, file_name)
        with open(file_path, 'w', encoding='utf-8') as file_out:
            file_out.write(f'// {title}\n\n= {title}\n\n')
            if len(description) > 0:
                file_out.write(description)
                file_out.write('\n\n')

    def render_chapter(self, extractor: Extractor, content: Transformer, src_url, basename: str,
                       metadata=True, title_strip=''):
        file_name = f'{basename}.asciidoc'
        self.file_list.append(file_name)
        file_path = os.path.join(self.output_dir, file_name)
        with open(file_path, 'w', encoding='utf-8') as file_out:
            title = extractor.title
            title = title.replace(title_strip, '')
            file_out.write(f'// {title}\n\n== {title}\n\n')

            if metadata:
                article_metadata = self.render_metadata(extractor, content, src_url)
                file_out.write(article_metadata)

            file_out.write(content.value)

    def render_metadata(self, extractor: Extractor, content: Transformer, src_url):
        from urllib.parse import urlparse

        author = extractor.author
        data = []
        if author:
            author_fmt = f'by **{author}**'
            data.append(author_fmt)
        time_published = extractor.published
        if time_published:
            published_info = f'on {time_published}'
            data.append(published_info)

        domain = urlparse(src_url).netloc
        data.append(f'at _link:{src_url}[{domain}]_')
        first_line = ' '.join(data)
        lines = [f"{first_line}\n"]
        extra = extractor.extra_metadata
        if extra:
            lines.append(extra)
        lines.append('\n')
        article_metadata = "\n".join(lines)
        return article_metadata

    def generate_makefile(self):
        template = '''html:
\tasciidoctor index.asciidoc -d book -b html5 -D output
\tcp -r images output/

epub:
\tasciidoctor-epub3 index.asciidoc -d book -D output

pdf:
\tasciidoctor-pdf index.asciidoc -d book -D output
'''
        file_path = os.path.join(self.output_dir, 'Makefile')
        with open(file_path, 'w') as out_file:
            out_file.write(template)

    def ebook_generate_master_file(self):
        """ Generate master index.asciidoc to include all book related information such as
        - book title
        - book author
        - book version
        - etc
        - and include all generated asciidoc files from `urls`
        """
        included_files = '\n'.join(['include::%s[]' % x for x in self.file_list])
        book_properties = '\n'.join([x.strip() for x in self.config.get('book_properties', [])])
        content = f'''= {self.config["title"]}
{self.config["author"]}
{self.config["version"]}
:doctype: book
:partnums:
:toc:
:imagesdir: images
:homepage: {self.config["homepage"]}
{book_properties}

{included_files}
'''
        with open(os.path.join(self.output_dir, 'index.asciidoc'), 'w') as index_file:
            index_file.write(content)
