# -*- coding: utf-8 -*-

import argparse
import logging
import textwrap

from cliff.command import Command
from d2 import __version__


class About(Command):
    """About the ``d2`` CLI"""

    log = logging.getLogger(__name__)

    def get_parser(self, prog_name):
        parser = super(About, self).get_parser(prog_name)
        parser.formatter_class = argparse.RawDescriptionHelpFormatter
        parser.epilog = textwrap.dedent("""
            .. code-block:: console

                $ d2 about
                d2 version {VERSION}

            ..
            """.format(VERSION=__version__)
        )

        return parser

    def take_action(self, parsed_args):
        print("d2 version {VERSION}\n".format(VERSION=__version__))


# EOF
