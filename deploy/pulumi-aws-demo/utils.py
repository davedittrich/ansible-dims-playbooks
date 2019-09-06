# Copyright 2019, Dave Dittrich <dave.dittrich@gmail.com>.  All rights reserved.

import textwrap

from jinja2 import Template

# See __main__.py exports for comments on default AMI user.
HOSTS_TEMPLATE = textwrap.dedent("""\
  ---
  aws:
    vars:
      ansible_user: 'ec2-user'
      ansible_port: 22
      ansible_ssh_private_key_file: '{{ aws_private_keypath }}'
      _public_key: '{{ aws_private_keypath }}.pub'
    hosts:
      {{ public_ip }}

  ---
  """)

def create_hosts_file(template_vars=dict()):
    """
    Write out an Ansible YAML style inventory file named 'hosts'
    in the current working directory.
    """

    with open('hosts', 'w') as f:
        template = Template(HOSTS_TEMPLATE)
        output_text = template.render(dict(template_vars))
        f.writelines(output_text)


# vim: set fileencoding=utf-8 ts=4 sw=4 tw=0 et :
