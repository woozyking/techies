techies
=======

Opinionated Python toolbox

Master branch: |Build Status|

Prerequisites
-------------

-  Redis server for Counters and Python ``Queue`` implementations.

Installation
------------

::

    $ pip install techies
    $ pip install techies --upgrade

In The Box
----------

Counters (backed by Redis)
~~~~~~~~~~~~~~~~~~~~~~~~~~

*New in 0.2.0* ``techies.MultiCounter`` is a stateless multi-event
counter, based on Redis ``Hash``.

.. code:: python

    from techies import MultiCounter

    counter = MultiCounter(key='demo_counter')

    counter.incr('event_1')
    counter.incr('event_1')
    counter.incr('event_2')
    counter.incr('event_3')
    counter.incr('event_2')

    print(counter.get_count('event_1'))  # 2
    print(counter.get_count('event_2'))  # 2
    print(counter.get_count('event_3'))  # 1
    print(counter.get_count('event_null'))  # 0

    print(counter.json())  # {u'event_2': u'4', u'event_3': u'2', u'event_1': u'4'}
    print(unicode(counter))  # {"event_2": "2", "event_3": "1", "event_1": "2"}
    print(str(counter))  # same as above

    # clears the counts
    counter.clear()

*New in 0.2.0* ``techies.TsCounter`` is a stateless multi-key,
single-event timestamp counter, based on Redis ``Hash``.

.. code:: python

    from techies import TsCounter
    import time

    # initialize with chunk_size and ttl defined
    counter = TsCounter(
        key='demo_event',
        chunk_size=24 * 60 * 60,
        ttl=48 * 60 * 60
    )
    # or call initialize() method later to customize chunk_size and/or ttl
    counter.initialize(chunk_size=24 * 60 * 60, ttl=48 * 60 * 60)

    t = time.time()

    counter.incr(timestamp=t - 86400)
    counter.incr(timestamp=t - 86400)
    counter.incr(timestamp=t)
    counter.incr(timestamp=t - 86400)
    counter.incr(timestamp=t + 86400)
    counter.incr(timestamp=t + 86400)

    print(counter.get_count(timestamp=t - 86400))  # 3
    print(counter.get_count(timestamp=t))  # 1
    print(counter.get_count(timestamp=t + 86400))  # 2

    print(counter.json())  # {u'demo_event:1429142400': {u'1429162301': u'3'}, u'demo_event:1429228800': {u'1429248701': u'1'}, u'demo_event:1429315200': {u'1429335101': u'2'}}
    print(unicode(counter))  # {"demo_event:1429142400": {"1429162301": "3"}, "demo_event:1429228800": {"1429248701": "1"}, "demo_event:1429315200": {"1429335101": "2"}}
    print(str(counter))  # same as above

    # clears the counts
    counter.clear()

``techies.StateCounter`` is a single event state counter, based on Redis
``Hash``. Project
```tidehunter`` <https://github.com/woozyking/tidehunter>`__ is built
around the concept and APIs of this counter, you can find some extended
usage example on its `project
page <https://github.com/woozyking/tidehunter>`__. **Breaking API
Changes from 0.1.4 to 0.2.0**: ``StateCounter`` now has a new behavior
when its objects are casted by ``str`` and ``unicode``. ``get_all()`` is
now ``json()``, and ``started`` and ``stopped`` are now properties
instead of methods.

Python ``Queue`` Implementations (backed by Redis)
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

``techies.Queue``, based on Redis ``List``. Interfaces are almost
standard queue compatible.

.. code:: python

    from techies import Queue

    q = Queue(key='demo_q', host='localhost', port=6379, db=0)

    # put, or enqueue
    q.put('lol')
    q.put('dota')
    q.put('skyrim')
    q.put('dota')

    # Check size of the queue, two ways
    print(q.qsize())  # 4
    print(len(q))  # 4

    # get, or dequeue
    print(q.get())  # 'lol'
    print(q.get())  # 'dota'
    print(q.get())  # 'skyrim'
    print(q.get())  # 'dota'
    print(q.get())  # ''

    # clear the queue
    q.clear()

``techies.UniQueue``, based on Redis ``Sorted Set``. Inherits
``techies.Queue`` but ignores repetitive items, keeps items unique.
Score of the sorted set member is epoch timestamp from ``time.time()``.

.. code:: python

    from techies import UniQueue

    q = UniQueue(key='demo_q', host='localhost', port=6379, db=0)

    # put, or enqueue
    q.put('lol')
    q.put('dota')
    q.put('skyrim')
    q.put('dota')  # this one is ignored

    # Check size of the unique queue, two ways
    print(q.qsize())  # 3
    print(len(q))  # 3

    # get, or dequeue
    print(q.get())  # 'lol'
    print(q.get())  # 'dota'
    print(q.get())  # 'skyrim'
    print(q.get())  # ''  # only 3 unique items

    # clear the queue
    q.clear()

``techies.CountQueue``, based on Redis ``Sorted Set``. Inherits
``techies.UniQueue`` but score is used as a count of item appearance,
that the item has the highest count gets placed in front to be ``get``
first.

.. code:: python

    from techies import CountQueue

    q = CountQueue(key='demo_q', host='localhost', port=6379, db=0)

    # put, or enqueue
    q.put('lol')
    q.put('dota')
    q.put('skyrim')
    q.put('dota')  # increment the count of the existing 'dota'

    # Check size of the unique queue, two ways
    print(q.qsize())  # 3
    print(len(q))  # 3

    # get, or dequeue
    print(q.get())  # ('dota', 2)  # the one with the most count is returned first
    print(q.get())  # ('lol', 1)
    print(q.get())  # ('skyrim', 1)
    print(q.get())  # ()  # only 3 unique items still

    # clear the queue
    q.clear()

Python ``logging.Handler`` Implementation
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

``techies.QueueHandler``, inherits standard ``logging.Handler`` that
``emit`` to any standard ``Queue`` compatible implementations, including
all the ``Queue`` implementations in this library.

.. code:: python

    import logging
    from techies import (
        Queue, UniQueue, CountQueue, QueueHandler, REF_LOG_FORMAT
    )
    from techies.compat import xrange

    if __name__ == '__main__':
        key = 'test_q'
        q = Queue(key=key, host='localhost', port=6379, db=0)
        uq = UniQueue(key=key, host='localhost', port=6379, db=1)
        cq = CountQueue(key=key, host='localhost', port=6379, db=2)

        logger = logging.getLogger(__name__)

        for i in [q, uq, cq]:
            handler = QueueHandler(i)
            handler.setFormatter(logging.Formatter(REF_LOG_FORMAT))
            logger.addHandler(handler)

        # Enqueue multiple times of the same error
        for i in xrange(3):
            try:
                1 / 0
            except ZeroDivisionError as e:
                logger.error(e)

        # simple queue, should print error log 3 times
        while len(q):
            print(q.get())

        # unique queue, should just have 1 item in this case
        print(len(uq) == 1)
        print(uq.get())

        # count queue, should just have 1 item as unique queue
        print(len(cq) == 1)
        print(cq.get()[1])  # 3, the count of the same item

        for i in [q, uq, cq]:
            i.clear()

Test (Unit Tests)
-----------------

To run unit tests locally, make sure that you have Redis server
installed and running locally, where DB 0 is not occupied by any data
that you cannot afford to lose.

::

    $ pip install -r requirements.txt
    $ pip install -r test_requirements.txt
    $ nosetests --with-coverage --cover-package=techies

License
-------

The MIT License (MIT). See the full
`LICENSE <https://github.com/woozyking/techies/blob/master/LICENSE>`__.

.. |Build Status| image:: https://travis-ci.org/woozyking/techies.png?branch=master
   :target: https://travis-ci.org/woozyking/techies
