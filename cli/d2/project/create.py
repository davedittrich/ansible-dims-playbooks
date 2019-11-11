# -*- coding: utf-8 -*-

import argparse
import logging
import textwrap

from cliff.command import Command
from d2.project import Projects
from d2.project import Project


class Create(Command):
    """Create a new project"""

    log = logging.getLogger(__name__)

    def get_parser(self, prog_name):
        parser = super(Create, self).get_parser(prog_name)
        parser.formatter_class = argparse.RawDescriptionHelpFormatter
        parser.add_argument('name',
                            nargs='?',
                            default=None)
        parser.epilog = textwrap.dedent(
            """
            Create a new project by cloning the repository at
            {repo_url}
            into a directory where it will be used by Ansible
            to deploy infrastructure.
            """.format(repo_url=self.app_args.repo_url)
        )

        return parser

    def take_action(self, parsed_args):
        self.log.debug('create project')
        if parsed_args.name is None:
            raise RuntimeError('no project name specified')
        projects = Projects()
        if projects.project_exists(parsed_args.name):
            raise RuntimeError('project "{}" '.format(parsed_args.name) +
                               'already exists')
        project = Project(name=parsed_args.name,
                          projects_dir=self.app_args.projects_dir,
                          repo_url=self.app_args.repo_url,
                          repo_branch=self.app_args.repo_branch)
        project.create_project()
        projects.add_project(project=project)
        self.log.debug('[!] cloned {} '.format(self.app_args.repo_url) +
                       'into {}'.format(str(project.path())))
        self.log.info('[+] created project "{}"'.format(parsed_args.name))

# EOF
