techies
=======

Opinionated Python toolbox

List of Tools
-------------

1. Redis backed ``techies.landmines.Queue``, provides (almost) what
   Python standard ``Queue`` provides, except that it's semi-persisted
   in Redis.
2. Redis backed ``techies.landmines.UniQueue``, a ``Queue``
   implementation that keeps only distinct items.

Prerequisites
-------------

-  Redis server

Installation
------------

::

    $ pip install techies
    $ pip install techies --upgrade  # to update

Usage
-----

``Queue``

.. code:: python

    from techies.landmines import Queue

    q = Queue(key='demo_q', host='localhost', port=6379, db=0)

    # put, aka enqueue
    q.put('lol')
    q.put('dota')
    q.put('skyrim')

    # check the size of the queue
    print(q.qsize())  # 3
    # or
    print(len(q))  # 3

    # get, aka dequeue
    print(q.get())

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
