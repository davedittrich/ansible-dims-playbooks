# vim: set ts=4 sw=4 tw=0 et :
#
# Copyright (C) 2018, David Dittrich. All rights reserved.
#
#  Licensed under the Apache License, Version 2.0 (the "License");
#  you may not use this file except in compliance with the License.
#  You may obtain a copy of the License at
#
#      http://www.apache.org/licenses/LICENSE-2.0
#
#  Unless required by applicable law or agreed to in writing, software
#  distributed under the License is distributed on an "AS IS" BASIS,
#  WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
#  See the License for the specific language governing permissions and
#  limitations under the License.
#
# This lookup provides an interface to the python_secrets (psec)
# program.

from __future__ import (absolute_import, division, print_function)
__metaclass__ = type

DOCUMENTATION = """
    lookup: psec
    author: Dave Dittrich <dave.dittrich@gmail.com>
    short_description: Lookup interface for python_secrets (psec)
    description:
      - This lookup provides a limited interface to the python_secrets
        (psec) program.
    options:
      args:
        description: command arguments
        required: True
      environment:
        description: python_secrets environment to use
        required: False
    notes:
"""

EXAMPLES = """
Running 'psec' on the command line:

$ psec environments path
/home/dittrich/.secrets/do

$ psec -e goSecure environments path
/home/dittrich/.secrets/goSecure

$ psec secrets get do_region
sfo2

Lookup use in plays:

- name: Get path to directory for environment 'do'
  debug: msg="{{ lookup('psec','environments path', environment="do") }}"

- name: Always use quote filter to make sure your variables are safe to use with shell
  debug: msg="{{ lookup('psec','secrets get ' + mysecret|quote ) }}"

Lookup use with Ansible ad-hoc mode, debug module:

$ ansible -i localhost, -c local -m debug -a 'msg={{ lookup("psec", "environments path") }}' localhost
localhost | SUCCESS => {
    "msg": "/home/dittrich/.secrets/do"
}

$ ansible -i localhost, -c local -m debug -a 'msg={{ lookup("psec", "environments path", environment="goSecure") }}' localhost
localhost | SUCCESS => {
    "msg": "/home/dittrich/.secrets/goSecure"
}

$ ansible -i localhost, -c local -m debug -a 'msg={{ lookup("psec", "secrets get do_region", environment="do") }}' localhost
localhost | SUCCESS => {
    "msg": "sfo2"
}

NOTE: It isn't possible for psec to properly identify the default environment
by looking at the current working directory, which Ansible alters. To make it
work properly, run Ansible using 'psec -E run -- ansible ...' to take advantage
of the environment variable PYTHON_SECRETS_ENVIRONMENT that gets set from
what is more likely the real current working directory.
"""

RETURN = """
  _string:
    description:
      - stdout from command
"""

import os
import re
import subprocess

from ansible.errors import AnsibleError
from ansible.plugins.lookup import LookupBase


class LookupModule(LookupBase):

    def run(self, args, variables, **kwargs):

        ret = []
        environment = kwargs.get('environment',
                                 os.getenv('PYTHON_SECRETS_ENVIRONMENT', None))
        cmd_args = " ".join([a for a in args])
        # Use the -q flag to quiet output
        if environment is not None:
            cmd = "psec -q -e {} {}".format(environment, cmd_args)
        else:
            cmd = "psec -q {}".format(cmd_args)
        p = subprocess.Popen(cmd,
                             cwd=self._loader.get_basedir(),
                             shell=True,
                             stdin=subprocess.PIPE,
                             stdout=subprocess.PIPE)
        (stdout, stderr) = p.communicate()
        if p.returncode == 0:
            ret.append(stdout.decode("utf-8").rstrip())
        else:
            raise AnsibleError("lookup_plugin.psec(%s) returned %d" % (cmd, p.returncode))

        return ret
