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

