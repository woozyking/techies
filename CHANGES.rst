Changelog
---------

0.2.0 (2015-04-17)
~~~~~~~~~~~~~~~~~~

-  Removed ``hiredis`` from requirements.txt since it is not a hard
   requirement. Users who wish to take advantage of ``hiredis`` can
   always install it themselves, following the concept of ``redis-py``.
-  Added ``MultiCounter``, a stateless multi-event counter, based on
   Redis ``Hash``.
-  Added ``TsCounter``, a stateless timestamp counter based on Redis
   ``Hash``, and making use of multiple keys to group timestamps, with
   auto expiration based on Redis key TTL mechanism.
-  **Breaking Change**: ``StateCounter`` now has a new behavior when its
   objects are casted by ``str`` and ``unicode``. ``get_all()`` is now
   ``json()``. This change directly reflects the underlying change
   described in the next point. Also, ``started`` and ``stopped`` are
   now properties instead of methods.
-  Simplified ``techies.landmines.RedisBase`` by factoring out its new
   child class ``techies.landmines.RedisHashBase``. All Redis Hash based
   implementations now extends from this class to get unicode ``dict``
   by calling ``json()`` method (previously ``get_all()``), and unicode
   string serialization of the ``dict`` by casting the objects using
   ``str`` or ``unicode`` (both behave exactly the same).

0.1.4 (2014-01-22)
~~~~~~~~~~~~~~~~~~

-  Added ``StateCounter``, a state counter based on Redis ``Hash``. To
   see an example of its usage, see
   `tidehunter <https://github.com/woozyking/tidehunter#example-2-without-limit>`__.
-  Included ``hiredis`` in requirements.txt for added performance gain.

0.1.3 (2014-01-20)
~~~~~~~~~~~~~~~~~~

-  Added ``QueueHandler``, inherits standard ``logging.Handler`` that
   ``emit`` to any standard ``Queue`` compatible implementations,
   including all the ``Queue`` implementations in this library
-  Exposed direct accessibility of all intended APIs, for example,
   ``from techies import Queue``; or if you will,
   ``from techies import *``
-  Behavior of ``CountQueue.get`` has changed from just returning the
   item value to a ``tuple`` of item value and its number of appearances
   in the queue, eg: ``('dota', 2)``; an empty ``tuple`` is returned
   when the ``CountQueue`` is empty

0.1.2 (2014-01-17)
~~~~~~~~~~~~~~~~~~

-  Added ``CountQueue``, inherits ``UniQueue`` but the score is used as
   a count of item appearance, that the item has the highest count gets
   placed in front to be ``get`` first
-  Behavior of all ``Queue`` and its subclasses' ``put`` and
   ``put_nowait`` methods changed from return certain value to not
   return anything (more Python standard Queue like)

0.1.1 (2014-01-16)
~~~~~~~~~~~~~~~~~~

-  Python 3.2 and 3.3 supported now
-  Behavior of both ``Queue`` and ``UniQueue``'s ``get`` method changed
   from returning ``None`` to empty "native string" (unicode for Python
   2.x, str for Python 3.x) when attempting to dequeue from an empty
   queue

0.1.0 (2014-01-16)
~~~~~~~~~~~~~~~~~~

-  Initial release with Redis backed ``Queue`` and ``UniQueue``
