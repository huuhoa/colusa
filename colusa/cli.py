import argparse

from colusa import Colusa, read_configuration_file, ConfigurationError, logs


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

    return parser.parse_args()


def init(args):
    try:
        Colusa.generate_new_configuration(args.output)
    except ConfigurationError as e:
        logs.error(e)


def generate(args):
    try:
        configs = read_configuration_file(args.input)
        s = Colusa(configs)
        s.generate()
    except ConfigurationError as e:
        logs.error(e)


if __name__ == '__main__':
    main()
