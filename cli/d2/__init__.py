# -*- coding: utf-8 -*-

import pbr.version

version_info = pbr.version.VersionInfo('d2')
try:
    __version__ = version_info.version_string()
except AttributeError:
    __version__ = '19.10.0'

try:
    __release__ = version_info.release_string()
except AttributeError:
    __release__ = __version__

__author__ = 'Dave Dittrich'
__email__ = 'dave.dittrich@gmail.com'

__all__ = ['__author__', '__email__', '__version__', '__release__']

# vim: set fileencoding=utf-8 ts=4 sw=4 tw=0 et :
