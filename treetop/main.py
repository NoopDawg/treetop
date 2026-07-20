import argparse
import sys

from .command import up, down, status, delete, launch, connect, add, create_template, init


def main(argv=None):
    import treetop
    parse = argparse.ArgumentParser(
        prog="treetop",
        description="CLI tool for managing EC2 development instances",
    )
    parse.add_argument(
        '--version', '-V',
        action='version',
        version=treetop.__version__,
        help='Show program version and exit.'
    )
    subparser = parse.add_subparsers()

    init.add_command(subparser)
    launch.add_command(subparser)
    up.add_command(subparser)
    down.add_command(subparser)
    delete.add_command(subparser)
    status.add_command(subparser)
    connect.add_command(subparser)
    add.add_command(subparser)
    create_template.add_command(subparser)

    def print_help(args):
        parse.print_help()

    parse.set_defaults(func=print_help)
    args = parse.parse_args(argv)

    return args.func(args)


if __name__ == "__main__":
    main(sys.argv[1:])
