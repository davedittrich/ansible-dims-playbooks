# -*- coding: utf-8 -*-

"""D2 CLI utility.

Author: Dave Dittrich <dave.dittrich@gmail.com>
URL: https://davedittrich.github.io
"""

# Standard library modules.
import argparse
import logging
import os
import sys
import textwrap

from d2 import __version__
from d2 import __release__
from d2.utils import Timer

# External dependencies.

from cliff.app import App
from cliff.commandmanager import CommandManager


if sys.version_info < (3, 6, 0):
    program = os.path.basename(sys.argv[0])
    raise RuntimeError(
        textwrap.dedent("""
            The {0} program prequires Python 3.6.0 or newer\n
            Found Python {1}'
            """.format(program, sys.version),
        )
    )

BUFFER_SIZE = 128 * 1024
DAY = os.environ.get('DAY', 5)
DEFAULT_PROTOCOLS = ['icmp', 'tcp', 'udp']
KEEPALIVE = 5.0
MAX_LINES = None
MAX_ITEMS = 10
REPO_URL = os.getenv(
    'D2_REPO_URL',
    'https://github.com/davedittrich/ansible-dims-playbooks',
)
REPO_BRANCH = os.getenv('D2_REPO_BRANCH', 'master')

# Use syslog for logging?
# TODO(dittrich): Make this configurable, since it can fail on Mac OS X
SYSLOG = False

# Initialize a logger for this module.
logger = logging.getLogger(__name__)


def default_data_dir():
    """Return the directory path root for data storage"""
    return os.getenv('D@_DATA_DIR', None)


def default_environment(default=None):
    """Return environment identifier"""
    return os.getenv('D2_ENVIRONMENT', default)


class D2App(App):
    """D2 CLI application"""

    def __init__(self):
        super().__init__(
            description=__doc__.strip(),
            version=__release__ if __release__ != __version__ else __version__,
            command_manager=CommandManager(
                namespace='d2',
            ),
            deferred_help=True,
        )
        self.environment = None
        self.timer = Timer()

    def build_option_parser(self, description, version):
        parser = super().build_option_parser(
            description,
            version,
        )
        parser.formatter_class = argparse.RawDescriptionHelpFormatter

        # Global options
        parser.add_argument(
            '-D',
            '--projects-dir',
            metavar='<projects-directory>',
            dest='projects_dir',
            default=os.getenv('D2_PROJECTS_DIR', None),
            help=textwrap.dedent("""
                Root directory for holding projects (Env: D2_PROJECTS_DIR;
                default: {0})
                """.format(os.getenv('D2_PROJECTS_DIR', os.getcwd()))
            ),
        )
        parser.add_argument(
            '-e',
            '--elapsed',
            action='store_true',
            dest='elapsed',
            default=False,
            help=textwrap.dedent("""
                Include elapsed time (and ASCII bell) on exit (default: False)
                """),
        )
        parser.add_argument(
            '-E',
            '--environment',
            metavar='<environment>',
            dest='environment',
            default=default_environment(),
            help=textwrap.dedent("""
                Deployment environment selector (Env: D2_ENVIRONMENT;
                default: {0})
                """.format(default_environment())
            ),
        )
        parser.add_argument(
            '-n',
            '--limit',
            action='store',
            type=int,
            metavar='<results_limit>',
            dest='limit',
            default=0,
            help=textwrap.dedent("""
                Limit result to no more than this many items (0 means
                no limit; default: 0)
                """),
        )
        parser.add_argument(
            '-B',
            '--repo-branch',
            action='store',
            metavar='<repo_branch>',
            dest='repo_branch',
            default=REPO_BRANCH,
            help=textwrap.dedent("""
                Branch or commit for ansible-dims-playbooks repository
                (default: {0})
                """.format(REPO_BRANCH)
            ),
        )
        parser.add_argument(
            '-R',
            '--repo-url',
            action='store',
            metavar='<repo_url>',
            dest='repo_url',
            default=REPO_URL,
            help=textwrap.dedent("""
                URL for ansible-dims-playbooks repository (default: {0})
                """.format(REPO_URL)
            ),
        )
        parser.epilog = textwrap.dedent(
            """
            Environment variables:
              D2_REPO_URL         URL to dims-ansible-playbooks Git repository
              D2_REPO_BRANCH      Specific repo branch or commit
              D2_ENVIRONMENT      Name for project's environment
              D2_PROJECTS_DIR     Directory root for storing multiple projects.
            """)

        return parser

    def initialize_app(self, argv):
        self.LOG.debug('initialize_app')
        self.set_environment(self.options.environment)

    def prepare_to_run_command(self, cmd):
        if cmd.app_args.verbose_level > 1:
            msg = " ".join(list(sys.argv))
            self.LOG.info('[+] command line: {0}'.format(msg))
        self.LOG.debug('prepare_to_run_command %s', cmd.__class__.__name__)
        if self.options.elapsed:
            self.timer.start()

    def clean_up(self, cmd, result, err):  # NOQA: WPS110
        self.LOG.debug('[!] clean_up %s', cmd.__class__.__name__)
        if self.options.elapsed:
            self.timer.stop()
            elapsed = self.timer.elapsed()
            if result != 0:
                self.LOG.debug('[!] elapsed time: %s', elapsed)
            elif self.options.verbose_level > 0 and cmd.__class__.__name__ != 'CompleteCommand':  # NOQA
                self.stdout.write('[+] Elapsed time {0}\n'.format(elapsed))
                if sys.stdout.isatty():
                    sys.stdout.write('\a')
                    sys.stdout.flush()

    def set_environment(self, environment=default_environment()):  # NOQA
        """Set variable for current environment"""
        self.environment = environment

    def get_environment(self):
        """Get the current environment setting"""
        return self.environment


def main(argv=sys.argv[1:]):  # NOQA
    """
    Command line interface for the ``d2`` program.
    """

    myapp = D2App()
    ret = 1
    try:
        ret = myapp.run(argv)
    except KeyboardInterrupt:
        sys.stderr.write("\nReceived keyboard interrupt: exiting\n")
    return ret


if __name__ == '__main__':
    sys.exit(main(argv=sys.argv[1:]))

# EOF
