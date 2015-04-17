#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Techies' landmines

:copyright: (c) 2014 Runzhou Li (Leo)
:license: The MIT License (MIT), see LICENSE for details.
"""

from __future__ import unicode_literals
from techies.compat import (
    unicode, nativestr, unicode_data
)

import time
import redis

try:
    import simplejson as json
except:
    import json


class RedisBase(object):

    def __init__(self, key, host='localhost', port=6379, db=0, **kwargs):
        pool = redis.ConnectionPool(host=host, port=port, db=db)
        self.conn = redis.StrictRedis(connection_pool=pool)
        self.key = key

        self.initialize(**kwargs)

    def initialize(self, **kwargs):
        pass

    def clear(self, **kwargs):
        self.conn.delete(self.key)
        self.initialize(**kwargs)


class RedisHashBase(RedisBase):

    def __str__(self):
        return json.dumps(
            unicode_data(self.json()), ensure_ascii=False
        )

    def __unicode__(self):
        return self.__str__()

    def json(self):
        return unicode_data(self.conn.hgetall(self.key))


class MultiCounter(RedisHashBase):

    '''
    A stateless multi-event counter, based on Redis Hash

    Hash fields:
        event_1: positive int value
        event_2: positive int value
        ...
        event_N: positive int value
    '''

    def get_count(self, field):
        return int(self.conn.hget(self.key, field) or 0)

    def incr(self, field):
        self.conn.hincrby(self.key, field, 1)


class TsCounter(RedisHashBase):

    '''
    A stateless multi-key, single-event timestamp counter, based on Redis
    Hash

    Similar to MultiCounter, but instead of using only one key, it
    bundles timestamps of the same chunk. Therefore conceptually the
    user passes in a namespace instead of a key in constructor. In
    initialize(), user can define chunk size in order to group
    timestamps under different redis keys with a format of
    <namespace>:<chunk>; user can also pass in a TTL for these keys to
    make the mechanism overall memory efficient.

    The chunk is calculated as <timestamp> - <timestamp> % <chunk_size>

    Hash fields:
        timestamp_1: positive int value
        timestamp_2: positive int value
        ...
        timestamp_N: positive int value
    '''

    def initialize(self, **kwargs):
        # default chunk_size is 86400 seconds (1 day)
        self.chunk_size = kwargs.get('chunk_size', 86400)
        # default ttl is chunk_size * 2
        self.ttl = kwargs.get('ttl', self.chunk_size * 2)

    def get_count(self, timestamp=None):
        if not timestamp:
            timestamp = time.time()

        timestamp = int(timestamp)
        key = '{0}:{1}'.format(
            self.key, timestamp - timestamp % self.chunk_size
        )

        return int(self.conn.hget(key, timestamp) or 0)

    def incr(self, timestamp=None):
        if not timestamp:
            timestamp = time.time()

        timestamp = int(timestamp)
        chunk = timestamp - timestamp % self.chunk_size
        key = '{0}:{1}'.format(self.key, chunk)

        self.conn.hincrby(key, timestamp, 1)
        self.conn.expireat(key, chunk + self.ttl)

    def _chunks(self):
        return self.conn.keys(self.key + ':*')

    def clear(self):
        chunks = self._chunks()

        if len(chunks) > 0:
            self.conn.delete(*chunks)

    def json(self):
        r = {}

        for chunk in self._chunks():
            r[chunk] = self.conn.hgetall(chunk)

        return unicode_data(r)


class StateCounter(RedisHashBase):

    '''
    A single event state counter, based on Redis Hash

    Hash fields:
        state: 1 or 0 (on or off, respectively)
        count: positive int value (current count)
        total: positive int value (total count since init)
    '''

    def initialize(self, **kwargs):
        if not self.conn.exists(self.key):
            self.start()
            self.conn.hset(self.key, 'total', kwargs.get('total', 0))

    def clear(self):
        self.conn.delete(self.key)

    def get_state(self):
        return int(self.conn.hget(self.key, 'state') or 0)

    def get_count(self):
        return int(self.conn.hget(self.key, 'count') or 0)

    def get_total(self):
        return int(self.conn.hget(self.key, 'total') or 0)

    def start(self):
        if self.stopped:
            self._count2total()
            self.conn.hset(self.key, 'state', 1)

    def stop(self):
        self.conn.hset(self.key, 'state', 0)
        self._count2total()

    def _count2total(self):
        self.conn.hincrby(self.key, 'total', self.get_count())
        self.conn.hset(self.key, 'count', 0)

    def incr(self):
        if self.stopped:
            self.start()

        self.conn.hincrby(self.key, 'count', 1)

    @property
    def started(self):
        return bool(self.get_state())

    @property
    def stopped(self):
        return not self.started

    def get_all(self):

        ''' deprecated, use json() '''

        return self.json()


class Queue(RedisBase):

    '''
    Queue, based on Redis List

    Interfaces are almost standard queue compatible
    '''

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

        ret = self.conn.zrevrange(
            self.key, 0, 0, withscores=True, score_cast_func=int
        )[0]

        # Pop it out
        self.conn.zrem(self.key, ret[0])

        return unicode(nativestr(ret[0])), ret[1]
