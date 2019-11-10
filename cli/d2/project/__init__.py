# -*- coding: utf-8 -*-

import logging
import json
import os
import shutil

from subprocess import CalledProcessError  # nosec
from d2.utils import get_output
from shlex import quote

log = logging.getLogger(__name__)

PROJECTS_CACHE = os.path.join(os.environ['HOME'], '.d2_projects')

__all__ = ['create', 'Projects', 'Project', PROJECTS_CACHE]

class Projects(object):
    """Class for tracking projects metadata"""
    def __init__(self, projects_cache=PROJECTS_CACHE):
        self.projects_cache = projects_cache
        self.projects = self.load_projects()

    def load_projects(self):
        if self.projects_cache is None:
            raise RuntimeError('projects_cache is not defined')
        if not os.path.exists(self.projects_cache):
            return dict()
        with open(self.projects_cache, 'r') as f_in:
            contents = f_in.read()
        if contents != '':
            projects = json.loads(contents)
            if type(projects) is not dict:
                raise RuntimeError('{} '.format(self.projects_cache) +
                                   'is not a dict()')
        return projects

    def save_projects(self):
        if type(self.projects) is not dict:
            raise RuntimeError('self.projects is not a dict()')
        with open(self.projects_cache, 'w') as f_out:
            f_out.write(json.dumps(self.projects))

    def project_exists(self, name=None):
        if name is None:
            raise RuntimeError('no project specified')
        return name in self.projects

    def add_project(self, project=None, save=True):
        if project is None:
            raise RuntimeError('no project specified')
        if project.name in self.projects:
            raise RuntimeError('project "{}" '.format(project.name) +
                               'already exists')
        self.projects[project.name] = dict(project)
        if save:
            self.save_projects()

    def delete_project(self, name=None, ignore_missing=False):
        if name is None:
            raise RuntimeError('no project specified')
        project_meta = self.projects.pop(name, None)
        if project_meta is not None:
            shutil.rmtree(project_meta['project_path'])
            self.save_projects()
        else:
            if not ignore_missing:
                raise RuntimeError('project "{}" '.format(name) +
                                   'does not exist')


class Project(object):
    """Class for D2 project"""
    def __init__(self,
                 name=None,
                 projects_dir=None,
                 repo_url=None,
                 repo_branch=None):
        self.name = name
        if projects_dir is None:
            self.projects_dir = os.getcwd()
        else:
            self.projects_dir = projects_dir
        self.project_path = os.path.join(self.projects_dir, self.name)
        # See: https://security.openstack.org/guidelines/dg_use-subprocess-securely.html  # noqa
        self.repo_url = repo_url
        self.repo_branch = repo_branch

    def __iter__(self):
        yield 'name', self.name
        yield 'project_path', self.project_path
        yield 'repo_url', self.repo_url
        yield 'repo_branch', self.repo_branch

    def create_project(self):
        """Create and configure the project directory"""
        if os.path.exists(self.project_path):
            if not self._is_project():
                raise RuntimeError('project path ' +
                                   '"{}" '.format(self.project_path) +
                                   'exists')
        os.mkdir(self.project_path)
        # See: https://security.openstack.org/guidelines/dg_use-subprocess-securely.html  # noqa
        cmd = [
            'git',
            'clone',
            '--single-branch',
            '-b',
            quote(self.repo_branch),
            quote(self.repo_url)
        ]
        # Mark directory as a D2 project
        with open(os.path.join(self.project_path, '.d2-project'), 'w') as f:
            f.write(self.name)
        log.debug(" ".join([arg for arg in cmd]))
        try:
            # See: https://security.openstack.org/guidelines/dg_use-subprocess-securely.html  # noqa
            output = get_output(cmd=cmd, cwd=self.project_path)  # noqa
        except CalledProcessError as err:
            shutil.rmtree(self.project_path)
            raise RuntimeError(err.stdout.decode('utf-8'))

    def delete_project(self):
        """Delete a project directory"""
        if self.project_path is None:
            raise RuntimeError('no project_path found')
        if os.path.exists(self.project_path):
            shutil.rmtree(self.project_path)
        else:
            raise RuntimeError('project_path ' +
                               '"{}" '.format(self.project_path) +
                               'does not exist')

    def path(self):
        return self.project_path

    def __str__(self):
        return "" if self.name is None else str(self.name)

    def _is_project(self):
        return os.path.exists(os.path.join(self.project_path,
                                           '.d2_project'))


# vim: set fileencoding=utf-8 ts=4 sw=4 tw=0 et :
