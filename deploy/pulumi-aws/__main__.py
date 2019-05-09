import arrow
import logging
import pulumi
import os

from ami import get_linux_ami
from get_console_output import get_console_output
from jinja2 import Environment
from jinja2 import FileSystemLoader
from jinja2 import Markup
from jinja2 import StrictUndefined
from jinja2 import Undefined
from jinja2 import contextfunction
from jinja2 import make_logging_undefined
from jinja2 import select_autoescape
from psec.secrets import SecretsEnvironment
from pulumi import Output
from pulumi_aws import ec2
from utils import create_hosts_file

DEBUG = False

def attributes(object=object()):
    return [i for i in dir(object) if
            not i.startswith('_') and
            not i.startswith('translate_')]


@contextfunction
def include_raw(ctx, name):
    env = ctx.environment
    return Markup(env.loader.get_source(env, name)[0]).strip


log = logging.getLogger(__name__)
LoggingUndefined = make_logging_undefined(
    logger=log,
    base=Undefined
    )

# Use the default environment
env = SecretsEnvironment()
env.read_secrets()
aws_private_keypath = env.get_secret('aws_privatekey_path')
with open(aws_private_keypath + '.pub', 'r') as f:
    aws_publickey = f.read().strip()

instance_type = env.get_secret('aws_instance_type')
pulumi.info(msg="instance_type={}".format(instance_type))
try:
    ami = env.get_secret('aws_ami_id')
except RuntimeError:
    ami = ''
if ami == '':
    ami = get_linux_ami(instance_type)
pulumi.info(msg="ami={}".format(ami))

web_group = ec2.SecurityGroup('web-secgrp',
    description='Enable HTTP/HTTPS access',
    ingress=[
        { 'protocol': 'tcp', 'from_port': 80, 'to_port': 80,
          'cidr_blocks': ['0.0.0.0/0'] },
        { 'protocol': 'tcp', 'from_port': 443, 'to_port': 443,
          'cidr_blocks': ['0.0.0.0/0'] }
    ],
    egress=[
        { 'protocol': 'tcp', 'from_port': 0, 'to_port': 80,
          'cidr_blocks': ['0.0.0.0/0'] },
        { 'protocol': 'tcp', 'from_port': 0, 'to_port': 443,
          'cidr_blocks': ['0.0.0.0/0'] }
    ])

pulumi.info(msg="aws_cidr_allowed={}".format(
    env.get_secret('aws_cidr_allowed')))
ssh_group = ec2.SecurityGroup('ssh-secgrp',
    description='Enable SSH access',
    ingress=[
        { 'protocol': 'tcp', 'from_port': 22, 'to_port': 22,
          'cidr_blocks': [ env.get_secret('aws_cidr_allowed') ] }
    ])

if os.path.exists('user-data.j2'):
    template_vars = dict(env.items())
    template_vars['aws_publickey'] = aws_publickey
    template_vars['aws_ami_id'] = ami
    template_loader = FileSystemLoader(
        ['.', os.path.expanduser('~')],
        followlinks=True)
    template_env = Environment(
        loader=template_loader,
        autoescape=select_autoescape(
            disabled_extensions=('txt',),
            default_for_string=True,
            default=True,
        ),
        undefined=LoggingUndefined)
    template_env.globals['include_raw'] = include_raw
    template = template_env.get_template('user-data.j2')
    user_data = template.render(template_vars)
    with open('user-data.test', 'w') as f:
        f.write(user_data)
    pulumi.info(msg='generated user-data from user-data.j2')
elif os.path.exists('user-data.txt'):
    with open('user-data.txt') as f:
        user_data = f.read()
    pulumi.info(msg='read user-data from user-data.txt')

server = ec2.Instance('server',
    instance_type=instance_type,
    security_groups=[web_group.name, ssh_group.name],
    user_data=user_data,
    ami=ami)

if DEBUG:
    pulumi.info("web_group={}".format(attributes(web_group)))
    pulumi.info("web_group.vpc_id={}".format(
        Output.all(web_group.vpc_id).apply(lambda s: f"{s[0]}")))
    pulumi.info("ssh_group={}".format(attributes(ssh_group)))
    pulumi.info("ssh_group.vpc_id={}".format(
        ssh_group.vpc_id.apply(lambda s: f"{s[0]}")))

# Determining the user account for a given AMI is not an easy
# task. For details on how to get the default user name, see
# https://docs.aws.amazon.com/AWSEC2/latest/UserGuide/connection-prereqs.html
# Hard code the user until this can be derived programatically.
pulumi.export('instance_user', 'ec2-user')
pulumi.export('instance_id', server.id)
pulumi.export('privatekey_path', env.get_secret('aws_privatekey_path'))
pulumi.export('public_ip', server.public_ip)
pulumi.export('public_dns', server.public_dns)
pulumi.export('subnet_id', server.subnet_id)
pulumi.export('vpc_id', ssh_group.vpc_id)
