# -*- coding: utf-8 -*-

"""D2 project/delete.py.

Author: Dave Dittrich <dave.dittrich@gmail.com>
URL: https://davedittrich.github.io
"""

import argparse
import logging
import textwrap

from cliff.command import Command
from d2.project import Projects


class Delete(Command):
    """Delete a new project."""

    log = logging.getLogger(__name__)

    def get_parser(self, prog_name):
        """Returns parser."""
        parser = super().get_parser(prog_name)
        parser.formatter_class = argparse.RawDescriptionHelpFormatter
        parser.add_argument(
            '--delete-environment',
            action='store_true',
            dest='delete_environment',
            default=False,
            help='Delete project\'s python_secrets environment (default: False)'  # NOQA
        )
        parser.add_argument(
            'name',
            nargs='?',
            default=None,
        )
        parser.epilog = textwrap.dedent("""
            Deletes a project directory.
            """)
        return parser

    def take_action(self, parsed_args):
        """Take action."""
        self.log.debug('delete project')
        if parsed_args.name is None:
            raise RuntimeError('no project name specified')
        projects = Projects()
        if parsed_args.name not in projects.projects:
            msg = 'project "{0}" does not exist'.format(parsed_args.name)
            raise RuntimeError(msg)
        projects.delete_project(
            name=parsed_args.name,
            delete_environment=parsed_args.delete_environment,
        )
        msg = '[+] deleted project "{0}"'.format(parsed_args.name)
        self.log.info(msg)


# EOF
