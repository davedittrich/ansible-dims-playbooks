#!/usr/bin/env python3
# -*- coding: utf-8 -*-

# Setup script for the LiminalAI CLI utility
#
# Author: Dave Dittrich <dave.dittrich@gmail.com>
# URL: ...

import codecs
import os
import re

from setuptools import find_packages, setup


PROJECT = 'd2'

try:
    with open('README.rst') as readme_file:
        long_description = readme_file.read()
except IOError:
    long_description = ''

try:
    with open('HISTORY.rst') as history_file:
        history = history_file.read().replace('.. :changelog:', '')
except IOError:
    history = ''


def get_contents(*args):
    """Get the contents of a file relative to the source distribution directory."""  # noqa
    with codecs.open(get_absolute_path(*args), 'r', 'UTF-8') as handle:
        return handle.read()


def get_version(*args):
    """Extract the version number from a Python module."""
    contents = get_contents(*args)
    metadata = dict(re.findall('__([a-z]+)__ = [\'"]([^\'"]+)', contents))
    return metadata['version']


def get_absolute_path(*args):
    """Transform relative pathnames into absolute pathnames."""
    return os.path.join(os.path.dirname(os.path.abspath(__file__)), *args)


setup(
    name='d2',
    pbr=True,
    # version=get_version('d2', '__init__.py'),
    #
    description="Python CLI for LiminalAI",
    long_description=long_description + "\n\n" + history,

    author="Dave Dittrich",
    author_email='dave.dittrich@gmail.com',

    url='https://github.com/davedittrich/ansible-dims-playbooks',
    download_url='https://github.com/davedittrich/ansible-dims-playbooks/tarball/master',  # noqa

    namespace_packages=[],
    packages=find_packages(),
    package_dir={'d2':
                 'd2'},
    include_package_data=True,

    python_requires='>=3.6,!=3.0.*,!=3.1.*,!=3.2.*,!=3.3.*',
    install_requires=get_contents('requirements.txt'),

    license="Apache Software License",
    keywords='d2',
    classifiers=[
        'Development Status :: 2 - Pre-Alpha',
        'Intended Audience :: Information Technology',
        'Intended Audience :: Science/Research',
        'Intended Audience :: Other Audience',
        'License :: OSI Approved :: Apache Software License',
        'Natural Language :: English',
        'Operating System :: OS Independent',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.6',
        'Programming Language :: Python :: 3.7',
    ],

    test_suite='tests',

    entry_points={
        'console_scripts': [
            'd2 = d2.main:main',
        ],
        'd2': [
            'about = d2.about:About',
            'project create = d2.project.create:Create',
            'project delete = d2.project.delete:Delete',
            'project list = d2.project.list:List',
        ],
    },
    zip_safe=False,
)
