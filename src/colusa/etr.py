import os
import re
from typing import Any, Callable, Optional, Type, Union

from bs4 import Tag, BeautifulSoup
from dateutil.parser import parse

from .asciidoc_visitor import AsciidocVisitor
from .visitor import NodeVisitor
from .utils import slugify
from .config import BookConfig, MakeConfig

"""
Dictionary of extractor
"""
__EXTRACTORS: dict[str, dict[str, Any]] = {}

"""
Dictionary of transformer
"""
__TRANSFORMERS: dict[str, dict[str, Any]] = {}

"""
Dictionary of postprocessing
"""
__POSTPROCESSORS: dict[str, Type['PostProcessor']] = {}


def register_extractor(pattern: str) -> Callable[[Type['Extractor']], Type['Extractor']]:
    def decorator(cls: Type['Extractor']) -> Type['Extractor']:
        __EXTRACTORS[cls.__name__] = {
            'pattern': pattern,
            'cls': cls,
        }
        return cls

    return decorator


def register_extractor_v2(id: str, pattern: str) -> Callable[[Type['Extractor']], Type['Extractor']]:
    def decorator(cls: Type['Extractor']) -> Type['Extractor']:
        __EXTRACTORS[id] = {
            'pattern': pattern,
            'cls': cls,
        }
        return cls

    return decorator


def register_transformer(pattern: str) -> Callable[[Type['Transformer']], Type['Transformer']]:
    def decorator(cls: Type['Transformer']) -> Type['Transformer']:
        __TRANSFORMERS[cls.__name__] = {
            'pattern': pattern,
            'cls': cls,
        }
        return cls

    return decorator


def register_transformer_v2(id: str, pattern: str) -> Callable[[Type['Transformer']], Type['Transformer']]:
    def decorator(cls: Type['Transformer']) -> Type['Transformer']:
        __TRANSFORMERS[id] = {
            'pattern': pattern,
            'cls': cls,
        }
        return cls

    return decorator


def register_postprocessor(name: str) -> Callable[[Type['PostProcessor']], Type['PostProcessor']]:
    """Register post processing class"""
    def decorator(cls: Type['PostProcessor']) -> Type['PostProcessor']:
        __POSTPROCESSORS[name] = cls
        return cls

    return decorator


def create_extractor(url_path: str, bs: BeautifulSoup) -> 'Extractor':
    for _, ext in __EXTRACTORS.items():
        p: str = ext['pattern']
        cls: Type['Extractor'] = ext['cls']
        if re.search(p, url_path):
            return cls(bs)
    return Extractor(bs)


def populate_extractor_config(config: dict[str, Any]) -> None:
    """
    Populate extract configs from external configuration file.
    Should be called at begining before creating any extractor
    """
    for id, v in config.items():
        if id in __EXTRACTORS:
            ext = __EXTRACTORS[id]
            ext.update(v)


def populate_transformer_config(config: dict[str, Any]) -> None:
    """
    Populate transformer configs from external configuration file.
    Should be called at begining before creating any transformer
    """
    for id, v in config.items():
        if id in __TRANSFORMERS:
            trf = __TRANSFORMERS[id]
            trf.update(v)


def create_transformer(url_path: str, content: Tag, root: str) -> 'Transformer':
    config: dict[str, str] = {
        "src_url": url_path,
        "output_dir": root
    }
    for _, trf in __TRANSFORMERS.items():
        p: str = trf['pattern']
        cls: Type['Transformer'] = trf['cls']
        if re.search(p, url_path):
            return cls(config, content)

    return Transformer(config, content)


class ContentNotFoundError(Exception):
    def __init__(self, *args: Any, **kwargs: Any) -> None:
        pass

    def __str__(self) -> str:
        return 'cannot detect content of the site'


class Extractor:
    """Extractor extract real article content from sea of other contents"""
    def __init__(self, bs: BeautifulSoup) -> None:
        self.bs: BeautifulSoup = bs
        self.content: Optional[Tag] = None
        self.author: Optional[str] = None
        self.published: Optional[str] = None
        self.title: Optional[str] = None
        self.extra_metadata: str = ''

        self.main_content: Optional[Tag] = self._find_main_content()
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
    def remove_tag(cls, site: Optional[Tag], tag: str, attrs: dict[str, Any]) -> None:
        if site is None:
            return
        elements = site.find_all(tag, attrs=attrs)
        if elements is not None:
            for e in elements:
                e.extract()

    def cleanup(self) -> None:
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

    def get_content(self) -> Optional[Tag]:
        """
        :return: handle to main content of website
        """
        return self.main_content

    def _find_main_content(self) -> Optional[Tag]:
        """
        The purpose of internal_init is to find the main content of website
        and set the member self.site to handle of that content

        Default implementation tries to cover as much as possible the commonly
        known web structure such as blog, hentry, article

        :return: Tag of main content
        """
        def is_content_class(css_class: Optional[str]) -> bool:
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
        return None

    def _parse_yoast_data(self) -> dict[str, str]:
        """
        Parse yoast json data to get some metadata such as author, published date
        :return: dict of metadata found in yoast data
        """
        yoast_data = self.bs.find('script', attrs={
            'type': "application/ld+json",
            'class': "yoast-schema-graph",
        })

        return_data: dict[str, str] = {}
        if yoast_data is None:
            return return_data

        import json
        from dateutil import parser
        data = json.loads(yoast_data.string)
        graph = data.get('@graph', [])
        persons: dict[str, str] = {}
        author: Optional[str] = None
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

    def _parse_metadata(self) -> None:
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


class Transformer:
    """Transformer transform some html tags into asciidoc syntax"""
    def __init__(self, config: dict[str, str], site: Tag) -> None:
        self.value: str = ''
        self.config: dict[str, str] = config
        self.site: Tag = site

    @classmethod
    def tag_wrapper_pre(cls, tag: Tag, text: str, indent: int) -> str:
        code_pattern = r"^\[code\s+lang=(?P<lang>.*)\](?P<content>.*)\[\/code\]$"
        matches = re.finditer(code_pattern, tag.text, re.MULTILINE | re.DOTALL)
        content: list[str] = []
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

    def create_visitor(self) -> NodeVisitor:
        """
        Create new instance of NodeVisitor, used in transform method
        """
        return AsciidocVisitor()

    def transform(self) -> str:
        visitor = self.create_visitor()
        # print(self.site)
        self.value = visitor.visit(self.site, src_url=self.config['src_url'], output_dir=self.config['output_dir'])
        # print(value)
        # cleanup large whitespace
        self.cleanup_after_visit()
        return self.value

    def cleanup_after_visit(self) -> None:
        """
        Cleanup transformed text
        """
        self.value = re.sub(r'(\n\s*){3,}', '\n\n', self.value)


class Render:
    """
        Render book metadata, structure
    """
    def __init__(self, config: Union[dict[str, Any], BookConfig]) -> None:
        # Support both dict and BookConfig for backward compatibility
        if isinstance(config, BookConfig):
            self._config = config
        else:
            self._config = BookConfig.from_dict(config)
        self.output_dir: str = self._config.output_dir
        self.file_list: list[tuple[str, int]] = []

    def render_book_part(self, title: str, description: str) -> None:
        file_name = f'part_{slugify(title)}.asciidoc'
        self.file_list.append((file_name, 0))
        file_path = os.path.join(self.output_dir, file_name)
        with open(file_path, 'w', encoding='utf-8') as file_out:
            file_out.write(f'= {title}\n\n')
            if len(description) > 0:
                file_out.write(description)
                file_out.write('\n\n')

    def render_chapter(self, extractor: Extractor, content: Transformer, src_url: str, basename: str,
                       metadata: bool = True, title_strip: str = '') -> str:
        file_name = f'{basename}.asciidoc'
        self.file_list.append((file_name, 1))
        file_path = os.path.join(self.output_dir, file_name)
        with open(file_path, 'w', encoding='utf-8') as file_out:
            title = extractor.title or ''
            title = title.replace(title_strip, '')
            file_out.write(f'= {title}\n\n')

            if metadata:
                article_metadata = self.render_metadata(extractor, content, src_url)
                file_out.write(article_metadata)

            file_out.write(content.value)

        return file_path

    def render_metadata(self, extractor: Extractor, content: Transformer, src_url: str) -> str:
        from urllib.parse import urlparse

        author = extractor.author
        data: list[str] = []
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
        lines: list[str] = [f"{first_line}\n"]
        extra = extractor.extra_metadata
        if extra:
            lines.append(extra)
        lines.append('\n')
        article_metadata = "\n".join(lines)
        return article_metadata

    def generate_makefile(self, make_params: Union[dict[str, str], MakeConfig]) -> None:
        # Support both dict and MakeConfig
        if isinstance(make_params, MakeConfig):
            html_params = make_params.html
            epub_params = make_params.epub
            pdf_params = make_params.pdf
        else:
            html_params = make_params.get('html', '')
            epub_params = make_params.get('epub', '')
            pdf_params = make_params.get('pdf', '')
        
        book_file_name = self._config.book_file_name
        target_prefix = book_file_name
        target_prefix = target_prefix.removesuffix('.asciidoc').replace('-', '_')
        target_prefix = '' if target_prefix == 'index' else f'{target_prefix}_'
        template = f'''html:
\tasciidoctor {book_file_name} -d book -b html5 -D output {html_params}
\tcp -r images output/

epub:
\tasciidoctor-epub3 {book_file_name} -d book -D output {epub_params}

pdf:
\tasciidoctor-pdf {book_file_name} -d book -D output {pdf_params}
'''
        file_path = os.path.join(self.output_dir, f'{target_prefix}Makefile')
        with open(file_path, 'w') as out_file:
            out_file.write(template)

    def ebook_generate_master_file(self) -> None:
        """ Generate master index.asciidoc to include all book related information such as
        - book title
        - book author
        - book version
        - etc
        - and include all generated asciidoc files from `urls`
        """
        included_files = '\n\n'.join([f'include::{x[0]}[leveloffset={x[1]}]' for x in self.file_list])
        book_properties = '\n'.join([x.strip() for x in self._config.book_properties])
        content = f'''= {self._config.title}
{self._config.author}
{self._config.version}
:doctype: book
:partnums:
:toc:
:imagesdir: images
:homepage: {self._config.homepage}
{book_properties}

{included_files}
'''
        book_file_name = self._config.book_file_name
        with open(os.path.join(self.output_dir, book_file_name), 'w') as index_file:
            index_file.write(content)


class PostProcessor:
    def __init__(self, file_path: str, params: list[Any]) -> None:
        self.file_path: str = file_path
        self.params: list[Any] = params

    def run(self) -> None:
        pass


class PostProcessorNotFoundError(Exception):
    def __init__(self, name: str, *args: Any, **kwargs: Any) -> None:
        self.name: str = name

    def __str__(self) -> str:
        return f'Post Processor {self.name} is not registered'


def create_postprocessor(name: str, file_path: str, params: list[Any]) -> PostProcessor:
    cls = __POSTPROCESSORS.get(name)
    if not cls:
        raise PostProcessorNotFoundError(name)

    return cls(file_path, params)
