# -*- coding: utf-8 -*-

import argparse
import logging
import textwrap

from cliff.command import Command
from d2 import __version__


class Create(Command):
    """Create a new project"""

    log = logging.getLogger(__name__)

    def get_parser(self, prog_name):
        parser = super(Create, self).get_parser(prog_name)
        parser.formatter_class = argparse.RawDescriptionHelpFormatter
        parser.add_argument('project',
                            nargs='1',
                            default=None)
        parser.epilog = textwrap.dedent(
            """
            Create project.
            """
        )

        return parser

    def take_action(self, parsed_args):
        if parsed_args.project is None:
            raise RuntimeError('no project name specified')
        self.log.debug('create project')

# EOF
