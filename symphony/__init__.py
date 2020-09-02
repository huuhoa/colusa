__author__ = "Huu Hoa NGUYEN (huuhoa@gmail.com)"
__version__ = "0.2.0"
__copyright__ = "Copyright (c) 2020 Huu Hoa NGUYEN"
# Use of this source code is governed by the MIT license.
__license__ = "MIT"


import argparse
import json
import os
import pathlib

from bs4 import BeautifulSoup


class Symphony(object):
    def __init__(self, configuration: dict):
        self.config = configuration
        self.output_dir = configuration['output_dir']

    def download_content(self, url_path):
        from .utils import download_url, get_hexdigest

        output_path = pathlib.Path(self.output_dir)
        cached_file_path = output_path.joinpath('.cached', f'{get_hexdigest(url_path)}.html')
        p = pathlib.PurePath(url_path)
        output_file_name = f'{p.name}.asciidoc'
        output_file_path = output_path.joinpath(output_file_name)
        print(output_file_path)

        if not cached_file_path.exists():
            # download file from url_path
            download_url(url_path, str(cached_file_path))

        with open(cached_file_path, 'rt', encoding='utf-8') as file_in:
            content = file_in.read()
        return content, output_file_path, output_file_name

    def ebook_generate_content(self, url_path, content, output_path):
        from .etr_factory import create_extractor, create_transformer

        bs = BeautifulSoup(content, 'html.parser')

        with open(output_path, 'w', encoding='utf-8') as file_out:
            extractor = create_extractor(url_path, bs)
            file_out.write(f'== {extractor.get_title()}\n\n')

            time_published = extractor.get_published()
            if time_published is not None:
                published_info = f'published on {time_published}'
            else:
                published_info = ''
            article_metadata = f"'''\n" \
                               f"source: {url_path} {published_info}\n\n{extractor.get_metadata()}\n" \
                               f"'''\n"
            file_out.write(article_metadata)

            extractor.cleanup()
            transformer = create_transformer(url_path, extractor.get_content(), self.output_dir)
            value = transformer.transform()
            file_out.write(value)

    @classmethod
    def generate_new_configuration(cls, file_path):
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

    def ebook_generate_master_file(self, files: list):
        """ Generate master index.asciidoc to include all book related information such as
        - book title
        - book author
        - book version
        - etc
        - and include all generated asciidoc files from `urls`
        """
        included_files = '\n'.join(['include::%s[]' % x for x in files])
        content = f'''= {self.config["title"]}
{self.config["author"]}
{self.config["version"]}
:toc:
:imagesdir: images
:homepage: {self.config["homepage"]}

{included_files}
'''
        with open(os.path.join(self.output_dir, 'index.asciidoc'), 'w') as index_file:
            index_file.write(content)

    def main(self):
        paths = self.config['urls']
        os.makedirs(os.path.join(self.output_dir, ".cached"), exist_ok=True)
        os.makedirs(os.path.join(self.output_dir, "images"), exist_ok=True)
        self.generate_makefile()

        files = []
        for url_path in paths:
            content, output_path, relative_path = self.download_content(url_path)
            self.ebook_generate_content(url_path, content, output_path)
            files.append(relative_path)

        self.ebook_generate_master_file(files)


def read_configuration_file(file_path):
    with open(file_path, 'r') as file_in:
        data = json.load(file_in)
        return data


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--new', '-n', type=bool, default=False,
                        help='Generate new configuration file. '
                             'File name will be specified in the --input parameter')
    parser.add_argument('--input', '-i', type=str, help='Configuration file')
    args = parser.parse_args()
    if args.new:
        symp = Symphony()
        symp.generate_new_configuration(args.input)
        exit(0)

    configs = read_configuration_file(args.input)
    symp = Symphony(configs)
    symp.main()
