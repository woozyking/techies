#!/usr/bin/env python
# -*- coding: utf-8 -*-

import unittest
import random

import sys
import os

import logging

target_path = os.path.join(os.path.dirname(__file__), '..', 'techies')
sys.path.append(target_path)

# Compat layer to support some tests
from compat import (
    unicode, xrange
)

# Queue to support testing
from landmines import (
    Queue, UniQueue, CountQueue
)

# Test Targets
from stasistrap import (
    QueueHandler
)


class QueueHandlerTest(unittest.TestCase):

    def setUp(self):
        self.key = 'test_q'
        self.q = Queue(key=self.key, host='localhost', port=6379, db=0)
        self.uq = UniQueue(key=self.key, host='localhost', port=6379, db=1)
        self.cq = CountQueue(key=self.key, host='localhost', port=6379, db=2)

        self.logger = logging.getLogger(__name__)

        for q in [self.q, self.uq, self.cq]:
            handler = QueueHandler(q)
            _format = '%(levelname)s:%(message)s'
            handler.setFormatter(logging.Formatter(_format))
            self.logger.addHandler(handler)

    def test_emit(self):
        times = random.randint(3, 10)

        # Enqueue multiple times of the same error
        for i in xrange(times):
            try:
                1 / 0
            except ZeroDivisionError as e:
                msg = unicode(e)
                self.logger.error(e)  # this line number is important

        expected = unicode(':').join(
            [
                'ERROR', msg
            ]
        )

        # Simple Queue Test
        self.assertEqual(len(self.q), times)

        while len(self.q):
            actual = self.q.get()
            self.assertEqual(actual, expected)

        # Unique Queue Test
        self.assertEqual(len(self.uq), 1)
        actual = self.uq.get()
        self.assertEqual(actual, expected)
        actual = self.uq.get()
        self.assertEqual(actual, unicode())

        # Count Queue Test
        self.assertEqual(len(self.cq), 1)
        actual = self.cq.get()
        self.assertEqual(actual, (expected, times))
        actual = self.cq.get()
        self.assertEqual(actual, ())

    def tearDown(self):
        self.q.conn.delete(self.key)
        self.uq.conn.delete(self.key)
        self.cq.conn.delete(self.key)

if __name__ == '__main__':
    unittest.main()
