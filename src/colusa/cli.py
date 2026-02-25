import argparse
import sys
from typing import Any

from colusa import Colusa, ConfigurationError, logs


def main() -> None:
    args = parse_args()
    args.func(args)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description='Download web articles and compile them into ebooks (HTML, EPUB, PDF).',
        epilog=(
            'Typical workflow:\n'
            '  1. colusa init book.json           create a config file\n'
            '  2. colusa add-url book.json <url>  add articles (repeat as needed)\n'
            '  3. colusa generate book.json       download and convert to AsciiDoc\n'
            '  4. colusa build book.json          compile to ebook formats\n'
            '\n'
            'Exit codes: 0 = success, 1 = error'
        ),
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )

    commands = parser.add_subparsers(dest='command')
    commands.required = True

    init_parser = commands.add_parser(
        'init',
        help='Create a new config file with all required fields pre-filled',
        description=(
            'Create a new config file at OUTPUT with all required fields pre-filled.\n'
            'Edit the file to set title, author, output directory, and add URLs.'
        ),
        epilog=(
            'Examples:\n'
            '  colusa init my_book.json\n'
            '  colusa init my_book.yml'
        ),
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )
    init_parser.set_defaults(func=init)
    init_parser.add_argument('output', type=str,
                             help='Path to the config file to create (.json or .yml)')

    generate_parser = commands.add_parser(
        'generate',
        help='Download articles and convert to AsciiDoc source files',
        description=(
            'Download all URLs in the config, extract article content, and write AsciiDoc\n'
            'source files to the output directory defined in the config file.\n'
            '\n'
            'Use --dry-run to preview which URLs would be processed without downloading.\n'
            'Use --build to also compile after generating (avoids a separate build step).'
        ),
        epilog=(
            'Examples:\n'
            '  colusa generate book.json\n'
            '  colusa generate book.json --dry-run\n'
            '  colusa generate book.json --build epub --build pdf'
        ),
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )
    generate_parser.set_defaults(func=generate)
    generate_parser.add_argument('input', type=str,
                                 help='Config file (.json or .yml)')
    generate_parser.add_argument('--dry-run', action='store_true',
                                 help='Print what would be done without downloading or writing any files')
    generate_parser.add_argument('--build', action='append', dest='build_formats',
                                 metavar='FORMAT', choices=['html', 'epub', 'pdf'],
                                 help='Compile to FORMAT after generating (html, epub, pdf). May be repeated.')

    build_parser = commands.add_parser(
        'build',
        help='Compile AsciiDoc source files into ebook formats using asciidoctor',
        description=(
            'Compile the AsciiDoc files produced by `generate` into ebook formats using\n'
            'asciidoctor. Requires asciidoctor to be installed.\n'
            '\n'
            'Defaults to building all formats (html, epub, pdf) if --format is not given.'
        ),
        epilog=(
            'Examples:\n'
            '  colusa build book.json\n'
            '  colusa build book.json --format epub\n'
            '  colusa build book.json --format epub --format pdf'
        ),
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )
    build_parser.set_defaults(func=build)
    build_parser.add_argument('input', type=str, help='Config file (.json or .yml)')
    build_parser.add_argument('--format', action='append', dest='build_formats',
                              metavar='FORMAT', choices=['html', 'epub', 'pdf'],
                              help='Format to build (html, epub, pdf). May be repeated. Defaults to all.')

    crawler_parse = commands.add_parser(
        'crawl',
        help='Crawl a URL to discover article links and print them one per line',
        description=(
            'Crawl URL to discover article links and print them one per line to stdout\n'
            '(or to a file with --output). Useful for bulk-populating a config file.'
        ),
        epilog=(
            'Examples:\n'
            '  colusa crawl https://example.com/series\n'
            '  colusa crawl https://example.com/series --output urls.txt\n'
            '  colusa crawl https://example.com/series --output urls.txt --output-dir ./cache'
        ),
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )
    crawler_parse.set_defaults(func=crawl_url)
    crawler_parse.add_argument('url', type=str, help='URL to crawl')
    crawler_parse.add_argument('--output-dir', '-d', type=str, dest='output_dir',
                               help='Directory to store cached pages')
    crawler_parse.add_argument('--output', '-o', type=argparse.FileType('w'), default=sys.stdout,
                               help='Output file for discovered URLs (default: stdout)')

    add_url_parser = commands.add_parser(
        'add-url',
        help='Append a URL or local file to an existing config file',
        description=(
            'Append a URL (or local file path) to an existing config file\'s URL list.\n'
            'Use --fetch-title to automatically extract the article title by downloading\n'
            'the page. Without it, the title is left empty and must be set manually.'
        ),
        epilog=(
            'Examples:\n'
            '  colusa add-url book.json https://example.com/article\n'
            '  colusa add-url book.json https://example.com/article --fetch-title\n'
            '  colusa add-url book.json https://example.com/article --title "My Title"\n'
            '  colusa add-url book.json page.html --title "Local Article"\n'
            '  colusa add-url book.json https://example.com/article --part "Chapter 1"'
        ),
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )
    add_url_parser.set_defaults(func=add_url)
    add_url_parser.add_argument('input', type=str, help='Config file (.json or .yml)')
    add_url_parser.add_argument('url', type=str, help='URL or local file path to add')
    add_url_parser.add_argument('--title', type=str, default=None, help='Override article title')
    add_url_parser.add_argument('--author', type=str, default=None, help='Override article author')
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
        raise SystemExit(1)


def generate(args: argparse.Namespace) -> None:
    try:
        if args.dry_run:
            Colusa.dry_run_book(args.input)
        else:
            Colusa.generate_book(args.input)
            if args.build_formats:
                Colusa.build_book(args.input, formats=args.build_formats)
    except ConfigurationError as e:
        logs.error(e)
        raise SystemExit(1)


def build(args: argparse.Namespace) -> None:
    try:
        Colusa.build_book(args.input, formats=args.build_formats)
    except ConfigurationError as e:
        logs.error(e)
        raise SystemExit(1)


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
        raise SystemExit(1)


if __name__ == '__main__':
    main()
