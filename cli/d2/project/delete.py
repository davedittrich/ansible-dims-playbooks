# -*- coding: utf-8 -*-

import argparse
import logging
import textwrap

from cliff.command import Command
from d2.project import Projects


class Delete(Command):
    """Delete a new project"""

    log = logging.getLogger(__name__)

    def get_parser(self, prog_name):
        parser = super(Delete, self).get_parser(prog_name)
        parser.formatter_class = argparse.RawDescriptionHelpFormatter
        parser.add_argument('name',
                            nargs='?',
                            default=None)
        parser.epilog = textwrap.dedent(
            """
            Deletes a project directory.
            """
        )

        return parser

    def take_action(self, parsed_args):
        self.log.debug('delete project')
        if parsed_args.name is None:
            raise RuntimeError('no project name specified')
        projects = Projects()
        if parsed_args.name not in projects.projects:
            raise RuntimeError('project "{}" '.format(parsed_args.name) +
                               'does not exist')
        projects.delete_project(name=parsed_args.name)
        self.log.debug('deleted project ' +
                       '"{}" '.format(parsed_args.name))

# EOF
