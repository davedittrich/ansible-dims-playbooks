# -*- coding: utf-8 -*-

"""D2 utilies.

Author: Dave Dittrich <dave.dittrich@gmail.com>
URL: https://davedittrich.github.io
"""

import logging
import os
import subprocess  # nosec
import sys
import requests
import time
import warnings

from bz2 import BZ2Decompressor
from collections import OrderedDict
from shlex import quote
# >> Issue: [B404:blacklist] Consider possible security implications
#           associated with CalledProcessError module.
#    Severity: Low   Confidence: High
#    Location: d2/utils.py:13
#    More Info: https://bandit.readthedocs.io/en/latest/blacklists/
#               blacklist_imports.html#b404-import-subprocess
from subprocess import CalledProcessError  # nosec

log = logging.getLogger(__name__)


def psec_available():
    """Return boolean indicating availability of 'psec' program."""
    cmd = ['psec', '--version']
    try:
        output = get_output(cmd=cmd)
    except CalledProcessError as err:
        raise RuntimeError(err.stdout.decode('utf-8'))
    return output[0].startswith('psec')


def psec_environment_delete(name=None):
    """Delete project environment 'name'."""
    if name is None:
        raise RuntimeError('environment must be defined')
    cmd = ['psec', 'environments', 'delete', quote(name), '--force']
    try:
        output = get_output(cmd=cmd, stdin=subprocess.PIPE)
    except CalledProcessError as err:
        raise RuntimeError(err.stdout.decode('utf-8'))
    return 'deleted' in output[0]


def psec_environment_exists(name=None):
    """Return boolean indicating existence of environment 'name'."""
    cmd = ['psec', 'environments', 'list', '-f', 'value', '-c', 'Environment']
    try:
        output = get_output(cmd=cmd)
    except CalledProcessError as err:
        raise RuntimeError(err.stdout.decode('utf-8'))
    return name in output


def psec_default_environment(name=None, cwd=None):
    """Return default environment name."""
    if cwd is None:
        cwd = os.getcwd()
    cmd = ['psec', '-q', 'environments', 'default']
    try:
        output = get_output(cmd=cmd, cwd=cwd)
    except CalledProcessError as err:
        raise RuntimeError(err.stdout.decode('utf-8'))
    return output[0]


def psec_secrets_generate(name=None):
    """Generate secrets for new environment."""
    cmd = ['psec', '-e', quote(name), 'secrets', 'generate']
    res = ''
    try:
        res = get_output(cmd=cmd)
    except CalledProcessError as err:
        raise RuntimeError(err.stdout.decode('utf-8'))
    return res


def find(lst, key, vv):
    for ii, dic in enumerate(lst):
        if dic[key] == vv:
            return ii
    return None


def convert_type(tt, vv):
    """Convert value 'vv' to type 'tt'."""
    valid_type = ['int', 'float', 'long', 'complex', 'str']
    if tt not in valid_type:
        valid_types = ','.join(valid_type)
        raise RuntimeError(
            'Unsupported type: must be one of: {0}'.format(valid_types)
        )
    try:
        return type(eval('{0}()'.format(tt)))(vv)  # nosec  # NOQA
    except ValueError:
        raise ValueError('type={0}, value="{1}"'.format(tt, vv))


def check_natural(vv):
    try:
        ii = int(vv)
    except ValueError:
        raise RuntimeError('"{0}" is not a base-10 integer'.format(vv))
    if ii <= 0:
        raise RuntimeError('"{0}" is not a natural number (>0)'.format(vv))
    return ii


def check_whole(vv):
    try:
        ii = int(vv)
    except ValueError:
        raise RuntimeError('"{0}" is not a base-10 integer'.format(vv))
    if ii < 0:
        raise RuntimeError('"{0}" is not a whole number (>=0)'.format(vv))
    return ii


def elapsed(start, end):
    assert isinstance(start, float)
    assert isinstance(end, float)
    assert start >= 0.0
    assert start <= end
    hours, rem = divmod(end - start, 3600)
    minutes, seconds = divmod(rem, 60)
    return '{:0>2}:{:0>2}:{:05.2f}'.format(int(hours), int(minutes), seconds)


def get_output(
    cmd=None,
    cwd=None,
    stdin=None,
    stderr=subprocess.STDOUT,
    shell=False,
):
    """Use subprocess.check_ouput to run subcommand."""
    if cmd is None:
        cmd = ['echo', 'NO COMMAND SPECIFIED']
    if cwd is None:
        cwd = os.getcwd()
    if shell:
        warnings.warn('[!] invoking subprocess with "shell=True"')
    output = subprocess.check_output(
        cmd,
        cwd=cwd,
        stdin=stdin,
        stderr=stderr,
        shell=shell  # nosec
    ).decode('UTF-8').splitlines()
    return output


class Timer(object):  # NOQA: WPS214
    """Timer object usable as a context manager, or for manual timing. Based on
    code from http://coreygoldberg.blogspot.com/2012/06/python-timer-class-
    context-manager-for.html  # NOQA.

    As a context manager, do:

        from timer import Timer

        url = 'https://github.com/timeline.json'
        with Timer() as t:
            r = requests.get(url)
        print('fetched %r in %.2f millisecs' % (url, t.elapsed*1000))
    """
    def __init__(self, task_description='elapsed time', verbose=False):
        self.verbose = verbose
        self.task_description = task_description
        self.laps = OrderedDict()

    def __enter__(self):
        """Record initial time."""
        self.start(lap='__enter__')
        if self.verbose:
            sys.stdout.write('{0}...'.format(self.task_description))
            sys.stdout.flush()
        return self

    def __exit__(self, *args):
        """Record final time."""
        self.stop()
        backspace = '\b\b\b'
        if self.verbose:
            sys.stdout.flush()
            if self.elapsed_raw() < 1.0:
                sys.stdout.write(
                    '{0}:{1:.2f}ms\n'.format(
                        backspace, self.elapsed_raw() * 1000,
                    )
                )
            else:
                sys.stdout.write(
                    '{0}: {1}\n'.format(backspace, self.elapsed())
                )
            sys.stdout.flush()

    def start(self, lap=None):
        """Record starting time."""
        tt = time.time()
        first = None if any(self.laps) \
            else self.laps.iteritems().next()[0]
        if first is None:
            self.laps['__enter__'] = tt
        if lap is not None:
            self.laps[lap] = tt
        return tt

    def lap(self, lap='__lap__'):
        """Records a lap time.

        If no lap label is specified, a single 'last lap' counter will
        be (re)used. To keep track of more laps, provide labels
        yourself.
        """
        tt = time.time()
        self.laps[lap] = tt
        return tt

    def stop(self):
        """Record stop time."""
        return self.lap(lap='__exit__')

    def get_lap(self, lap='__exit__'):
        """Get the timer for label specified by 'lap'."""
        return self.lap[lap]

    def elapsed_raw(self, start='__enter__', end='__exit__'):
        """Return the elapsed time as a raw value."""
        return self.laps[end] - self.laps[start]

    def elapsed(self, start='__enter__', end='__exit__'):
        """Return a formatted string with elapsed time between 'start' and
        'end' kwargs (if specified) in HH:MM:SS.SS format."""
        hours, rem = divmod(self.elapsed_raw(start, end), 3600)
        minutes, seconds = divmod(rem, 60)
        return '{0:0>2}:{1:0>2}:{2:05.2f}'.format(
            int(hours), int(minutes), seconds
        )


def safe_to_open(filename, overwrite=False):
    """Ensure that file can be opened without over-writing (unless --force)."""
    if os.path.exists(filename):
        statinfo = os.stat(filename)
        if (statinfo.st_size > 0 and not overwrite):
            raise RuntimeError(
                'File "{0}" exists. Use --force to overwrite.'.format(
                    filename
                ),
            )
    return True


class BZ2_LineReader(object):
    """Class to implement an iterator outputting individual JSON records from
    BZ2 compressed data hosted at a specific URL.

    Based on code example from:
    https://stackoverflow.com/questions/47778579/how-to-read-lines-from-arbitrary-bz2-streams-for-csv
    """  # NOQA

    def __init__(self, url=None, buffer_size=None, verify=True):
        if buffer_size is None:
            buffer_size = 6 * 1024
        self.url = url
        self.buffer_size = buffer_size
        self.verify = verify
        self.bytes_transferred = 0
        self.decompressor = BZ2Decompressor()
        self.buffer = ''
        self.first_line = None

    def __len__(self):
        """Return number of bytes transfered."""
        return self.bytes_transferred

    def first_line(self):
        """Return the first line read (header?)"""
        return self.first_line

    def readlines(self, maxlines=None):
        """Returns lines."""
        with requests.get(
            self.url,
            stream=True,
            verify=self.verify,
        ) as fh:
            if fh.status_code == 404:
                raise RuntimeError('file not found: {0}'.format(self.url))
            for row in self._line_reader(fh, maxlines=maxlines):
                yield row

    def _line_reader(self, fh, maxlines=None):
        """Line reader."""
        count = 0
        for chunk in fh.iter_content(chunk_size=self.buffer_size):
            self.bytes_transferred += len(chunk)
            block = self.decompressor.decompress(chunk)
            if sys.version_info >= (3, ):  # Python 3
                block = block.decode('utf-8')  # Convert bytes to string.
            if block:
                self.buffer += block
            if '\n' in self.buffer or '\r\n' in self.buffer:
                lines = self.buffer.splitlines()
                if lines:
                    self.buffer = '' if lines[-1].endswith('\n') or \
                        lines[-1].endswith('\r\n') else lines.pop()
                    for line in lines:
                        if self.first_line is None:
                            self.first_line = line
                        yield line
                        count += 1
                        if maxlines is not None and count == int(maxlines):
                            # TODO(dittrich): Is this really a problem, wemake?
                            # WPS438 Found `StopIteration` raising inside
                            # generator
                            raise StopIteration  # NOQA: WPS438


class LineReader(object):
    """Class to implement an iterator outputting individual lines from
    uncompressed data hosted at a specific URL.

    Based on code example from:
    https://stackoverflow.com/questions/47778579/how-to-read-lines-from-arbitrary-bz2-streams-for-csv
    """

    def __init__(self, url=None, buffer_size=None, verify=True):
        """Object initializer."""
        if buffer_size is None:
            buffer_size = 6 * 1024
        self.url = url
        self.buffer_size = buffer_size
        self.verify = verify
        self.bytes_transferred = 0
        self.buffer = ''
        self.first_line = None

    def __len__(self):
        """Return number of bytes transfered."""
        return self.bytes_transferred

    def first_line(self):
        """Return the first line read (header?)"""
        return self.first_line

    def readlines(self, maxlines=None):
        """Returns lines."""
        with requests.get(self.url, stream=True, verify=self.verify) as fh:
            if fh.status_code == 404:
                raise RuntimeError('file not found: {0}'.format(self.url))
            for row in self._line_reader(fh, maxlines=maxlines):
                yield row

    def _line_reader(self, fh, maxlines=None):
        """Line reader."""
        count = 0
        for block in fh.iter_content(chunk_size=self.buffer_size):
            self.bytes_transferred += len(block)
            if sys.version_info >= (3, ):  # Python 3
                block = block.decode('utf-8')  # Convert bytes to string.
            if block:
                self.buffer += block
            if '\n' in self.buffer or '\r\n' in self.buffer:
                lines = self.buffer.splitlines()
                if lines:
                    self.buffer = '' if lines[-1].endswith('\n') or \
                        lines[-1].endswith('\r\n') else lines.pop()
                    for line in lines:
                        if self.first_line is None:
                            self.first_line = line
                        yield line
                        count += 1
                        if maxlines is not None and count >= int(maxlines):
                            # TODO(dittrich): Is this really a problem, wemake?
                            # WPS438 Found `StopIteration` raising inside
                            # generator
                            raise StopIteration  # NOQA: WPS438


# vim: set fileencoding=utf-8 ts=4 sw=4 tw=0 et :
