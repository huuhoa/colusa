import argparse

from colusa import Colusa, read_configuration_file, ConfigurationError, logs


def main():
    args = parse_args()
    args.func(args)


def parse_args():
    parser = argparse.ArgumentParser()

    commands = parser.add_subparsers(dest='command')
    commands.required = True

    init_parser = commands.add_parser('init')
    init_parser.set_defaults(func=init)
    init_parser.add_argument('output', type=str, help='Configuration file')

    generate_parser = commands.add_parser('generate')
    generate_parser.set_defaults(func=generate)
    generate_parser.add_argument('input', type=str, help='Configuration file')

    return parser.parse_args()


def init(args):
    Colusa.generate_new_configuration(args.output)


def generate(args):
    try:
        configs = read_configuration_file(args.input)
        s = Colusa(configs)
        s.generate()
    except ConfigurationError as e:
        logs.error(e)


if __name__ == '__main__':
    main()
