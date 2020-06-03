#!/usr/bin/env python

import argparse
import signal

from . import __version__


def _set_up_parser():
    """Set up parser for hop-SNalert app entry point.

    """
    parser = argparse.ArgumentParser(prog="hop-SNalert")
    parser.add_argument(
        "--version", action="version", version=f"%(prog)s version {__version__}",
    )

    # my arguments here

    return parser


def _set_up_cli():
    """Set up CLI boilerplate for hop-SNalert app entry point.

    """
    signal.signal(signal.SIGINT, signal.SIG_DFL)
    parser = _set_up_parser()
    return parser.parse_args()


# ------------------------------------------------
# -- main

def main():
    args = _set_up_cli()

    # do stuff here


if __name__ == "__main__":
    main()
