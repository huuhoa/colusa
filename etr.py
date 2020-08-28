import hashlib
import os
import re
import shutil
from urllib.parse import urlparse

import requests


class Extractor(object):
    """Extractor extract real article content from sea of other contents"""
    def __init__(self, bs):
        self.bs = bs
        self.site = None
        self.content = None

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


class Transformer(object):
    """Transformer transform some html tags into asciidoc syntax"""
    def __init__(self, config, doc, site):
        self.config = config
        self.doc = doc
        self.site = site

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

    def transform_strong(self):
        for a in self.site.find_all(['strong', 'b']):
            text = a.text
            a.replace_with(f'**{text}**')

    def transform_italic(self):
        for a in self.site.find_all(['italic', 'i', 'em']):
            text = a.text
            a.replace_with(f'__{text}__')

    def transform_a(self):
        for a in self.site.find_all('a'):
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
        self.transform_strong()
        self.transform_italic()
        self.transform_img()
        self.transform_a()


class Renderer(object):
    """Renderer render supported html tags into asciidoc syntax"""
    def render_tag_p(self, file_out, tag):
        file_out.write(tag.text)
        file_out.write('\n\n')

    def render_tag_h1(self, file_out, tag):
        file_out.write(f'=== {tag.string}\n\n')

    def render_tag_h2(self, file_out, tag):
        file_out.write(f'=== {tag.string}\n\n')

    def render_tag_h3(self, file_out, tag):
        file_out.write(f'==== {tag.string}\n\n')

    def render_tag_h4(self, file_out, tag):
        file_out.write(f'===== {tag.string}\n\n')

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
        file_out.write('____\n')

    def render_tag_table(self, file_out, tag):
        file_out.write('++++\n')
        file_out.write(tag.prettify())
        file_out.write('++++\n')

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
            'ul': self.render_tag_ul,
            'ol': self.render_tag_ol,
            'div': self.render_tag_div,
            'blockquote': self.render_tag_blockquote,
            'figure': self.render_tag_p,
            'table': self.render_tag_table,
            'pre': self.render_tag_pre,
        }
        for tag in site:
            if tag.name is None:
                continue
            if tag.name in handlers:
                handlers[tag.name](file_out, tag)
            else:
                print('=============')
                print(tag)
