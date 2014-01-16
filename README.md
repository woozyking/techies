# techies

Opinionated Python toolbox

Master branch: [![Build Status](https://travis-ci.org/woozyking/techies.png?branch=master)](https://travis-ci.org/woozyking/techies)

## List of Tools

1. Redis backed `techies.landmines.Queue`, (almost) Python standard `Queue` compatible, the main difference is that it's semi-persisted in Redis.
2. Redis backed `techies.landmines.UniQueue`, a `Queue` implementation that keeps only distinct items.

## Prerequisites

* Redis server

## Installation

```
$ pip install techies
$ pip install techies --upgrade  # to update
```

## Usage

`Queue`

```python
from techies.landmines import Queue

q = Queue(key='demo_q', host='localhost', port=6379, db=0)

# put, or enqueue
print(q.put('lol'))  # 1L
print(q.put('dota'))  # 2L
print(q.put('skyrim'))  # 3L
print(q.put('dota'))  # 4L
# Queue.put returns the queue size at that moment

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
```

`UniQueue`

```python
from techies.landmines import UniQueue

q = UniQueue(key='demo_q', host='localhost', port=6379, db=0)

# put, or enqueue
print(q.put('lol'))  # 1
print(q.put('dota'))  # 1
print(q.put('skyrim'))  # 1
print(q.put('dota'))  # 0
# UniQueue.put returns 1 on success, 0 otherwise; such as duplicated item

# Check size of the unique queue, two ways
print(q.qsize())  # 3
print(len(q))  # 3

# get, or dequeue
print(q.get())  # 'lol'
print(q.get())  # 'dota'
print(q.get())  # 'skyrim'
print(q.get())  # ''
print(q.get())  # ''

# clear the queue
q.clear()
```

## Test (Unit Tests)

To run unit tests locally, make sure that you have Redis server installed and running

```
$ pip install -r requirements.txt
$ pip install -r test_requirements.txt
$ nosetests --with-coverage --cover-package=techies
```

## License

The MIT License (MIT). See the full [LICENSE](https://github.com/woozyking/techies/blob/master/LICENSE).
