#!/usr/bin/env python3

from bs4 import BeautifulSoup
import requests
import os
import hashlib
from urllib.parse import urlparse
import re
import shutil


def compute_image_path(url_path):
    m = hashlib.sha256()
    m.update(url_path.encode('utf-8'))
    os.makedirs(".cached", exist_ok=True)

    u_path = urlparse(url_path)
    output_path = u_path.path
    output_path = os.path.splitext(output_path)
    image_name = "%s%s" % (m.hexdigest(), output_path[1])
    file_path = os.path.join("images", image_name)
    return file_path, image_name


def download_image(url_path):
    print('img src: %s' % url_path)
    image_path, image_name = compute_image_path(url_path)
    print(image_path)
    if os.path.exists(image_path):
        return image_name
    else:
        headers = {
            'Accept': '*/*',
            'User-Agent': 'curl/7.64.1',
        }
        req = requests.get(url_path, headers=headers, stream=True)
        if req.status_code != 200:
            print("Cannot make request. Result: %d" % (req.status_code))
            exit(1)

        with open(image_path, 'wb') as file_out:
            req.raw.decode_content = True
            shutil.copyfileobj(req.raw, file_out)

        return image_name


def load_file_content(url_path, file_path):
    if os.path.exists(file_path):
        with open(file_path, 'rt') as file_in:
            content = file_in.read()
    else:
        headers = {
            'Accept': '*/*',
            'User-Agent': 'curl/7.64.1',
        }
        req = requests.get(url_path, headers=headers)
        if req.status_code != 200:
            print("Cannot make request. Result: %d" % (req.status_code))
            exit(1)

        with open(file_path, 'wt') as file_out:
            file_out.write(req.text)

        content = req.text
    return content


def remove_tag(site, tag, attrs):
    b = site.find(tag, attrs=attrs)
    if b is not None:
        b.extract()


class Renderer(object):
    def render_tag_p(self, file_out, tag):
        file_out.write(tag.text)
        file_out.write('\n\n')

    def render_tag_h1(self, file_out, tag):
        file_out.write('== %s\n\n' % tag.string)

    def render_tag_h2(self, file_out, tag):
        file_out.write('=== %s\n\n' % tag.string)

    def render_tag_h3(self, file_out, tag):
        file_out.write('==== %s\n\n' % tag.string)

    def render_tag_h4(self, file_out, tag):
        file_out.write('===== %s\n\n' % tag.string)

    def render_tag_ul(self, file_out, tag):
        for li in tag:
            if li.name != 'li':
                continue
            file_out.write('- %s\n' % li.text)
        file_out.write('\n\n')

    def render_tag_ol(self, file_out, tag):
        for li in tag:
            if li.name != 'li':
                continue
            file_out.write('* %s\n' % li.text)
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
        }
        for tag in site:
            if tag.name is None:
                continue
            if tag.name in handlers:
                handlers[tag.name](file_out, tag)
            else:
                print('=============')
                print(tag)


class UntoolsRenderer(Renderer):
    def render_tag_div(self, file_out, div):
        file_out.write(div.text)
        file_out.write('\n\n')


class Transformer(object):
    def __init__(self, doc, site):
        self.doc = doc
        self.site = site

    def transform_strong(self):
        for a in self.site.find_all(['strong', 'b']):
            text = a.text
            repl = '**%s**' % text
            a.replace_with(repl)

    def transform_italic(self):
        for a in self.site.find_all(['italic', 'i']):
            text = a.text
            repl = '__%s__' % text
            a.replace_with(repl)

    def transform_a(self):
        for a in self.site.find_all('a'):
            href = a['href']
            text = a.text
            repl = 'link:%s[%s]' % (href, text)
            a.replace_with(repl)

    def transform_img(self):
        for img in self.site.findAll('img'):
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
            image_name = download_image(src)
            repl = 'image:%s[%s,%s,%s]' % (image_name, alt, width, height)
            print(repl)
            img.replace_with(repl)

    def transform(self):
        self.transform_strong()
        self.transform_italic()
        self.transform_img()
        self.transform_a()


class UntoolsTransformer(Transformer):
    def transform_h2(self):
        for a in self.site.find_all('h2'):
            text = a.text
            repl = '=== %s\n\n' % text
            p = self.doc.new_tag('p')
            p.string = repl
            a.replace_with(p)

    def transform_h3(self):
        for a in self.site.find_all('h3'):
            text = a.text
            repl = '==== %s\n\n' % text
            p = self.doc.new_tag('p')
            p.string = repl
            a.replace_with(p)

    def transform_sources(self):
        source = self.site.find('div', class_=re.compile('article-module--sources--'))
        source.unwrap()

    def transform(self):
        self.transform_strong()
        self.transform_italic()
        self.transform_img()
        self.transform_a()
        # self.transform_h2()
        # self.transform_h3()
        self.transform_sources()


class Extracter(object):
    def __init__(self, bs):
        self.bs = bs
        self.site = None
        self.content = None

    def get_title(self):
        pass

    def get_published(self):
        pass

    def cleanup(self):
        pass

    def get_content(self):
        pass


class Untools(Extracter):
    def get_title(self):
        import re
        header = self.bs.find('div', class_=re.compile('article-module--top--'))
        title = header.find('h2').text
        tag = header.find('span', class_=re.compile('tag-module--tag--')).text
        usage = header.find('div', class_=re.compile('article-module--when-useful--')).text

        return '%s\n\n.%s\n****\n%s\n****\n' % (title, tag, usage)

    def get_published(self):
        time_published = self.bs.find('time', attrs={'class': 'entry-date published'})
        if time_published is not None:
            published = time_published.text
            return published
        else:
            return None

    def cleanup(self):
        self.site = self.bs.find(class_=re.compile('article-module--content--'))
        remove_tag(self.site, 'div', attrs={'class': 'site-branding'})
        remove_tag(self.site, 'div', attrs={'class': 'navigation-top'})
        remove_tag(self.site, 'footer', attrs={'class': 'site-footer'})
        remove_tag(self.site, 'div', attrs={'class': 'searchsettings'})
        remove_tag(self.site, 'section', attrs={'id': 'ajaxsearchlitewidget-2'})
        remove_tag(self.site, 'aside', attrs={'id': 'secondary'})
        remove_tag(self.site, 'nav', attrs={'class': 'post-navigation'})
        remove_tag(self.site, 'header', attrs={'id': 'masthead'})

    def get_content(self):
        return self.site


class UnintendedSequences(Extracter):
    def get_title(self):
        return self.bs.find('h1').text

    def get_published(self):
        time_published = self.bs.find('time', attrs={'class': 'entry-date published'})
        if time_published is not None:
            published = time_published.text
            return published
        else:
            return None

    def cleanup(self):
        self.site = self.bs.find(id='page')
        remove_tag(self.site, 'div', attrs={'class': 'site-branding'})
        remove_tag(self.site, 'div', attrs={'class': 'navigation-top'})
        remove_tag(self.site, 'footer', attrs={'class': 'site-footer'})
        remove_tag(self.site, 'div', attrs={'class': 'searchsettings'})
        remove_tag(self.site, 'section', attrs={'id': 'ajaxsearchlitewidget-2'})
        remove_tag(self.site, 'aside', attrs={'id': 'secondary'})
        remove_tag(self.site, 'nav', attrs={'class': 'post-navigation'})
        remove_tag(self.site, 'header', attrs={'id': 'masthead'})

    def get_content(self):
        return self.site.find(attrs={'class': 'entry-content'})


def download_content(url_path):
    m = hashlib.sha256()
    m.update(url_path.encode('utf-8'))
    file_path = os.path.join(".cached", "%s.html" % m.hexdigest())
    output_path = urlparse(url_path).path
    output_path = output_path.rstrip('/')
    output_path = os.path.basename(output_path)
    os.makedirs(output_path, exist_ok=True)
    output_path = os.path.join(output_path, 'index.asciidoc')
    print(output_path)

    content = load_file_content(url_path, file_path)
    bs = BeautifulSoup(content, 'html.parser')

    with open(output_path, 'w') as a_out:
        extracter = Untools(bs)
        a_out.write("== %s\n\n" % extracter.get_title())
        time_published = extracter.get_published()
        if time_published is not None:
            a_out.write('**published**: %s\n\n' % time_published)
        extracter.cleanup()
        transformer = UntoolsTransformer(bs, extracter.get_content())
        transformer.transform()
        renderer = UntoolsRenderer()
        renderer.render_tags(a_out, extracter.get_content())


def main():
    paths = [
        'https://untools.co/cynefin-framework',
        'https://untools.co/decision-matrix',
        'https://untools.co/ladder-of-inference',
        'https://untools.co/confidence-determines-speed-vs-quality',
        'https://untools.co/second-order-thinking',
        'https://untools.co/hard-choice-model',
        'https://untools.co/iceberg-model',
        'https://untools.co/connection-circles',
        'https://untools.co/balancing-feedback-loop',
        'https://untools.co/reinforcing-feedback-loop',
        'https://untools.co/inversion',
        'https://untools.co/issue-trees',
        'https://untools.co/first-principles',
        'https://untools.co/abstraction-laddering',
    ]

    os.makedirs(".cached", exist_ok=True)
    os.makedirs("images", exist_ok=True)

    for url_path in paths:
        download_content(url_path)


if __name__ == '__main__':
    main()
