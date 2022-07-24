import argparse
import sys

from colusa import Colusa, ConfigurationError, logs


def main():
    args = parse_args()
    args.func(args)


def parse_args():
    parser = argparse.ArgumentParser()

    commands = parser.add_subparsers(dest='command')
    commands.required = True

    init_parser = commands.add_parser('init',
                                      help='Generate configuration file with basic structure which '
                                           'contains every input fields required by colusa')
    init_parser.set_defaults(func=init)
    init_parser.add_argument('output', type=str, help='Configuration file. '
                                                      'File extension should be either json or yml')

    generate_parser = commands.add_parser('generate',
                                          help='Generate ebook source data based on input configuration')
    generate_parser.set_defaults(func=generate)
    generate_parser.add_argument('input', type=str, help='Configuration file. '
                                                         'File extension should be either json or yml')

    crawler_parse = commands.add_parser('crawl',
                        help='Crawl an URL to generate list of URLs')
    crawler_parse.set_defaults(func=crawl_url)
    crawler_parse.add_argument('--url', '-u', type=str, help='URL to crawl')
    crawler_parse.add_argument('--output_dir', '-d', type=str, help='Output folder to store cached')
    crawler_parse.add_argument('--output', '-o', type=argparse.FileType('w'), default=sys.stdout, help='Output file (default: standard output)')

    return parser.parse_args()


def init(args):
    try:
        Colusa.generate_new_configuration(args.output)
    except ConfigurationError as e:
        logs.error(e)


def generate(args):
    try:
        Colusa.generate_book(args.input)
    except ConfigurationError as e:
        logs.error(e)


def crawl_url(args):
    from colusa import Crawler
    try:
        crawler = Crawler(args.url, args.output_dir, args.output)
        crawler.run()
    except ConfigurationError as e:
        logs.error(e)


if __name__ == '__main__':
    main()
