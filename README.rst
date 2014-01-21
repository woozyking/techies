techies
=======

Opinionated Python toolbox

Master branch: |Build Status|

List of Tools
-------------

``Queue`` Implementations (backed by Redis)
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

1. ``techies.Queue``, based on Redis List. Interfaces are almost
   standard queue compatible.
2. ``techies.UniQueue``, based on Redis Sorted Set. Inherits
   ``techies.Queue`` but ignores repetitive items, keeps items unique.
   Score of the sorted set member is epoch timestamp from
   ``time.time()``.
3. ``techies.CountQueue``, based on Redis Sorted Set. Inherits
   ``techies.UniQueue`` but score is used as a count of item appearance,
   that the item has the highest count gets placed in front to be
   ``get`` first.

``logging.Handler`` Implementation
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

1. ``techies.QueueHandler``, inherits standard ``logging.Handler`` that
   ``emit`` to any standard ``Queue`` compatible implementations,
   including all the ``Queue`` implementations in this library.

Prerequisites
-------------

-  Redis server for ``Queue`` implementations

Installation
------------

::

    $ pip install techies
    $ pip install techies --upgrade  # to update

Usage
-----

``Queue``
~~~~~~~~~

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

``UniQueue``
~~~~~~~~~~~~

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

``CountQueue``
~~~~~~~~~~~~~~

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

QueueHandler
~~~~~~~~~~~~

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
installed and running

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
