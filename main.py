#!/usr/bin/env python3

import argparse
import hashlib
import json
import os
import re
from urllib.parse import urlparse

import requests
from bs4 import BeautifulSoup


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
            print(f'Cannot make request. Result: {req.status_code:d}')
            exit(1)

        with open(file_path, 'wt') as file_out:
            file_out.write(req.text)

        content = req.text
    return content


def download_content(url_path, root, **kwargs):
    from etr_factory import create_extractor, create_transformer, create_renderer

    m = hashlib.sha256()
    m.update(url_path.encode('utf-8'))
    file_path = os.path.join(root, ".cached", "%s.html" % m.hexdigest())
    output_path = urlparse(url_path).path
    output_path = output_path.rstrip('/')
    output_path = os.path.join(root, os.path.basename(output_path))
    os.makedirs(output_path, exist_ok=True)
    output_path = os.path.join(output_path, 'index.asciidoc')
    print(output_path)

    content = load_file_content(url_path, file_path)
    bs = BeautifulSoup(content, 'html.parser')

    with open(output_path, 'w') as a_out:
        extractor = create_extractor(url_path, bs, **kwargs)
        a_out.write(f'== {extractor.get_title()}\n\n')

        time_published = extractor.get_published()
        if time_published is not None:
            published_info = f'published on {time_published}'
        else:
            published_info = ''
        article_metadata = f'link:{url_path}[original article] {published_info}\n\n{extractor.get_metadata()}'
        a_out.write(article_metadata)

        extractor.cleanup()
        transformer = create_transformer(url_path, bs, extractor.get_content(), root)
        transformer.transform()
        renderer = create_renderer(url_path)
        renderer.render_tags(a_out, extractor.get_content())
    return output_path


def read_configuration(file_path):
    with open(file_path, 'r') as file_in:
        data = json.load(file_in)
        return data


def generate_new_configuration(file_path):
    template = {
            "title": "__fill the title__",
            "author": "__fill the author__",
            "version": "v1.0",
            "homepage": "__fill url to home page__",
            "output_dir": "__fill output dir__",
            "urls": [
            ]
        }
    with open(file_path, 'w') as file_out:
        json.dump(template, file_out, indent=4)


def generate_makefile(output_dir):
    template = '''html:
\tasciidoctor index.asciidoc -d book -b html5 -D output
\tcp -r images output/

epub:
\tasciidoctor-epub3 index.asciidoc -d book -D output

pdf:
\tasciidoctor-pdf index.asciidoc -d book -D output
'''
    file_path = os.path.join(output_dir, 'Makefile')
    with open(file_path, 'w') as out_file:
        out_file.write(template)


def create_experiment_config(config):
    return {
        'experiment': True,
        'config': config.get('etr'),
    }


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--new', '-n', type=bool, default=False,
                        help='Generate new configuration file. '
                             'File name will be specified in the --input parameter')
    parser.add_argument('--input', '-i', type=str, help='Configuration file')
    parser.add_argument('--experiment', '-e', type=bool, default=False,
                        help='Experiment mode. When True, symphony will work in experiment/unstable mode')
    args = parser.parse_args()
    if args.new:
        generate_new_configuration(args.input)
        exit(0)

    config = read_configuration(args.input)
    paths = config['urls']
    root = config['output_dir']
    os.makedirs(os.path.join(root, ".cached"), exist_ok=True)
    os.makedirs(os.path.join(root, "images"), exist_ok=True)
    generate_makefile(root)

    files = []
    if args.experiment:
        params = create_experiment_config(config)
    else:
        params = {}

    for url_path in paths:
        output_path = download_content(url_path, root, **params)
        output_path = re.sub(f'^{root}/', '', output_path)
        files.append(output_path)

    included_files = '\n'.join(['include::%s[]' % x for x in files])
    content = f'''= {config["title"]}
{config["author"]}
{config["version"]}
:toc:
:imagesdir: images
:homepage: {config["homepage"]}

{included_files}
'''
    with open(os.path.join(root, 'index.asciidoc'), 'w') as index_file:
        index_file.write(content)


if __name__ == '__main__':
    main()
