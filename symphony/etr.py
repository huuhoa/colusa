import os
import re
from dateutil.parser import parse

import requests
from bs4 import NavigableString, Tag

from .asciidoc_visitor import AsciidocVisitor
from .utils import download_image, slugify

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
        self.remove_tag(self.site, 'footer', attrs={'class': 'site-footer'})
        self.remove_tag(self.site, 'div', attrs={'class': 'searchsettings'})
        self.remove_tag(self.site, 'section', attrs={'id': 'ajaxsearchlitewidget-2'})
        self.remove_tag(self.site, 'aside', attrs={'id': 'secondary'})
        self.remove_tag(self.site, 'nav', attrs={'class': 'post-navigation'})
        self.remove_tag(self.site, 'header', attrs={'id': 'masthead'})

    def get_content(self):
        return self.site

    def internal_init(self):
        # h-entry from microformat
        site = self.bs.find(class_='hentry')
        if site is not None:
            self.site = site
            return
        self.site = self.bs.find('div', class_='entry-content')
        if self.site is None:
            self.site = self.bs.find('div', class_='article-content')
        if self.site is None:
            self.site = self.bs.find('article')


class Transformer(object):
    """Transformer transform some html tags into asciidoc syntax"""
    def __init__(self, config, site):
        self.value = ''
        self.wrappers = {
            'a': self.tag_wrapper_a,
            'italic': self.tag_wrapper_italic,
            'em': self.tag_wrapper_italic,
            'i': self.tag_wrapper_italic,
            'b': self.tag_wrapper_strong,
            'strong': self.tag_wrapper_strong,
            'h1': self.tag_wrapper_h1,
            'h2': self.tag_wrapper_h2,
            'h3': self.tag_wrapper_h3,
            'h4': self.tag_wrapper_h4,
            'h5': self.tag_wrapper_h5,
            'h6': self.tag_wrapper_h6,
            'p': self.tag_wrapper_p,
            'div': self.tag_wrapper_p,
            'span': self.tag_wrapper_span,
            'article': self.tag_wrapper_span,
            'ul': self.tag_wrapper_ul,
            'ol': self.tag_wrapper_ol,
            'li': self.tag_wrapper_li,
            'img': self.tag_wrapper_img,
            'blockquote': self.tag_wrapper_quote,
            'figure': self.tag_wrapper_figure,
            'figcaption': self.tag_wrapper_figurecaption,
            'code': self.tag_wrapper_inline_code,
            'pre': self.tag_wrapper_pre,
        }

        self.config = config
        self.site = site

    def tag_wrapper_cleanup(self, text: str) -> str:
        text = text.strip()
        rex = re.compile(r'\n\s*')
        text = re.sub(rex, ' ', text)
        return text

    def tag_wrapper_a(self, tag: Tag, text: str, indent: int):
        href = tag.get("href", "")
        m = re.match(r'https?://', href)
        if m is None:
            return text
        else:
            return f'link:{href}[{text}]'

    def tag_wrapper_italic(self, tag: Tag, text: str, indent: int):
        if not text:
            return ''
        return f'__{text}__'

    def tag_wrapper_strong(self, tag: Tag, text: str, indent: int):
        if not text:
            return ''
        return f'**{text}**'

    def tag_wrapper_h1(self, tag: Tag, text: str, indent: int):
        final_heading = self.tag_wrapper_cleanup(text)
        if not final_heading:
            return ''
        return f'=== {final_heading}\n\n'

    def tag_wrapper_h2(self, tag: Tag, text: str, indent: int):
        final_heading = self.tag_wrapper_cleanup(text)
        if not final_heading:
            return ''
        return f'=== {final_heading}\n\n'

    def tag_wrapper_h3(self, tag: Tag, text: str, indent: int):
        final_heading = self.tag_wrapper_cleanup(text)
        if not final_heading:
            return ''
        return f'==== {final_heading}\n\n'

    def tag_wrapper_h4(self, tag: Tag, text: str, indent: int):
        final_heading = self.tag_wrapper_cleanup(text)
        if not final_heading:
            return ''
        return f'===== {final_heading}\n\n'

    def tag_wrapper_h5(self, tag: Tag, text: str, indent: int):
        final_heading = self.tag_wrapper_cleanup(text)
        if not final_heading:
            return ''
        return f'====== {final_heading}\n\n'

    def tag_wrapper_h6(self, tag: Tag, text: str, indent: int):
        final_heading = self.tag_wrapper_cleanup(text)
        if not final_heading:
            return ''
        return f'======= {final_heading}\n\n'

    def tag_wrapper_p(self, tag: Tag, text: str, indent: int):
        return f'{text}\n\n'

    def tag_wrapper_span(self, tag: Tag, text: str, indent: int):
        return text

    def tag_wrapper_ul(self, tag: Tag, text: str, indent: int):
        return f'\n{text}\n'

    def tag_wrapper_ol(self, tag: Tag, text: str, indent: int):
        return f'\n{text}\n'

    def tag_wrapper_li(self, tag: Tag, text: str, indent: int):
        if tag.parent.name == 'ol':
            return f'{"." * indent} {text}\n'
        else:
            return f'{"*" * indent} {text}\n'

    def tag_wrapper_quote(self, tag: Tag, text: str, indent: int):
        return f'[quote]\n____\n{text}\n____\n\n'

    def tag_wrapper_figure(self, tag: Tag, text: str, indent: int):
        return f'{text}\n\n'

    def tag_wrapper_figurecaption(self, tag: Tag, text: str, indent: int):
        return f'\n{text}\n'

    def tag_wrapper_img(self, img: Tag, text: str, indent: int):
        alt = img.get('alt', '')
        height = img.get('height', '')
        width = img.get('width', '')
        src = img.get('src', None)
        if src is None:
            return ''
        srcset = img.get('srcset', None)
        dim = f'{width}, {height}'
        dim, src = self.get_image_from_srcset(srcset, src, dim)
        url_path = requests.compat.urljoin(self.config['src_url'], src)
        image_name = download_image(url_path, self.config['output_dir'])
        return f'image:{image_name}[{alt},{dim}]'

    def get_image_from_srcset(self, srcset, default_src, default_dim):
        if srcset is None:
            return default_dim, default_src

        srcs = srcset.split(', ')
        imgs = {}
        for s in srcs:
            s = s.strip()
            ss = s.split(' ')
            if len(ss) > 1:
                imgs[ss[1]] = ss[0]
        if len(imgs) == 0:
            return default_dim, default_src

        dim_list = sorted(imgs.keys(), key=lambda x: int(x.replace('w', '').replace('h', '')))
        largest = dim_list[-1]
        src = imgs[largest]
        dim = default_dim
        if 'w' in largest:
            dim = f"{largest.replace('w', '')},"
        if 'h' in largest:
            dim = f",{largest.replace('w', '')}"

        return dim, src

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

    @classmethod
    def tag_wrapper_inline_code(cls, tag: Tag, text: str, indent: int):
        if '\n' in text:
            # multiline code
            lang = tag.get('class', ['text'])
            lang = lang[0]
            lang = lang.replace('language-', '')
            ascii_content = f'''[source, {lang}]
----
{text}
----
'''
            return ascii_content
        else:
            # inline
            return f'`{text}`'

    @classmethod
    def tag_wrapper_default(cls, tag: Tag, text: str, indent: int):
        print(f'===UNSUPPORTED===: {tag.name}')
        # print(tag)
        return text

    def transform_tag(self, tag: Tag, indent_level=0) -> str:
        text = []
        if tag.name == 'table':
            return f'++++\n{tag.prettify()}\n++++\n\n'

        for t in tag.contents:
            if type(t) is NavigableString:
                if tag.name in ['ol', 'ul']:
                    continue
                m = re.match(r'^\n\s*$', str(t))
                if m is None:
                    text.append(str(t))
                # else:
                #     print('ONLY NEW LINE')

            elif type(t) is Tag:
                if tag.name in ['ol', 'ul']:
                    text.append(self.transform_tag(t, indent_level+1))
                else:
                    text.append(self.transform_tag(t, indent_level))

        wrapper_fmt = self.wrappers.get(tag.name, self.tag_wrapper_default)
        return wrapper_fmt(tag, ''.join(text), indent_level)

    def transform_v1(self):
        value = self.transform_tag(self.site)
        # cleanup large whitespace
        value = re.sub(r'(\n\s*){3,}', '\n\n', value)
        self.value = value
        return value

    def transform(self):
        visitor = AsciidocVisitor()
        value = visitor.visit(self.site, src_url=self.config['src_url'], output_dir=self.config['output_dir'])
        # print(value)
        # value = self.transform_tag(self.site)
        # cleanup large whitespace
        value = re.sub(r'(\n\s*){3,}', '\n\n', value)
        self.value = value
        return value

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
            file_out.write(f'= {title}\n\n')
            if len(description) > 0:
                file_out.write(description)
                file_out.write('\n\n')

    def render_chapter(self, extractor: Extractor, content: Transformer, src_url, basename: str):
        file_name = f'{basename}.asciidoc'
        self.file_list.append(file_name)
        file_path = os.path.join(self.output_dir, file_name)
        with open(file_path, 'w', encoding='utf-8') as file_out:
            file_out.write(f'== {extractor.get_title()}\n\n')

            time_published = extractor.get_published()
            if time_published is not None:
                published_info = f'published on {time_published}'
            else:
                published_info = ''
            article_metadata = f"'''\n" \
                               f"source: {src_url} {published_info}\n\n{extractor.get_metadata()}\n" \
                               f"'''\n"
            file_out.write(article_metadata)
            file_out.write(content.value)

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
        content = f'''= {self.config["title"]}
{self.config["author"]}
{self.config["version"]}
:doctype: book
:partnums:
:toc:
:imagesdir: images
:homepage: {self.config["homepage"]}

{included_files}
'''
        with open(os.path.join(self.output_dir, 'index.asciidoc'), 'w') as index_file:
            index_file.write(content)
