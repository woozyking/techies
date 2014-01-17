# techies

Opinionated Python toolbox

Master branch: [![Build Status](https://travis-ci.org/woozyking/techies.png?branch=master)](https://travis-ci.org/woozyking/techies)

## List of Tools

### `Queue` Implementations (backed by Redis)

1. `techies.landmines.Queue`, based on Redis List. Interfaces are almost standard queue compatible.
2. `techies.landmines.UniQueue`, based on Redis Sorted Set. Inherits `techies.landmines.Queue` but ignores repetitive items, keeps items unique. Score of the sorted set member is epoch timestamp from `time.time()`.
3. `techies.landmines.CountQueue`, based on Redis Sorted Set. Inherits `techies.landmines.UniQueue` but score is used as a count of item appearance, that the item has the highest count gets placed in front to be `get` first

## Prerequisites

* Redis server for `Queue` implementations

## Installation

```
$ pip install techies
$ pip install techies --upgrade  # to update
```

## Usage

### `Queue`

```python
from techies.landmines import Queue

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
```

### `UniQueue`

```python
from techies.landmines import UniQueue

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
```

### `CountQueue`

```python
from techies.landmines import CountQueue

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
print(q.get())  # 'dota'  # the one with the most count is returned first
print(q.get())  # 'lol'
print(q.get())  # 'skyrim'
print(q.get())  # ''  # only 3 unique items still

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
