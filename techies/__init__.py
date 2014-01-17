#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Opinionated Python toolbox

:copyright: (c) 2014 Runzhou Li (Leo)
:license: The MIT License (MIT), see LICENSE for details.
"""

__title__ = 'techies'
__version__ = '0.1.2'
VERSION = tuple(map(int, __version__.split('.')))
__author__ = 'Runzhou Li (Leo)'
__license__ = 'The MIT License (MIT)'
__copyright__ = 'Runzhou Li (Leo)'

from techies import landmines

__all__ = [
    'landmines'
]

# Set default logging handler to avoid "No handler found" warnings.
import logging

try:  # Python 2.7+
    from logging import NullHandler
except ImportError:  # pragma: no cover
    class NullHandler(logging.Handler):

        def emit(self, record):
            pass

logging.getLogger(__name__).addHandler(NullHandler())
