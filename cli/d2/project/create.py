# -*- coding: utf-8 -*-

import argparse
import logging
import os
import textwrap

from cliff.command import Command
from d2 import __version__
from d2.utils import get_output
from subprocess import CalledProcessError

class Create(Command):
    """Create a new project"""

    log = logging.getLogger(__name__)

    def get_parser(self, prog_name):
        parser = super(Create, self).get_parser(prog_name)
        parser.formatter_class = argparse.RawDescriptionHelpFormatter
        parser.add_argument('project',
                            nargs='?',
                            default=None)
        parser.epilog = textwrap.dedent(
            """
            Create a new project by cloning the repository at
            {repo_url} into a directory where it will be used by Ansible
            to deploy infrastructure.

            """.format(repo_url=self.app_args.repo_url)
        )

        return parser

    def take_action(self, parsed_args):
        self.log.debug('create project')
        if parsed_args.project is None:
            raise RuntimeError('no project name specified')
        cmd = [
            'git',
            'clone',
            self.app_args.repo_url
        ]
        cwd = self.app_args.projects_dir
        if cwd is None:
            cwd = os.getcwd()
        project_path = os.path.join(cwd, parsed_args.project)
        if os.path.exists(project_path):
            raise RuntimeError('project path "{}" exists'.format(project_path))
        os.mkdir(project_path)
        try:
            output = get_output(cmd=cmd,
                                cwd=project_path)
        except CalledProcessError as err:
            raise RuntimeError(err.stdout.decode('utf-8'))
        pass

# EOF
