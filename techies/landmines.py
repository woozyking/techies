#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Techies' landmines

:copyright: (c) 2014 Runzhou Li (Leo)
:license: The MIT License (MIT), see LICENSE for details.
"""

from __future__ import unicode_literals
from techies.compat import (
    unicode, nativestr
)

import time
import redis


class RedisBase(object):

    def __init__(self, key, host='localhost', port=6379, db=0):
        pool = redis.ConnectionPool(host=host, port=port, db=db)
        self.conn = redis.StrictRedis(connection_pool=pool)
        self.key = key

        self.initialize()

    def initialize(self):
        raise NotImplementedError  # pragma: no cover

    def clear(self):
        self.conn.delete(self.key)
        self.initialize()


class Queue(RedisBase):

    '''
    Queue, based on Redis List

    Interfaces are almost standard queue compatible
    '''

    def initialize(self):
        pass

    def qsize(self):
        return self.conn.llen(self.key)

    def empty(self):
        return self.qsize() == 0

    def full(self):
        return False  # need a better mechanism since it's controlled by Redis

    def task_done(self):
        pass

    def join(self):
        pass

    def __len__(self):
        return self.qsize()

    def put(self, var, block=True, timeout=None):
        self.conn.rpush(self.key, var)

    def put_nowait(self, var):
        self.put(var, block=False)

    def get(self, block=True, timeout=None):
        return unicode(nativestr(self.conn.lpop(self.key) or ''))

    def get_nowait(self):
        return self.get(block=False)


class UniQueue(Queue):

    '''
    Unique Queue, based on Redis Sorted Set

    Inherits Queue but ignores repetitive items, keeps items unique. Score of
    the sorted set member is epoch timestamp from time.time()
    '''

    def qsize(self):
        return int(self.conn.zcard(self.key))

    def put(self, var, block=True, timeout=None):
        if not self.conn.zscore(self.key, var):
            self.conn.zadd(self.key, time.time(), var)

    def get(self, block=True, timeout=None):
        if self.empty():
            return unicode()

        ret = self.conn.zrange(self.key, 0, 0)[0]

        # Pop it out
        self.conn.zrem(self.key, ret)

        return unicode(nativestr(ret))


class CountQueue(UniQueue):

    '''
    Count Queue, based on Redis Sorted Set

    Inherits UniQueue but score is used as a count of item appearance, that
    the item has the highest count gets placed in front to be get() first
    '''

    def put(self, var, block=True, timeout=None):
        self.conn.zincrby(self.key, var, 1)

    def get(self, block=True, timeout=None):
        if self.empty():
            return ()

        ret = self.conn.zrevrange(self.key, 0, 0, withscores=True,
                                  score_cast_func=int)[0]

        # Pop it out
        self.conn.zrem(self.key, ret[0])

        return unicode(nativestr(ret[0])), ret[1]
