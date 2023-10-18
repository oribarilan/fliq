#  <img src="assets/flick_emoji_2_small.png" alt="drawing" width="40" height="40"/> Fliq

Fluent-syntaxed Lazily-evaluated Integrated Query.

[//]: # (bages using https://shields.io/badges/)
[![build](https://img.shields.io/github/actions/workflow/status/oribarilan/fliq/package_build.yml)](https://github.com/oribarilan/fliq/actions/workflows/package_build.yml)
[![lint](https://img.shields.io/github/actions/workflow/status/oribarilan/fliq/lint.yml?label=lint)](https://github.com/oribarilan/fliq/actions/workflows/lint.yml)
[![coverage](https://img.shields.io/github/actions/workflow/status/oribarilan/fliq/coverage.yml?label=coverage%3E95%25)](https://github.com/oribarilan/fliq/actions/workflows/coverage.yml)

[![Python Versions](https://img.shields.io/badge/python-3.9%20|%203.10%20|%203.11-blue)](https://www.python.org/downloads/)
[![PyPI - Version](https://img.shields.io/pypi/v/fliq?color=1E7FBF)](https://pypi.org/project/fliq/)
[![Downloads](https://img.shields.io/pypi/dm/fliq?color=1E7FBF)](https://pypi.org/project/fliq/)
[![Ruff](https://img.shields.io/endpoint?url=https://raw.githubusercontent.com/astral-sh/ruff/main/assets/badge/v2.json)](https://github.com/astral-sh/ruff)

Fliq is a lightweight Python library for high-performance processing of iterables,
inspired by [Django's ORM](https://docs.djangoproject.com/en/4.2/topics/db/queries/)
and [LINQ](https://learn.microsoft.com/en-us/dotnet/standard/linq/).
It provides a fluent syntax for lazily-evaluated operations on iterables, 
and it is tested to have on-par performance with the standard library.

## Installation

```shell
pip install fliq
````

## Fliq

- **Intuitive** to use. Built for readability and usability.
- **Lightweight** wrapper for the standard library. No dependencies or bloat.
- **Efficient** as the standard library. Abstraction overhead is kept to a minimum. 
- **Lazy** operations, evaluated only when needed and only as needed.
- **Compatible** with APIs consuming iterables.

## Motivation

What is the output of the following code?
```python
next(map(lambda x: x * 2, filter(lambda x: x % 2, [1, 2, 3, 4, 5]))) or -1
```

And what about this?
```python
from fliq import q

(q([1, 2, 3, 4, 5])
    .where(lambda x: x % 2 == 0)
    .select(lambda x: x * 2)
    .first_or_default(-1))
```

And this is just a simple example.

Python's standard library provides a rich set of functions for processing iterables.
However, it is not always easy to read and use. 

This is especially true when chaining multiple operations together.
This is where Fliq comes in.
Fliq provides a fluent, easy to read syntax for processing iterables, while keeping
performance on-par with the standard library.

## Query (aka q) API

Note that API docs may contain custom types to improve readability:
- Predicates. ```Predicate = Callable[[Any], bool]```

* [Streamers](#query.Streamers)
  * [snap](#query.Query.snap)
  * [where](#query.Query.where)
  * [select](#query.Query.select)
  * [exclude](#query.Query.exclude)
  * [distinct](#query.Query.distinct)
  * [order](#query.Query.order)
  * [reverse](#query.Query.reverse)
  * [slice](#query.Query.slice)
  * [take](#query.Query.take)
  * [skip](#query.Query.skip)
  * [zip](#query.Query.zip)
* [Collectors](#query.Collectors)
  * [first](#query.Query.first)
  * [first\_or\_default](#query.Query.first_or_default)
  * [single](#query.Query.single)
  * [single\_or\_default](#query.Query.single_or_default)
  * [count](#query.Query.count)
  * [any](#query.Query.any)
  * [all](#query.Query.all)
  * [to\_list](#query.Query.to_list)

<a id="query.Streamers"></a>

### Streamers

<a id="query.Query.snap"></a>

### snap

```python
def snap() -> 'Query'
```

Snap is a unique streamer.
Yields the same elements, and creates a snapshot for the query.
This snapshot allows for multiple iterations over the same elements,
as they were at the point of the snapshot.
If multiple snapshots are created in a query lifetime, the last one is considered.

Assumes a finite iterable.

Example:

    evens = q(range(10)).where(lambda x: x % 2 == 0).cache()
    count = evens.count()                       # <-- 5
    first_even = evens.first()                  # <-- 0
    even_pows = evens.select(lambda x: x ** 2)  # <-- [0, 4, 16, 36, 64]

<a id="query.Query.where"></a>

### where

```python
def where(predicate: Optional[Predicate] = None) -> 'Query'
```

Yields elements that satisfy the predicate (aka filter).

Example:

    q(range(10)).where(lambda x: x % 2 == 0)
    >> [0, 2, 4, 6, 8]

Args:
    <br />
    predicate: Optional. The predicate to filter the iterable by. If None is
    given, no filtering takes place.

<a id="query.Query.select"></a>

### select

```python
def select(selector: Callable[[Any], Any]) -> 'Query'
```

Yields the result of applying the selector function to each element (aka map).

Example:

    q(range(5)).select(lambda x: x * 2 == 0)
    >> [0, 2, 4, 6, 8, 10]

Args:
    <br />
    selector: The selector function to apply to each element.

<a id="query.Query.exclude"></a>

### exclude

```python
def exclude(predicate: Predicate) -> 'Query'
```

Yields elements that do not satisfy the predicate.

Example:

    q(range(5)).exclude(lambda x: x > 3)
    >> [0, 1, 2, 3]

Args:
    <br />
    predicate: The predicate to filter the iterable by.

<a id="query.Query.distinct"></a>

### distinct

```python
def distinct(preserve_order: bool = True) -> 'Query'
```

Yields distinct elements, preserving order if specified.

Example:
    q([0, 1, 0, 2, 2]).distinct()
    >> [0, 1, 2]

Args:
    <br />
    preserve_order: Optional. Whether to preserve the order of the items. Defaults to True.

<a id="query.Query.order"></a>

### order

```python
def order(by: Optional[Callable[[Any], Any]] = None,
          ascending: bool = True) -> 'Query'
```

Yields elements in sorted order.

Example:

    q([4, 3, 2, 1, 0]).order()
    >> [0, 1, 2, 3, 4]

Args:
    <br />
    by: a selector function to extract the key from an item, defaults to None.
    If None, the default ordering is used.
    <br />
    ascending: whether to sort in ascending or descending order, defaults to True.

<a id="query.Query.reverse"></a>

### reverse

```python
def reverse() -> 'Query'
```

Yields elements in reverse order.
Notes:
 - in case of an irreversible iterable, TypeError is raised (e.g., set).
 - in case of an iterator, it is first converted to a list, then reversed,
 this has a performance and memory impact, and assumes a finite iterator.

 Example:

    q([0, 1, 2, 3, 4]).order()
    >> [4, 3, 2, 1, 0]

Raises:
    <br />
    TypeError: In case the iterable is irreversible.

<a id="query.Query.slice"></a>

### slice

```python
def slice(start: int = 0,
          stop: Optional[int] = None,
          step: int = 1) -> 'Query'
```

Yields a slice of the iterable.
Example:

    q(range(10)).slice(start=1, stop=6, step=2)
    >> [1, 3, 5]

Args:
    <br />
    start: Optional. The start index of the slice. Defaults to 0.
    <br />
    stop: Optional. The stop index of the slice. Defaults to None.
    <br />
    step: Optional. The step of the slice. Defaults to 1.

<a id="query.Query.take"></a>

### take

```python
def take(n: int = 1, predicate: Optional[Predicate] = None) -> 'Query'
```

Yields up to n items that satisfies the predicate (if provided).
In case the iterable is ordered, the first n items are returned.

Args:
    <br />
    n: Optional. The number of items to take. Defaults to 1.
    <br />
    predicate: Optional. The predicate to filter the iterable by.

<a id="query.Query.skip"></a>

### skip

```python
def skip(n: int = 1) -> 'Query'
```

Yields the items after skipping the first n items (as returned from the iterator).

Example:

    q(range(10)).skip(n=5)
    >> [5, 6, 7, 8, 9]

Args:
    <br />
    n: Optional. The number of items to take. Defaults to 1.

<a id="query.Query.zip"></a>

### zip

```python
def zip(*iterables: Iterable) -> 'Query'
```

Yields tuples of the items of the iterable with the input iterables.
The iteration stops as soon as one of the input iterables is exhausted.

Example:

    q(range(5)).zip(range(5, 10), range(10, 15)
    >> [(0, 5, 10), (1, 6, 11), (2, 7, 12), (3, 8, 13), (4, 9, 14)]

Args:
    <br />
    *iterables: One or more iterables to zip with the iterable.

<a id="query.Collectors"></a>

### Collectors

<a id="query.Query.first"></a>

### first

```python
def first(predicate: Optional[Predicate] = None) -> Any
```

<a id="query.Query.first_or_default"></a>

### first\_or\_default

```python
def first_or_default(predicate: Optional[Predicate] = None,
                     default: Any = None) -> Any
```

<a id="query.Query.single"></a>

### single

```python
def single(predicate: Optional[Predicate] = None) -> Any
```

<a id="query.Query.single_or_default"></a>

### single\_or\_default

```python
def single_or_default(predicate: Optional[Predicate] = None,
                      default: Any = None) -> Any
```

<a id="query.Query.count"></a>

### count

```python
def count() -> int
```

Returns the number of elements in the iterable
:return: The number of the elements in the iterable
:rtype: int

<a id="query.Query.any"></a>

### any

```python
def any(predicate: Optional[Predicate] = None) -> bool
```

Returns whether any element in the iterable evaluates to true.
If a predicate is provided, only elements that satisfy the predicate are considered.
Args:
    predicate: Optional. The predicate to filter the iterable by.

Returns:
    True if any element evaluates to true, False otherwise.

<a id="query.Query.all"></a>

### all

```python
def all(predicate: Optional[Predicate] = None) -> bool
```

Returns whether all elements in the iterable evaluate to true.
If a predicate is provided, only elements that satisfy the predicate are considered.
Args:
    predicate: Optional. The predicate to filter the iterable by.

Returns:
    True if all elements evaluate to true, False otherwise.

<a id="query.Query.to_list"></a>

### to\_list

```python
def to_list() -> List
```



## Roadmap

### Special Functionality
- [x] snap (aka cache)

### Streamers
- [x] where (aka filter)
- [x] select (aka map)
- [x] exclude (aka where_not) 
- [x] distinct
- [ ] group_by
- [x] order_by
- [x] reverse
- [x] slice
- [x] skip
- [ ] skip_last
- [x] take
- [x] zip
- [ ] remove
- [ ] append
- [ ] prepend
- [ ] concat

### Collectors
- [x] first
- [x] first_or_default
- [x] get
- [x] to_list
- [x] count
- [x] any
- [x] all
- [ ] sum
- [ ] min
- [ ] max
- [ ] average