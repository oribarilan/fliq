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

## Fliq is:

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
- Predicate. ```Predicate = Callable[[Any], bool]```
- Selector. ```Selector = Callable[[Any], Any]```

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
  * [append](#query.Query.append)
  * [append\_many](#query.Query.append_many)
  * [prepend](#query.Query.prepend)
  * [prepend\_many](#query.Query.prepend_many)
* [Collectors](#query.Collectors)
  * [first](#query.Query.first)
  * [first\_or\_default](#query.Query.first_or_default)
  * [single](#query.Query.single)
  * [single\_or\_default](#query.Query.single_or_default)
  * [count](#query.Query.count)
  * [any](#query.Query.any)
  * [all](#query.Query.all)
  * [aggregate](#query.Query.aggregate)
  * [max](#query.Query.max)
  * [min](#query.Query.min)
  * [sum](#query.Query.sum)
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
def select(selector: Selector) -> 'Query'
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
Distinct supports infinite iterables, when preserver_order is True.
Note that the items must be hashable.

Example:

    q([0, 1, 0, 2, 2]).distinct()
    >> [0, 1, 2]

Args:
    <br />
    preserve_order: Optional. Whether to preserve the order of the items. Defaults to True.
    If True, distinct supports infinite iterables.
    If order is not important and iterable is finite, set to False for better performance.

Raises:
    <br />
    TypeError: In case one or more items in the iterable are not hashable.

<a id="query.Query.order"></a>

### order

```python
def order(by: Optional[Selector] = None, ascending: bool = True) -> 'Query'
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

<a id="query.Query.append"></a>

### append

```python
def append(*single_items) -> 'Query'
```

Yields the items of the iterable, followed by the item(s) given.
API also supports multiple arguments, where each is considered as a single item.

Infinite iterables are supported, behaving as expected.

Examples:

    q(range(5)).append(5)
    >> [0, 1, 2, 3, 4, 5]

    q(range(5)).append(5, 6, 7)
    >> [0, 1, 2, 3, 4, 5, 6, 7]

Args:
    <br />
    *single_items: One or more items to add to the end of the iterable.

<a id="query.Query.append_many"></a>

### append\_many

```python
def append_many(items: Iterable) -> 'Query'
```

Yields the items of the iterable, followed by the items given.

Infinite iterables are supported, behaving as expected.

Examples:

    q(range(5)).append_many([5, 6, 7])
    >> [0, 1, 2, 3, 4, 5, 6, 7]

Args:
    <br />
    items: The items to add to the end of the iterable.

Raises:
    <br />
    TypeError: In case the items are not iterable.
    Error will be raised when item is consumed.

<a id="query.Query.prepend"></a>

### prepend

```python
def prepend(*single_items) -> 'Query'
```

Yields the item(s) given, followed by the items of the iterable.
API also supports multiple arguments, where each is considered as a single item.

Infinite iterables are supported, behaving as expected.

Examples:

    q(range(5)).prepend(5)
    >> [5, 0, 1, 2, 3, 4]

    q(range(5)).prepend(5, 6, 7)
    >> [5, 6, 7, 0, 1, 2, 3, 4]

Args:
    <br />
    *single_items: One or more items to add to the start of the iterable.

<a id="query.Query.prepend_many"></a>

### prepend\_many

```python
def prepend_many(items) -> 'Query'
```

Yields the items given, followed by the items of the iterable.

Infinite iterables are supported, behaving as expected.

Examples:

    q(range(5)).prepend_many([5, 6, 7])
    >> [5, 6, 7, 0, 1, 2, 3, 4]

Args:
    <br />
    items: The items to add to the start of the iterable.

Raises:
    <br />
    TypeError: In case the items are not iterable.
    Error will be raised when item is consumed.

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

In most cases, for custom types, user would want to use a predicate or
 consider implementing `__bool__` or `__len__` to support this method.
 see https://docs.python.org/3/reference/datamodel.html#object.__bool__ .

Args:
    <br />
    predicate: Optional. The predicate to filter the iterable by.

<a id="query.Query.all"></a>

### all

```python
def all(predicate: Optional[Predicate] = None) -> bool
```

Returns whether all elements in the iterable evaluate to true.
If a predicate is provided, only elements that satisfy the predicate are considered.

In most cases, for custom types, user would want to use a predicate or
 consider implementing `__bool__` or `__len__` to support this method.
 see https://docs.python.org/3/reference/datamodel.html#object.__bool__ .

Args:
    predicate: Optional. The predicate to filter the iterable by.

<a id="query.Query.aggregate"></a>

### aggregate

```python
def aggregate(by: Callable[[Any, Any], Any], initial: Any = None)
```

Applies an accumulator function over the iterable.

For an optimized summation of numeric values, use `sum`.

Args:
    <br />
    by: The accumulator function to apply to each two elements.
    initial: Optional. The initial value of the accumulator. Defaults to None.
    If provided, it will also serve as the default value for an empty iterable.
    If not provided, the first element of the iterable will be used as the initial value.

<a id="query.Query.max"></a>

### max

```python
def max(by: Optional[Selector] = None) -> Any
```

Returns the maximal element in the query.
If a selector is provided, the maximal selected attribute is returned.

Custom types must provide a selector function or implement value comparisons
(see https://docs.python.org/3/reference/expressions.html#value-comparisons).

Args:
    <br />
    by: Optional. The selector function to test for the maximal element.

Raises:
    <br />
    ValueError: In case the query is empty.

<a id="query.Query.min"></a>

### min

```python
def min(by: Optional[Selector] = None) -> Any
```

Returns the minimal element in the query.
If a selector is provided, the minimal selected attribute is returned.

Custom types must provide a selector function or implement value comparisons
(see https://docs.python.org/3/reference/expressions.html#value-comparisons).

Args:
    <br />
    by: Optional. The selector function to test for the minimal element.

Raises:
    <br />
    ValueError: In case the query is empty.

<a id="query.Query.sum"></a>

### sum

```python
def sum(by: Optional[NumericSelector] = None, accumulator: Any = 0) -> Any
```

Returns the sum of the elements in the iterable.
If a selector is provided, the sum of the selected elements is returned.
If an accumulator is provided, it is used as the initial value for the summation.

For use with custom classes, the class must implement `__add__` and optionally `__radd__`
or provide a selector function.

Use this method for optimized summation of numeric values, for other types of aggregation,
 use aggregate.

Args:
    <br />
    by: Optional. The selector function to apply to each element.
    accumulator: Optional. The initial value of the sum. Defaults to 0.

Returns:
    The sum of the elements in the iterable.

<a id="query.Query.to_list"></a>

### to\_list

```python
def to_list() -> List
```



## Roadmap

### Special Functionality
- [x] snap (aka cache, materialize)
- [ ] membership (aka contains, in)

### Streamers
- [x] where (aka filter)
- [x] select (aka map)
- [x] exclude (aka where_not, remove_all) 
- [x] distinct
- [ ] group_by
- [x] order_by
- [x] reverse
- [x] slice
- [x] skip
- [ ] skip_last
- [x] take
- [x] zip
- [x] append
- [x] prepend
- [x] append_many
- [x] prepend_many

### Collectors
- [x] first
- [x] first_or_default
- [x] get
- [x] to_list
- [x] count
- [x] any
- [x] all
- [x] aggregate

#### Numeric Collectors
- [x] sum
- [x] min
- [x] max
- [ ] average