#!/usr/bin/env python

import argparse
import signal

from . import __version__
from . import generate
from . import model


def append_subparser(subparser, cmd, func):
    assert func.__doc__, "empty docstring: {}".format(func)
    help_ = func.__doc__.split("\n")[0].lower().strip(".")
    desc = func.__doc__.strip()

    parser = subparser.add_parser(
        cmd,
        formatter_class=argparse.RawDescriptionHelpFormatter,
        help=help_,
        description=desc,
    )

    parser.set_defaults(func=func)
    return parser


def set_up_cli():
    """Set up parser for SNalert entry point.

    """
    parser = argparse.ArgumentParser(prog="SNalert")
    parser.add_argument(
        "--version", action="version", version=f"%(prog)s version {__version__}",
    )

    # set up parser for subcommands
    subparser = parser.add_subparsers(title="commands", metavar="", dest="cmd")
    subparser.required = True

    # register commands
    p = append_subparser(subparser, "generate", generate.main)
    generate._add_parser_args(p)

    p = append_subparser(subparser, "model", model.main)
    model._add_parser_args(p)

    return parser


def main():
    parser = set_up_cli()
    args = parser.parse_args()
    args.func(args)


if __name__ == "__main__":
    main()
