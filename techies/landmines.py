#!/usr/bin/env python
# -*- coding: utf-8 -*-


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
    A minimum data queue, based on Redis List
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
        return self.conn.rpush(self.key, var)

    def put_nowait(self, var):
        return self.put(var, False)

    def get(self, block=True, timeout=None):
        return self.conn.lpop(self.key)

    def get_nowait(self):
        return self.get(False)


class UniQueue(Queue):

    '''
    An unique data queue, based on Redis Sorted Set

    Data in this queue are unique
    '''

    def qsize(self):
        return int(self.conn.zcard(self.key))

    def put(self, var, block=True, timeout=None):
        if not self.conn.zscore(self.key, var):
            return self.conn.zadd(self.key, time.time(), var)

        return 0

    def get(self, block=True, timeout=None):
        ret = None

        if not self.empty():
            ret = self.conn.zrange(self.key, 0, 0)[0]

        if self.conn.zscore(self.key, ret):
            self.conn.zrem(self.key, ret)

        return ret
