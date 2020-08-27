#!/usr/bin/env python3

from bs4 import BeautifulSoup
import requests
import os
import hashlib
from urllib.parse import urlparse


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


def transform_tag_p(file_out, tag):
    file_out.write(tag.text)
    file_out.write('\n\n')


def transform_tag_h1(file_out, tag):
    file_out.write('== %s\n\n' % tag.string)


def transform_tag_h2(file_out, tag):
    file_out.write('=== %s\n\n' % tag.string)


def transform_tag_h3(file_out, tag):
    file_out.write('==== %s\n\n' % tag.string)


def transform_tag_ul(file_out, tag):
    for li in tag:
        if li.name != 'li':
            continue
        file_out.write('- %s\n' % li.text)
    file_out.write('\n\n')


def transform_tag_ol(file_out, tag):
    for li in tag:
        if li.name != 'li':
            continue
        file_out.write('* %s\n' % li.text)
    file_out.write('\n\n')


def transform_tag_div(file_out, div):
    render_tags(file_out, div)


def transform_tag_blockquote(file_out, tag):
    file_out.write('[quote]\n')
    file_out.write('____\n')
    render_tags(file_out, tag)
    file_out.write('____\n')


handlers = {
    'p': transform_tag_p,
    'h1': transform_tag_h1,
    'h2': transform_tag_h2,
    'h3': transform_tag_h3,
    'ul': transform_tag_ul,
    'ol': transform_tag_ol,
    'div': transform_tag_div,
    'blockquote': transform_tag_blockquote,
    'figure': transform_tag_p,
}


def render_tags(file_out, site):
    for tag in site:
        if tag.name is None:
            continue
        if tag.name in handlers:
            handlers[tag.name](file_out, tag)
        else:
            print('=============')
            print(tag)

        # print(tag)


def transform_strong(site):
    for a in site.find_all(['strong', 'b']):
        text = a.text
        repl = '**%s**' % text
        a.replace_with(repl)


def transform_italic(site):
    for a in site.find_all(['italic', 'i']):
        text = a.text
        repl = '__%s__' % text
        a.replace_with(repl)


def transform_a(site):
    for a in site.find_all('a'):
        href = a['href']
        text = a.text
        repl = 'link:%s[%s]' % (href, text)
        a.replace_with(repl)


def transform_img(site):
    for img in site.findAll('img'):
        alt = img['alt']
        height = img['height']
        width = img['width']
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
        repl = 'image:%s[%s,%s,%s]' % (src, alt, width, height)
        img.replace_with(repl)


def download_content(url_path):
    m = hashlib.sha256()
    m.update(url_path.encode('utf-8'))
    os.makedirs(".cached", exist_ok=True)
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

        a_out.write("== %s\n\n" % bs.find('h1').text)
        time_published = bs.find('time', attrs={'class': 'entry-date published'})
        if time_published is not None:
            published = time_published.text
            a_out.write('**published**: %s\n\n' % published)
        site = bs.find(id='page')
        remove_tag(site, 'div', attrs={'class': 'site-branding'})
        remove_tag(site, 'div', attrs={'class': 'navigation-top'})
        remove_tag(site, 'footer', attrs={'class': 'site-footer'})
        remove_tag(site, 'div', attrs={'class': 'searchsettings'})
        remove_tag(site, 'section', attrs={'id': 'ajaxsearchlitewidget-2'})
        remove_tag(site, 'aside', attrs={'id': 'secondary'})
        remove_tag(site, 'nav', attrs={'class': 'post-navigation'})
        remove_tag(site, 'header', attrs={'id': 'masthead'})
        b_content = site.find(attrs={'class': 'entry-content'})
        transform_strong(b_content)
        transform_italic(b_content)
        transform_img(b_content)
        transform_a(b_content)
        render_tags(a_out, b_content)
        # a_out.write(site.prettify())


def main():
    paths = [
        "https://unintendedconsequenc.es/tiktok-ban-openness-trap/",
        "https://unintendedconsequenc.es/garmin-hack-and-dependence/",
        'https://unintendedconsequenc.es/a-second-step/',
        'https://unintendedconsequenc.es/scaling-a-scam/',
        'https://unintendedconsequenc.es/bezmenovs-steps/',
        'https://unintendedconsequenc.es/blank-paper/',
        'https://unintendedconsequenc.es/crumpled-butterfly/',
        'https://unintendedconsequenc.es/loop-in-loop-out/',
        'https://unintendedconsequenc.es/inevitable-surveillance/',
        'https://unintendedconsequenc.es/fff/',
        'https://unintendedconsequenc.es/changes-in-value-part-2/',
        'https://unintendedconsequenc.es/asylum-from-a-pack-of-wolves/',
        'https://unintendedconsequenc.es/modeling-epidemics/',
        'https://unintendedconsequenc.es/pandemic-protests/',
        'https://unintendedconsequenc.es/a-religion-of-isolation/',
    ]
    for url_path in paths:
        download_content(url_path)


if __name__ == '__main__':
    main()
