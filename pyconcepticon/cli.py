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

from clldutils.clilib import ArgumentParser
from pyconcepticon.commands import link, stats, attributes


def main():  # pragma: no cover
    parser = ArgumentParser(__name__, link, stats, attributes)
    sys.exit(parser.main())
