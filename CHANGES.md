## Changelog

### 0.1.3 (2014-01-20)

* Added `QueueHandler`, inherits standard `logging.Handler` that `emit` to any standard `Queue` compatible implementations, including all the `Queue` implementations in this library
* Exposed accessibility of all classes (`Queue` implementations and `logging.Handler` implementations to bypass module namespace)
* Behavior of `CountQueue.get` has changed from just returning the item value to a `tuple` of item value and its number of appearances in the queue, eg: `('dota', 2)`; an empty `tuple` is returned when the `CountQueue` is empty

### 0.1.2 (2014-01-17)

* Added `CountQueue`, inherits `UniQueue` but the score is used as a count of item appearance, that the item has the highest count gets placed in front to be `get` first
* Behavior of all `Queue` and its subclasses' `put` and `put_nowait` methods changed from return certain value to not return anything (more Python standard Queue like)

### 0.1.1 (2014-01-16)

* Python 3.2 and 3.3 supported now
* Behavior of both `Queue` and `UniQueue`'s `get` method changed from returning `None` to empty "native string" (unicode for Python 2.x, str for Python 3.x) when attempting to dequeue from an empty queue

### 0.1.0 (2014-01-16)

* Initial release with Redis backed `Queue` and `UniQueue`
