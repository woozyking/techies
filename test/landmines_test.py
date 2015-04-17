#!/usr/bin/env python
# -*- coding: utf-8 -*-

import unittest
import random
import string
import time

try:
    import simplejson as json
except:
    import json

import sys
import os

target_path = os.path.join(os.path.dirname(__file__), '..', 'techies')
sys.path.append(target_path)

# Compat layer to support some tests
from compat import (
    unicode, xrange
)


# test utility
def random_key():
    return ''.join(
        random.SystemRandom().choice(string.ascii_uppercase) for _ in xrange(12)
    )

# Test Targets
from landmines import (
    RedisBase, RedisHashBase,
    MultiCounter, TsCounter,
    Queue, UniQueue, CountQueue, StateCounter
)


class RedisBaseTest(unittest.TestCase):

    def setUp(self):
        self.key = random_key()
        self.obj = RedisBase(self.key)

    def test_initialize(self):
        self.obj.initialize()

    def test_clear(self):
        self.obj.clear()
        self.assertFalse(self.obj.conn.exists(self.key))

        self.obj.conn.set(self.key, random.randint(1, 32))
        self.obj.clear()
        self.assertFalse(self.obj.conn.exists(self.key))

    def tearDown(self):
        self.obj.conn.delete(self.key)


class RedisHashBaseTest(RedisBaseTest):

    def setUp(self):
        self.key = random_key()
        self.obj = RedisHashBase(self.key)

    def test_json(self):
        v = self.obj.json()
        self.assertEqual(v, {})

        a = random.randint(1, 10)
        self.obj.conn.hset(self.key, 'a', a)
        v = self.obj.json()
        self.assertEqual(int(v.get('a')), a)

    def test_str(self):
        v = str(self.obj)
        self.assertEqual(json.loads(v), {})

        a = random.randint(1, 10)
        self.obj.conn.hset(self.key, 'a', a)
        v = str(self.obj)
        self.assertEqual(int(json.loads(v).get('a')), a)

    def test_unicode(self):
        v = unicode(self.obj)
        self.assertEqual(json.loads(v), {})

        a = random.randint(1, 10)
        self.obj.conn.hset(self.key, 'a', a)
        v = unicode(self.obj)
        self.assertEqual(int(json.loads(v).get('a')), a)


class MultiCounterTest(RedisHashBaseTest):

    def setUp(self):
        self.key = random_key()
        self.obj = MultiCounter(self.key)

    def test_get_count(self):
        v = self.obj.get_count('f1')
        self.assertEqual(v, 0)

    def test_incr(self):
        self.obj.incr('f1')
        v = self.obj.conn.hget(self.key, 'f1')
        self.assertEqual(int(v), 1)


class TsCounterTest(RedisHashBaseTest):

    def setUp(self):
        self.key = random_key()
        self.obj = TsCounter(self.key)

    def test_initialize(self):
        if sys.version_info[:2] > (2, 6):
            super(TsCounterTest, self).test_initialize()
        else:
            RedisHashBaseTest.test_initialize(self)

        self.assertEqual(self.obj.chunk_size, 86400)
        self.assertEqual(self.obj.ttl, self.obj.chunk_size * 2)

        self.obj.initialize(chunk_size=3600)
        self.assertEqual(self.obj.chunk_size, 3600)
        self.assertEqual(self.obj.ttl, self.obj.chunk_size * 2)

        self.obj.initialize(chunk_size=86400, ttl=31536000)
        self.assertEqual(self.obj.chunk_size, 86400)
        self.assertEqual(self.obj.ttl, 31536000)

    def test_get_count(self):
        v = self.obj.get_count()
        self.assertEqual(v, 0)

        t = time.time()
        self.obj.incr(t)
        v = self.obj.get_count(t)
        self.assertEqual(v, 1)

    def test_incr(self):
        t = int(time.time())
        self.obj.incr(t)
        v = self.obj.get_count(t)
        self.assertEqual(v, 1)

        c = t - t % self.obj.chunk_size
        k = '{0}:{1}'.format(self.key, c)
        ttl = c + self.obj.ttl - t
        eps = abs(self.obj.conn.ttl(k) - ttl) / float(ttl)
        self.assertLessEqual(eps, 0.05)  # allows 5% eps

    def test_clear(self):
        self.obj.clear()
        self.assertEqual(self.obj._chunks(), [])

        t = time.time()
        self.obj.incr(t - 86400)
        self.obj.incr(t)
        self.obj.incr(t + 86400)
        self.obj.clear()
        self.assertEqual(self.obj._chunks(), [])

    def test_json(self):
        self.assertEqual(self.obj.json(), {})

        t = time.time()
        self.obj.incr(t - 86400)
        self.obj.incr(t)
        self.obj.incr(t + 86400)
        v = self.obj.json()

        for chunk in self.obj._chunks():
            self.assertNotEqual(v.get(chunk), {})

    def test_str(self):
        # todo
        pass

    def test_unicode(self):
        # todo
        pass

    def tearDown(self):
        if sys.version_info[:2] > (2, 6):
            super(TsCounterTest, self).tearDown()
        else:
            RedisHashBaseTest.tearDown(self)

        keys = self.obj.conn.keys(self.key + ':*')
        keys.append(self.key)

        if len(keys) > 0:
            self.obj.conn.delete(*keys)


class StateCounterTest(RedisHashBaseTest):

    def setUp(self):
        self.key = random_key()
        self.obj = StateCounter(self.key)

    def test_initialize(self):
        self.obj.initialize(total=50)
        v = self.obj.conn.hget(self.key, 'total')
        self.assertEqual(int(v), 0)

        self.obj.conn.delete(self.key)
        self.obj.initialize(total=50)
        v = self.obj.conn.hget(self.key, 'total')
        self.assertEqual(int(v), 50)

    def test_json(self):
        v = self.obj.json()
        self.assertEqual(int(v.get('count')), 0)
        self.assertEqual(int(v.get('state')), 1)
        self.assertEqual(int(v.get('total')), 0)

    def test_str(self):
        v = json.loads(str(self.obj))
        self.assertEqual(int(v.get('count')), 0)
        self.assertEqual(int(v.get('state')), 1)
        self.assertEqual(int(v.get('total')), 0)

    def test_unicode(self):
        v = json.loads(unicode(self.obj))
        self.assertEqual(int(v.get('count')), 0)
        self.assertEqual(int(v.get('state')), 1)
        self.assertEqual(int(v.get('total')), 0)

    def test_get_state(self):
        self.assertEqual(self.obj.get_state(), 1)

        self.obj.conn.hset(self.key, 'state', 0)
        self.assertEqual(self.obj.get_state(), 0)

    def test_get_count(self):
        self.assertEqual(self.obj.get_count(), 0)

        c = random.randint(1, 100)
        self.obj.conn.hset(self.key, 'count', c)
        self.assertEqual(self.obj.get_count(), c)

    def test_get_total(self):
        self.assertEqual(self.obj.get_total(), 0)

        c = random.randint(1, 100)
        self.obj.conn.hset(self.key, 'total', c)
        self.assertEqual(self.obj.get_total(), c)

    def test_start(self):
        c = random.randint(1, 100)
        self.obj.conn.hset(self.key, 'count', c)
        self.obj.conn.hset(self.key, 'state', 0)

        self.obj.start()
        self.assertEqual(self.obj.get_state(), 1)
        self.assertEqual(self.obj.get_count(), 0)
        self.assertEqual(self.obj.get_total(), c)

    def test_stop(self):
        c = random.randint(1, 100)
        self.obj.conn.hset(self.key, 'count', c)
        self.obj.conn.hset(self.key, 'state', 1)

        self.obj.stop()
        self.assertEqual(self.obj.get_state(), 0)
        self.assertEqual(self.obj.get_count(), 0)
        self.assertEqual(self.obj.get_total(), c)

    def test_incr(self):
        self.assertEqual(self.obj.get_count(), 0)
        self.obj.incr()
        self.assertEqual(self.obj.get_count(), 1)

    def test_started(self):
        self.assertTrue(self.obj.started)
        self.obj.stop()
        self.assertFalse(self.obj.started)
        self.obj.start()
        self.assertTrue(self.obj.started)

    def test_stopped(self):
        self.assertFalse(self.obj.stopped)
        self.obj.stop()
        self.assertTrue(self.obj.stopped)
        self.obj.start()
        self.assertFalse(self.obj.stopped)


class QueueTest(RedisBaseTest):

    def setUp(self):
        self.key = random_key()
        self.obj = Queue(self.key)

    def test_qsize(self):
        self.assertEqual(self.obj.qsize(), 0)

        s = random.randint(1, 32)
        for i in xrange(s):
            self.obj.put(i)

        self.assertEqual(self.obj.qsize(), s)

    def test_empty(self):
        self.assertTrue(self.obj.empty())

        self.obj.put(random.randint(1, 13))
        self.assertFalse(self.obj.empty())

        self.obj.get()
        self.assertTrue(self.obj.empty())

    def test_len(self):
        self.assertEqual(len(self.obj), 0)

        s = random.randint(1, 32)
        for i in xrange(s):
            self.obj.put(i)

        self.assertEqual(len(self.obj), s)

    def test_put(self):
        a = random.randint(1, 32)
        self.obj.put(a)
        v = self.obj.get()
        self.assertEqual(int(v), a)

    def test_get(self):
        self.assertEqual(self.obj.get(), unicode())

        a = random.randint(1, 32)
        self.obj.put(a)
        v = self.obj.get()
        self.assertEqual(int(v), a)


class UniQueueTest(QueueTest):

    def setUp(self):
        self.key = random_key()
        self.obj = UniQueue(self.key)

    def test_qsize(self):
        if sys.version_info[:2] > (2, 6):
            super(UniQueueTest, self).test_qsize()
        else:
            QueueTest.test_qsize(self)

        self.obj.clear()

        s = random.randint(1, 32)
        n = random.randint(2, 5)
        for _ in xrange(n):
            for i in xrange(s):
                self.obj.put(i)

        self.assertEqual(self.obj.qsize(), s)


class CountQueueTest(UniQueueTest):

    def setUp(self):
        self.key = random_key()
        self.obj = CountQueue(self.key)

    def test_get(self):
        self.assertEqual(self.obj.get(), ())

        a = random.randint(1, 32)
        n = random.randint(1, 5)
        for _ in xrange(n):
            self.obj.put(a)

        v = self.obj.get()
        self.assertEqual(v, (unicode(a), n))

    def test_put(self):
        a = random.randint(1, 32)
        n = random.randint(1, 5)
        for _ in xrange(n):
            self.obj.put(a)

        v = self.obj.get()
        self.assertEqual(v, (unicode(a), n))

if __name__ == '__main__':
    unittest.main()
