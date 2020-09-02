#!/usr/bin/env python3
import argparse

from symphony import Symphony, read_configuration_file


def main():
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


if __name__ == '__main__':
    main()
