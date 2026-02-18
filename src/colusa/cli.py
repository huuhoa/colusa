import argparse
import sys
from typing import Any

from colusa import Colusa, ConfigurationError, logs


def main() -> None:
    args = parse_args()
    args.func(args)


def parse_args() -> argparse.Namespace:
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
    generate_parser.add_argument('--dry-run', action='store_true',
                                 help='Print what would be done without downloading or writing any files')

    crawler_parse = commands.add_parser('crawl',
                        help='Crawl an URL to generate list of URLs')
    crawler_parse.set_defaults(func=crawl_url)
    crawler_parse.add_argument('--url', '-u', type=str, help='URL to crawl')
    crawler_parse.add_argument('--output_dir', '-d', type=str, help='Output folder to store cached')
    crawler_parse.add_argument('--output', '-o', type=argparse.FileType('w'), default=sys.stdout, help='Output file (default: standard output)')

    add_url_parser = commands.add_parser('add-url',
                        help='Append a URL to an existing config file')
    add_url_parser.set_defaults(func=add_url)
    add_url_parser.add_argument('input', type=str, help='Config file (JSON or YAML)')
    add_url_parser.add_argument('url', type=str, help='URL or local file path to add')
    add_url_parser.add_argument('--title', type=str, default=None, help='Override title')
    add_url_parser.add_argument('--author', type=str, default=None, help='Override author')
    add_url_parser.add_argument('--published', type=str, default=None, help='Override published date')
    add_url_parser.add_argument('--part', type=str, default=None,
                                help='Part title to add to (multi-part books only)')
    add_url_parser.add_argument('--fetch-title', action='store_true',
                                help='Download the page and extract the title automatically')

    return parser.parse_args()


def init(args: argparse.Namespace) -> None:
    try:
        Colusa.generate_new_configuration(args.output)
    except ConfigurationError as e:
        logs.error(e)


def generate(args: argparse.Namespace) -> None:
    try:
        if args.dry_run:
            Colusa.dry_run_book(args.input)
        else:
            Colusa.generate_book(args.input)
    except ConfigurationError as e:
        logs.error(e)


def add_url(args: argparse.Namespace) -> None:
    try:
        Colusa.add_url(
            config_path=args.input,
            url=args.url,
            title=args.title,
            author=args.author,
            published=args.published,
            part=args.part,
            fetch_title=args.fetch_title,
        )
    except ConfigurationError as e:
        logs.error(e)
        raise SystemExit(1)


def crawl_url(args: argparse.Namespace) -> None:
    from colusa import Crawler
    try:
        crawler = Crawler(args.url, args.output_dir, args.output)
        crawler.run()
    except ConfigurationError as e:
        logs.error(e)


if __name__ == '__main__':
    main()
