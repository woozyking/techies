#!/usr/bin/env python
# -*- coding: utf-8 -*-

import unittest
import random
import string
import time

import sys
import os

target_path = os.path.join(os.path.dirname(__file__), '..', 'techies')
sys.path.append(target_path)

# Compat layer to support some tests
from compat import unicode, nativestr

# Test Targets
from landmines import Queue, UniQueue


class QueueTest(unittest.TestCase):

    def setUp(self):
        self.key = 'test_q'
        self.q = Queue(key=self.key, host='localhost', port=6379, db=0)
        self.q.conn.delete(self.key)

    def test_clear(self):
        # When empty
        self.q.clear()
        self.assertEquals(self.q.conn.llen(self.key), 0)

        # After putting
        self.q.conn.rpush(self.key, 'test_val')
        self.q.clear()
        self.assertEquals(self.q.conn.llen(self.key), 0)

    def test__len__(self):
        # When empty
        self.assertEqual(len(self.q), 0)

        # When not empty
        length = random.randint(1, 32)

        for i in range(length):
            self.q.conn.rpush(self.key, i)

        self.assertEqual(len(self.q), length)

        # Uniqueness test
        for i in range(length):
            self.q.conn.rpush(self.key, i)

        self.assertEqual(len(self.q), length * 2)

    def test_full(self):
        # Meaningless now
        self.assertFalse(self.q.full())

    def test_task_done(self):
        self.q.task_done()

    def test_join(self):
        self.q.join()

    def test_qsize(self):
        # When empty
        self.assertEqual(self.q.qsize(), 0)

        # When not empty
        length = random.randint(1, 32)

        for i in range(length):
            self.q.conn.rpush(self.key, i)

        self.assertEqual(self.q.qsize(), length)

        # Uniqueness test
        for i in range(length):
            self.q.conn.rpush(self.key, i)

        self.assertEqual(len(self.q), length * 2)

    def test_empty(self):
        # When empty
        self.assertTrue(self.q.empty())

        # When not empty
        length = random.randint(1, 32)

        for i in range(length):
            self.q.conn.rpush(self.key, i)

        self.assertFalse(self.q.empty())

    def test_put(self):
        val = ''.join(random.choice(string.ascii_uppercase + string.digits)
                      for x in range(32))
        self.assertTrue(self.q.put(val))
        self.assertEqual(nativestr(self.q.conn.lpop(self.key)), unicode(val))

    def test_get(self):
        # When empty
        # self.assertIsNone(self.q.get())
        self.assertEqual(self.q.get(), unicode())

        # When not empty
        val = ''.join(random.choice(string.ascii_uppercase + string.digits)
                      for x in range(32))
        self.q.conn.rpush(self.key, val)
        self.assertEqual(self.q.get(), unicode(val))

    def test_put_nowait(self):
        self.test_put()

    def test_get_nowait(self):
        self.test_get()

    def tearDown(self):
        self.q.conn.delete(self.key)


class UniQueueTest(QueueTest):

    def setUp(self):
        self.key = 'test_q'
        self.q = UniQueue(key=self.key, host='localhost', port=6379, db=0)
        self.q.conn.delete(self.key)

    def test_clear(self):
        # When empty
        self.q.clear()
        self.assertEquals(self.q.conn.llen(self.key), 0)

        # After putting
        self.q.conn.zadd(self.key, time.time(), 'test_val')
        self.q.clear()
        self.assertEquals(self.q.conn.llen(self.key), 0)

    def test__len__(self):
        # When empty
        self.assertEqual(len(self.q), 0)

        # When not empty
        length = random.randint(1, 32)

        for i in range(length):
            self.q.conn.zadd(self.key, time.time(), i)

        self.assertEqual(len(self.q), length)

        # Uniqueness test
        for i in range(length):
            self.q.conn.zadd(self.key, time.time(), i)

        self.assertEqual(len(self.q), length)

    def test_qsize(self):
        # When empty
        self.assertEqual(self.q.qsize(), 0)

        # When not empty
        length = random.randint(1, 32)

        for i in range(length):
            self.q.conn.zadd(self.key, time.time(), i)

        self.assertEqual(self.q.qsize(), length)

        # Uniqueness test
        for i in range(length):
            self.q.conn.zadd(self.key, time.time(), i)

        self.assertEqual(self.q.qsize(), length)

    def test_empty(self):
        # When empty
        self.assertTrue(self.q.empty())

        # When not empty
        length = random.randint(1, 32)

        for i in range(length):
            self.q.conn.zadd(self.key, time.time(), i)

        self.assertFalse(self.q.empty())

    def test_get(self):
        # When empty
        self.assertEqual(self.q.get(), unicode())

        # When not empty
        val = ''.join(random.choice(string.ascii_uppercase + string.digits)
                      for x in range(32))
        self.q.conn.zadd(self.key, time.time(), val)
        self.assertEqual(self.q.get(), unicode(val))

    def test_put(self):
        val = ''.join(random.choice(string.ascii_uppercase + string.digits)
                      for x in range(32))
        self.assertTrue(self.q.put(val))
        self.assertEqual(nativestr(self.q.conn.zrange(self.key, 0, 0)[0]),
                         unicode(val))

    def tearDown(self):
        self.q.conn.delete(self.key)
