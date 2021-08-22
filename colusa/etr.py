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
        self.site = None
        self.content = None
        self.internal_init()
        if self.site is None:
            raise ContentNotFoundError()

    def get_title(self):
        meta = self.bs.find('meta', attrs={'property': 'og:title'})
        if meta is not None:
            return meta.get('content')
        return self.bs.title.text

    def get_published(self):
        meta = self.bs.find('meta', attrs={'property': 'article:published_time'})
        if meta is not None:
            value = meta.get('content')
            if value is not None:
                published = parse(value)
                return_value = str(published.date())
                return return_value

        time_published = self.bs.find('time', attrs={'class': 'entry-date published'})
        if time_published is not None:
            published = time_published.text
            return published
        else:
            return None

    def get_author(self):
        meta = self.bs.find('meta', attrs={'name': 'author'})
        if meta is not None:
            value = meta.get('content')
            if value is not None:
                return value

        return None

    def get_metadata(self):
        return ''

    @classmethod
    def remove_tag(cls, site, tag, attrs):
        b = site.find(tag, attrs=attrs)
        if b is not None:
            b.extract()

    def cleanup(self):
        self.remove_tag(self.site, 'div', attrs={'class': 'site-branding'})
        self.remove_tag(self.site, 'div', attrs={'class': 'navigation-top'})
        self.remove_tag(self.site, 'footer', attrs={})
        # self.remove_tag(self.site, 'footer', attrs={'class': 'site-footer'})
        self.remove_tag(self.site, 'div', attrs={'class': 'searchsettings'})
        self.remove_tag(self.site, 'section', attrs={'id': 'ajaxsearchlitewidget-2'})
        self.remove_tag(self.site, 'aside', attrs={'id': 'secondary'})
        self.remove_tag(self.site, 'nav', attrs={'class': 'post-navigation'})
        self.remove_tag(self.site, 'header', attrs={'id': 'masthead'})

    def get_content(self):
        return self.site

    def internal_init(self):
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

            self.site = site

            return
        self.site = self.bs.find('div', class_=is_content_class)
        if self.site is None:
            self.site = self.bs.find('article')
        hs_blog_post = self.bs.find(attrs={'class': 'hs-blog-post'})
        if hs_blog_post is not None:
            blog_content = hs_blog_post.find(attrs={'class': 'post-body'})
            self.site = blog_content
        if self.site is None:
            self.site = self.bs.find('main')


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
            title = extractor.get_title()
            title = title.replace(title_strip, '')
            file_out.write(f'// {title}\n\n== {title}\n\n')

            if metadata:
                article_metadata = self.render_metadata(extractor, content, src_url)
                file_out.write(article_metadata)

            file_out.write(content.value)

    def render_metadata(self, extractor: Extractor, content: Transformer, src_url):
        from urllib.parse import urlparse

        author = extractor.get_author()
        data = []
        if author is not None:
            author_fmt = f'by **{author}**'
            data.append(author_fmt)
        time_published = extractor.get_published()
        if time_published is not None:
            published_info = f'on {time_published}'
            data.append(published_info)

        domain = urlparse(src_url).netloc
        data.append(f'at _link:{src_url}[{domain}]_')
        first_line = ' '.join(data)
        lines = [f"{first_line}\n"]
        extra = extractor.get_metadata()
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
