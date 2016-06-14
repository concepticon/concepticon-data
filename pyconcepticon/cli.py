# coding: utf8
"""
Main command line interface of the pyconcepticon package.

Like programs such as git, this cli splits its functionality into sub-commands
(see e.g. https://docs.python.org/2/library/argparse.html#sub-commands).
The rationale behind this is that while a lot of different tasks may be triggered using
this cli, most of them require common configuration.

The basic invocation looks like

    concepticon [OPTIONS] <command> [args]

"""
from __future__ import unicode_literals
import sys
import argparse

from pyconcepticon.commands import link, stats

COMMANDS = {f.__name__: f for f in [link, stats]}


def main():
    parser = argparse.ArgumentParser(
        description="""Main command line interface of the pyconcepticon package.""",
        epilog="Use '%(prog)s help <cmd>' to get help about individual commands.")
    parser.add_argument("--verbosity", help="increase output verbosity")
    parser.add_argument('command', help='|'.join(COMMANDS))
    parser.add_argument('args', nargs=argparse.REMAINDER)

    args = parser.parse_args()
    if args.command == 'help':
        # As help text for individual commands we simply re-use the docstrings of the
        # callables registered for the command:
        print(COMMANDS[args.args[0]].__doc__)
        sys.exit(0)

    COMMANDS[args.command](args)
    sys.exit(0)
