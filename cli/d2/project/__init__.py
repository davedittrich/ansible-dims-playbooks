# -*- coding: utf-8 -*-

"""
D2 project module.

Author: Dave Dittrich <dave.dittrich@gmail.com>
URL: https://davedittrich.github.io
"""

import logging
import json
import os
import shutil
import textwrap

from distutils.dir_util import copy_tree
from subprocess import CalledProcessError  # nosec
from d2.utils import get_output
from d2.utils import psec_available
from d2.utils import psec_environment_delete
from d2.utils import psec_environment_exists
from d2.utils import psec_secrets_generate
from shlex import quote


PROJECTS_CACHE = os.path.join(os.environ['HOME'], '.d2_projects')

__all__ = ['Projects', 'Project']


class Projects(object):
    """Class for tracking projects metadata."""

    log = logging.getLogger(__name__)

    def __init__(self, projects_cache=PROJECTS_CACHE):
        """Object initializer."""
        self.projects_cache = projects_cache
        self.projects = self.load_projects()

    def load_projects(self):
        """Load projects cache from disk."""
        if self.projects_cache is None:
            raise RuntimeError('projects_cache is not defined')
        if not os.path.exists(self.projects_cache):
            return {}
        with open(self.projects_cache, 'r') as f_in:
            cache_contents = f_in.read()
        if cache_contents != '':
            projects = json.loads(cache_contents)
            if not isinstance(projects, dict):
                msg = '{0} is not a dict'.format(self.projects_cache)
                raise RuntimeError(msg)
        return projects

    def save_projects(self):
        """Save projects cache to disk."""
        if not isinstance(self.projects, dict):
            raise RuntimeError('self.projects is not a dict()')
        with open(self.projects_cache, 'w') as f_out:
            f_out.write(json.dumps(self.projects))

    def project_exists(self, name=None):
        """Boolean project existence test."""
        if name is None:
            raise RuntimeError('no project specified')
        return name in self.projects

    def add_project(self, project=None, save=True):
        """Add a new project."""
        if project is None:
            raise RuntimeError('no project specified')
        if project.name in self.projects:
            msg = 'project "{0}" already exists'.format(project.name)
            raise RuntimeError(msg)
        self.projects[project.name] = dict(project)
        if save:
            self.save_projects()

    def delete_project(
        self,
        name=None,
        delete_environment=False,
        ignore_missing=False,
    ):
        """Delete project."""
        if name is None:
            raise RuntimeError('no project specified')
        project_meta = self.projects.pop(name, None)
        if project_meta is not None:
            shutil.rmtree(project_meta['project_path'])
            self.save_projects()
        elif not ignore_missing:
            msg = 'project "{0}" does not exist'.format(name)
            raise RuntimeError(msg)
        if delete_environment:
            psec_environment_delete(name=name)
        else:
            self.log.info('[+] not deleting environment "{0}"'.format(name))


class Project(object):
    """Class for D2 project."""

    log = logging.getLogger(__name__)

    def __init__(
        self,
        name=None,
        projects_dir=None,
        repo_url=None,
        repo_branch=None,
        dir_name=None,
    ):
        """Object initializer."""
        self.name = name
        if projects_dir is None:
            self.projects_dir = os.getcwd()
        else:
            self.projects_dir = projects_dir
        self.project_path = os.path.join(self.projects_dir, self.name)
        # See: https://security.openstack.org/guidelines/dg_use-subprocess-securely.html  # NOQA
        self.repo_url = repo_url
        self.repo_branch = repo_branch
        self.dir_name = dir_name

    def __iter__(self):
        """Iterator for object."""
        yield 'name', self.name
        yield 'project_path', self.project_path
        yield 'repo_url', self.repo_url
        yield 'repo_branch', self.repo_branch

    def create_project(self, create_environment=False):
        """Create and configure the project directory."""
        if os.path.exists(self.project_path):
            if not self._is_project():
                msg = 'project path "{0}" exists'.format(self.project_path)
                raise RuntimeError(msg)
        if create_environment:
            if not psec_available():
                msg = textwrap.dedent("""
                    python_secrets module is required: install with
                    "python3 -m pip install python_secrets"
                    """)
                raise RuntimeError(msg)
            if psec_environment_exists(name=self.name):
                msg = 'python_secrets environment "{0}" already exists'.format(self.name)  # NOQA
                raise RuntimeError(msg)
        self.log.info('[+] creating directory "{0}"'.format(self.project_path))
        os.mkdir(self.project_path)
        base_name = os.path.basename(self.repo_url)
        self.dir_name = os.path.splitext(base_name)[0]
        # See: https://security.openstack.org/guidelines/dg_use-subprocess-securely.html  # NOQA
        cmd = [
            'git',
            'clone',
            '--single-branch',
            '-b',
            quote(self.repo_branch),
            quote(self.repo_url),
            quote(self.dir_name),
        ]
        # Mark directory as a D2 project
        with open(os.path.join(self.project_path, '.d2-project'), 'w') as fh:
            fh.write(self.name)
        msg = '[+] cloning "{0}" from branch "{1}" as "{2}"'.format(
            self.repo_url,
            self.repo_branch,
            self.dir_name
        )
        self.log.info(msg)
        msg = ' '.join(cmd)
        self.log.debug('[!] {0}'.format(msg))
        try:
            # See: https://security.openstack.org/guidelines/dg_use-subprocess-securely.html  # NOQA
            output = get_output(cmd=cmd, cwd=self.project_path)  # NOQA
        except CalledProcessError as err:
            msg = err.stdout.decode('utf-8')
            self.log.info(
                '[-] removing directory "{0}"'.format(self.project_path),
            )
            shutil.rmtree(self.project_path)
            raise RuntimeError(msg)
        if not self._is_d2():
            msg = '[+] "{}" is not a D2 Ansible playbooks clone'.format(
                self.dir_name,
            )
            self.log.info(msg)
        else:
            # Copy deploy directory up to top level
            deploy_src = os.path.join(
                self.project_path,
                self.dir_name,
                'deploy',
                'do',
            )
            self.log.info(
                '[+] copying deployment directory "{0}"'.format(deploy_src),
            )
            copy_tree(deploy_src, self.project_path)
        if self._has_secrets():
            if create_environment:
                cmd = [
                    'psec',
                    'environments',
                    'create',
                    '--clone-from',
                    'secrets',
                ]
                self.log.info('[+] creating python_secrets environment')
                msg = ' '.join(cmd)
                self.log.debug('[!] {0}'.format(msg))
                try:
                    # See: https://security.openstack.org/guidelines/dg_use-subprocess-securely.html  # NOQA
                    output = get_output(cmd=cmd, cwd=self.project_path)  # NOQA
                # TODO(dittrich): Not very elegant to just delete
                except CalledProcessError as err:
                    msg = err.stdout.decode('utf-8')
                    self.log.info(
                        '[-] removing directory "{0}"'.format(
                            self.project_path,
                        ),
                    )
                    shutil.rmtree(self.project_path)
                    raise RuntimeError(msg)
                self.log.info('[+] generating initial secrets')
                psec_secrets_generate(name=self.name)
        # Other configuration?...

    def delete_project(self):
        """Delete a project directory."""
        if self.project_path is None:
            raise RuntimeError('no project_path found')
        if os.path.exists(self.project_path):
            shutil.rmtree(self.project_path)
        else:
            msg = 'project_path "{0}" does not exist'.format(self.project_path)
            raise RuntimeError(msg)

    def path(self):
        """Return path."""
        return self.project_path

    def __str__(self):
        """Return string representation."""
        return '' if self.name is None else str(self.name)

    def _is_d2(self):
        """Return boolean if this is a D2 Ansible playbooks clone."""
        cloned_dir = os.path.join(self.project_path, self.dir_name)
        marker = os.path.join(cloned_dir, '.d2')
        return os.path.exists(marker)

    def _is_project(self):
        """Return boolean if project marker exists."""
        marker = os.path.join(self.project_path, '.d2_project')
        return os.path.exists(marker)

    def _has_secrets(self):
        """Return boolean if this directory contains secrets definitions."""
        defs_dir = os.path.join(
            self.project_path, 'secrets', 'secrets.d'
        )
        try:
            defs = [
                fname for fname in os.listdir(defs_dir) if
                fname.endswith('.yml')
            ]
        except FileNotFoundError:
            defs = []
        return bool(defs)


# vim: set fileencoding=utf-8 ts=4 sw=4 tw=0 et :
