#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Techies' Stasis Trap

:copyright: (c) 2014 Runzhou Li (Leo)
:license: The MIT License (MIT), see LICENSE for details.
"""

import sys
from logging import Handler, NOTSET

_ref_atributes = [
    '%(levelname)s',
    '%(name)s',
    '%(pathname)s',
    '%(module)s',
    '%(funcName)s',
    '%(lineno)d',
    '%(message)s'
]

'''
Reference log format, best used with UniQueue or CountQueue
'''
REF_LOG_FORMAT = ':'.join(_ref_atributes)


class QueueHandler(Handler):

    '''
    Queue Logging Handler

    Inherits standard logging.Handler that emits to any standard Queue
    compatible implementations. Including the ones in techies.landmines module
    '''

    def __init__(self, q, level=NOTSET):
        if sys.version_info[:2] > (2, 6):
            super(QueueHandler, self).__init__(level)
        else:
            Handler.__init__(self, level)

        self.q = q

    def emit(self, record):
        try:
            self.q.put(self.format(record))
        except (KeyboardInterrupt, SystemExit):
            raise
        except:
            self.handleError(record)
