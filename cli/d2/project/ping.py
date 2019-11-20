# -*- coding: utf-8 -*-

import argparse
import json
import logging
import os
import re
import textwrap

from cliff.lister import Lister
from d2.project import Projects
from d2.utils import get_output
from subprocess import CalledProcessError  # nosec


class Ping(Lister):
    """List status of project instances."""

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
            Show status of project instancess.
            """,
        )
        return parser

    def take_action(self, parsed_args):
        self.log.debug('project instance status')
        projects = Projects().load_projects()
        if parsed_args.name is None:
            raise RuntimeError('no project specified')
        project = projects[parsed_args.name]

        # Run "make ping" in project directory
        cmd = [
            'make',
            'ping',
        ]
        os.environ['ANSIBLE_STDOUT_CALLBACK'] = 'json'
        output = []
        try:
            # See: https://security.openstack.org/guidelines/dg_use-subprocess-securely.html  # NOQA
            output = get_output(cmd=cmd, cwd=project['project_path'])  # NOQA
        except CalledProcessError as err:
            output = err.stdout.decode('utf-8').split('\n')
        output_text = " ".join(list(output))
        # Parse output that looks like:
        # yellow | SUCCESS => {
        #    "changed": false,
        #    "ping": "pong"
        # }
        # blue | UNREACHABLE! => {
        #    "changed": false,
        #    "msg": "Failed to connect to the host via ssh: Permission denied (publickey,gssapi-keyex,gssapi-with-mic,password).",  # NOQA
        #    "unreachable": true
        # }

        pattern = re.compile(
            r'\s(?P<node>\S+?) \| (?P<status>\S+\!{0,1}?) => (?P<res>{.+?})',
        )
        columns = ('Node', 'Reachable', 'Ping')
        dats = []
        for match in pattern.finditer(output_text):
            res = json.loads(match.group(3))
            reachable = "no" if "unreachable" in res else "yes"
            try:
                pong = res['ping']
            except KeyError:
                pong = res['msg']
            dats.append(
                (
                    match.group(1),
                    reachable,
                    pong,
                )
            )
        return columns, dats


# vim: set fileencoding=utf-8 ts=4 sw=4 tw=0 et :
