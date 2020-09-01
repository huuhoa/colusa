import hashlib
import os
import re
import shutil
from urllib.parse import urlparse

import requests
from bs4 import NavigableString, Tag, PageElement


class Extractor(object):
    """Extractor extract real article content from sea of other contents"""
    def __init__(self, bs):
        self.bs = bs
        self.site = None
        self.content = None
        self.internal_init()

    def get_title(self):
        pass

    def get_published(self):
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
        self.site = self.bs.find('div', class_='entry-content')


class Transformer(object):
    """Transformer transform some html tags into asciidoc syntax"""
    def __init__(self, config, doc, site):
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
            'ul': self.tag_wrapper_ul,
            'ol': self.tag_wrapper_ol,
            'li': self.tag_wrapper_li,
            'img': self.tag_wrapper_img,
            'blockquote': self.tag_wrapper_quote,
            'figure': self.tag_wrapper_figure,
            'figcaption': self.tag_wrapper_figurecaption,
        }

        self.config = config
        self.doc = doc
        self.site = site

    @classmethod
    def tag_wrapper_cleanup(cls, text: str) -> str:
        text = text.strip()
        rex = re.compile(r'\n\s*')
        text = re.sub(rex, ' ', text)
        return text

    @classmethod
    def tag_wrapper_a(cls, tag: Tag, text: str, ident: int):
        href = tag.get("href", "")
        m = re.match(r'https?://', href)
        if m is None:
            return text
        else:
            return f'link:{href}[{text}]'

    @classmethod
    def tag_wrapper_italic(cls, tag: Tag, text: str, ident: int):
        return f'__{text}__'

    @classmethod
    def tag_wrapper_strong(cls, tag: Tag, text: str, ident: int):
        return f'**{text}**'

    @classmethod
    def tag_wrapper_h1(cls, tag: Tag, text: str, ident: int):
        return f'=== {cls.tag_wrapper_cleanup(text)}\n\n'

    @classmethod
    def tag_wrapper_h2(cls, tag: Tag, text: str, ident: int):
        return f'=== {cls.tag_wrapper_cleanup(text)}\n\n'

    @classmethod
    def tag_wrapper_h3(cls, tag: Tag, text: str, ident: int):
        return f'==== {cls.tag_wrapper_cleanup(text)}\n\n'

    @classmethod
    def tag_wrapper_h4(cls, tag: Tag, text: str, ident: int):
        return f'===== {cls.tag_wrapper_cleanup(text)}\n\n'

    @classmethod
    def tag_wrapper_h5(cls, tag: Tag, text: str, ident: int):
        return f'====== {cls.tag_wrapper_cleanup(text)}\n\n'

    @classmethod
    def tag_wrapper_h6(cls, tag: Tag, text: str, ident: int):
        return f'======= {cls.tag_wrapper_cleanup(text)}\n\n'

    @classmethod
    def tag_wrapper_p(cls, tag: Tag, text: str, ident: int):
        return f'{text}\n\n'

    @classmethod
    def tag_wrapper_span(cls, tag: Tag, text: str, ident: int):
        return text

    @classmethod
    def tag_wrapper_ul(cls, tag: Tag, text: str, ident: int):
        return f'{text}\n'

    @classmethod
    def tag_wrapper_ol(cls, tag: Tag, text: str, ident: int):
        return f'{text}\n'

    @classmethod
    def tag_wrapper_li(cls, tag: Tag, text: str, ident: int):
        if tag.parent.name == 'ol':
            return f'{"." * ident} {text}\n'
        else:
            return f'{"*" * ident} {text}\n'

    @classmethod
    def tag_wrapper_quote(cls, tag: Tag, text: str, ident: int):
        return f'[quote]\n____\n{text}\n____\n\n'

    @classmethod
    def tag_wrapper_figure(cls, tag: Tag, text: str, ident: int):
        return f'{text}\n'

    @classmethod
    def tag_wrapper_figurecaption(cls, tag: Tag, text: str, ident: int):
        return f'\n{text}\n'

    def tag_wrapper_img(self, img: Tag, text: str, ident: int):
        alt = img['alt']
        height = img.get('height', '')
        width = img.get('width', '')
        src = img['src']
        srcset = img.get('srcset', None)
        if srcset is not None:
            srcs = srcset.split(',')
            imgs = {}
            for s in srcs:
                ss = s.strip().split(' ')
                imgs[ss[1]] = ss[0]
            largest = sorted(imgs.keys())[0]
            src = imgs[largest]
            if 'w' in largest:
                width = largest.replace('w', '')
            if 'h' in largest:
                height = largest.replace('h', '')
        url_path = requests.compat.urljoin(self.config['src_url'], src)
        image_name = self.download_image(url_path, self.config['output_dir'])
        return f'image:{image_name}[{alt},{width},{height}]'

    @classmethod
    def tag_wrapper_default(cls, tag: Tag, text: str, ident: int):
        print(f'===UNSUPPORTED===: {tag.name}')
        return text

    @classmethod
    def compute_image_path(cls, url_path, root):
        m = hashlib.sha256()
        m.update(url_path.encode('utf-8'))
        os.makedirs(os.path.join(root, ".cached"), exist_ok=True)

        u_path = urlparse(url_path)
        output_path = u_path.path
        output_path = os.path.splitext(output_path)
        image_name = f'{m.hexdigest()}{output_path[1]}'
        file_path = os.path.join(root, "images", image_name)
        return file_path, image_name

    @classmethod
    def download_image(cls, url_path, root):
        image_path, image_name = cls.compute_image_path(url_path, root)
        if os.path.exists(image_path):
            return image_name
        else:
            headers = {
                'Accept': '*/*',
                'User-Agent': 'curl/7.64.1',
            }
            req = requests.get(url_path, headers=headers, stream=True)
            if req.status_code != 200:
                print(f'Cannot make request. Result: {req.status_code:d}')
                exit(1)

            with open(image_path, 'wb') as file_out:
                req.raw.decode_content = True
                shutil.copyfileobj(req.raw, file_out)

            return image_name

    def transform_tag(self, tag: Tag, ident_level=0) -> str:
        text = []
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
                    text.append(self.transform_tag(t, ident_level+1))
                else:
                    text.append(self.transform_tag(t, ident_level))

        wrapper_fmt = self.wrappers.get(tag.name, self.tag_wrapper_default)
        return wrapper_fmt(tag, ''.join(text), ident_level)

    def transform_strong(self):
        for a in self.site.find_all(['strong', 'b']):
            text = a.text
            a.replace_with(f'**{text}**')

    def transform_italic(self):
        for a in self.site.find_all(['italic', 'i', 'em']):
            value = self.transform_tag(a)
            a.replace_with(value)

    def transform_a(self):
        for a in self.site.find_all('a', attrs={'href': re.compile("^https?://")}):
            href = a['href']
            text = a.text
            a.replace_with(f'link:{href}[{text}]')

    def transform_img(self):
        for img in self.site.find_all('img'):
            alt = img['alt']
            height = img.get('height', '')
            width = img.get('width', '')
            src = img['src']
            srcset = img.get('srcset', None)
            if srcset is not None:
                srcs = srcset.split(',')
                imgs = {}
                for s in srcs:
                    ss = s.strip().split(' ')
                    imgs[ss[1]] = ss[0]
                largest = sorted(imgs.keys())[0]
                src = imgs[largest]
                if 'w' in largest:
                    width = largest.replace('w', '')
                if 'h' in largest:
                    height = largest.replace('h', '')
            url_path = requests.compat.urljoin(self.config['src_url'], src)
            image_name = self.download_image(url_path, self.config['output_dir'])
            repl = f'image:{image_name}[{alt},{width},{height}]'
            img.replace_with(repl)

    def transform(self):
        value = self.transform_tag(self.site)
        self.site.replace_with(value)
        return value
        # self.transform_strong()
        # self.transform_italic()
        # self.transform_img()
        # self.transform_a()


class Renderer(object):
    """Renderer render supported html tags into asciidoc syntax"""
    def render_tag_p(self, file_out, tag):
        file_out.write(tag.text)
        file_out.write('\n\n')

    def render_tag_h1(self, file_out, tag):
        text = tag.text.strip()
        rex = re.compile(r'\n\s*')
        text = re.sub(rex, ' ', text)
        file_out.write(f'=== {text}\n\n')

    def render_tag_h2(self, file_out, tag):
        text = tag.text.strip()
        rex = re.compile(r'\n\s*')
        text = re.sub(rex, ' ', text)
        file_out.write(f'=== {text}\n\n')

    def render_tag_h3(self, file_out, tag):
        text = tag.text.strip()
        rex = re.compile(r'\n\s*')
        text = re.sub(rex, ' ', text)
        file_out.write(f'==== {text}\n\n')

    def render_tag_h4(self, file_out, tag):
        text = tag.text.strip()
        rex = re.compile(r'\n\s*')
        text = re.sub(rex, ' ', text)
        file_out.write(f'===== {text}\n\n')

    def render_tag_h5(self, file_out, tag):
        text = tag.text.strip()
        rex = re.compile(r'\n\s*')
        text = re.sub(rex, ' ', text)
        file_out.write(f'====== {text}\n\n')

    def render_tag_ul(self, file_out, tag):
        for li in tag:
            if li.name != 'li':
                continue
            file_out.write(f'- {li.text}\n')
        file_out.write('\n\n')

    def render_tag_ol(self, file_out, tag):
        for li in tag:
            if li.name != 'li':
                continue
            file_out.write(f'* {li.text}\n')
        file_out.write('\n\n')

    def render_tag_div(self, file_out, div):
        self.render_tags(file_out, div)

    def render_tag_blockquote(self, file_out, tag):
        file_out.write('[quote]\n')
        file_out.write('____\n')
        self.render_tags(file_out, tag)
        file_out.write('____\n\n')

    def render_tag_table(self, file_out, tag):
        file_out.write('++++\n')
        file_out.write(tag.prettify())
        file_out.write('\n++++\n\n')

    def render_tag_pre(self, file_out, tag):
        code_pattern = r"^\[code\s+lang=(?P<lang>.*)\](?P<content>.*)\[\/code\]$"
        matches = re.finditer(code_pattern, tag.text, re.MULTILINE | re.DOTALL)

        for matchNum, match in enumerate(matches, start=1):
            ascii_content = f'''[source, {match.group('lang')}]
----
{match.group('content')}
----
'''
            file_out.write(ascii_content)

        if matches is None:
            file_out.write(f'''[listing]
....
{tag.text}
....

''')

    def render_tags(self, file_out, site):
        handlers = {
            'p': self.render_tag_p,
            'h1': self.render_tag_h1,
            'h2': self.render_tag_h2,
            'h3': self.render_tag_h3,
            'h4': self.render_tag_h4,
            'h5': self.render_tag_h5,
            'ul': self.render_tag_ul,
            'ol': self.render_tag_ol,
            'div': self.render_tag_div,
            'blockquote': self.render_tag_blockquote,
            'figure': self.render_tag_p,
            'table': self.render_tag_table,
            'pre': self.render_tag_pre,
            'span': self.render_tag_p,
        }
        file_out.write(site)
        return
        for tag in site:
            if tag.name is None:
                continue
            if tag.name in handlers:
                handlers[tag.name](file_out, tag)
            else:
                print('=============')
                print(tag)
