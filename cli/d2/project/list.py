# -*- coding: utf-8 -*-

import argparse
import logging
import textwrap

from cliff.lister import Lister
from d2.project import Projects


class List(Lister):
    """List projects."""

    log = logging.getLogger(__name__)

    def get_parser(self, prog_name):
        parser = super().get_parser(prog_name)
        parser.formatter_class = argparse.RawDescriptionHelpFormatter
        parser.add_argument(
            'name',
            nargs='?',
            default=None,
        )
        parser.epilog = textwrap.dedent(
            """
            List projects.
            """,
        )
        return parser

    def take_action(self, parsed_args):
        self.log.debug('list project(s)')
        projects = Projects().load_projects()
        if parsed_args.name is not None:
            projects = projects[parsed_args.name]
        columns = ('Name', 'Path', 'Repo', 'Branch')
        dats = [
            (
                project['name'],
                project['project_path'],
                project['repo_url'],
                project['repo_branch'],
            )
            for project in projects.values()
        ]
        return columns, dats

# EOF
