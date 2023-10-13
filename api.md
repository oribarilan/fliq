* [Streamers](#query.Streamers)
  * [where](#query.Query.where)
  * [select](#query.Query.select)
  * [exclude](#query.Query.exclude)
  * [distinct](#query.Query.distinct)
  * [order\_by](#query.Query.order_by)
  * [reverse](#query.Query.reverse)
  * [slice](#query.Query.slice)
* [Collectors](#query.Collectors)
  * [get](#query.Query.get)
  * [first](#query.Query.first)
  * [first\_or\_default](#query.Query.first_or_default)
  * [count](#query.Query.count)
  * [to\_list](#query.Query.to_list)

<a id="query.Streamers"></a>

### Streamers

<a id="query.Query.where"></a>

### where

```python
def where(predicate: Optional[Predicate] = None) -> 'Query'
```

<a id="query.Query.select"></a>

### select

```python
def select(selector: Callable[[Any], Any]) -> 'Query'
```

<a id="query.Query.exclude"></a>

### exclude

```python
def exclude(predicate: Predicate) -> 'Query'
```

<a id="query.Query.distinct"></a>

### distinct

```python
def distinct(preserve_order: bool = True) -> 'Query'
```

Yields distinct elements, preserving order if specified.
:param preserve_order: Optional. Whether to
preserve the order of the items. Defaults to True.

<a id="query.Query.order_by"></a>

### order\_by

```python
def order_by(selector: Optional[Callable[[Any], Any]] = None,
             ascending: bool = True) -> 'Query'
```

Yields sorted elements in an ascending or descending order,
based on the selector or default ordering.
:param selector: Optional. The selector to sort the iterable by.
If not provided, default ordering is used.
:param ascending: Optional. Whether to sort in ascending or
descending order. Defaults to ascending.

<a id="query.Query.reverse"></a>

### reverse

```python
def reverse() -> 'Query'
```

Yields elements in reverse order.
Notes:
 - in case of an irreversible iterable, TypeError is raised (e.g., set)
 - in case of a generator, the iterable is first converted to a list, then reversed,
 this has a performance impact, and assume a finite generator

<a id="query.Query.slice"></a>

### slice

```python
def slice(start: int = 0,
          stop: Optional[int] = None,
          step: int = 1) -> 'Query'
```

Yields a slice of the iterable.
Examples:
    >>> q(range(10)).slice(start=1, stop=6, step=2)
    [1, 3, 5]
:param start: Optional. The start index of the slice. Defaults to 0.
:param stop: Optional. The stop index of the slice. Defaults to None.
:param step: Optional. The step of the slice. Defaults to 1.

<a id="query.Collectors"></a>

### Collectors

<a id="query.Query.get"></a>

### get

```python
def get(predicate: Optional[Predicate] = None) -> Any
```

<a id="query.Query.first"></a>

### first

```python
def first(predicate: Optional[Predicate] = None) -> Any
```

Collector.
Returns the first item that satisfies the predicate (if provided).
This assumes at least one item exists in the query.
If no items exist, a NoItemsFoundException is raised.
:param predicate: Optional. The predicate to filter the iterable by.

<a id="query.Query.first_or_default"></a>

### first\_or\_default

```python
def first_or_default(predicate: Optional[Predicate] = None,
                     default: Any = None) -> Any
```

Collector.
Returns the first item that satisfies the predicate (if provided).
If no items exist, the default value is returned (None, if not provided).
:param predicate: Optional. The predicate to filter the iterable by.
:param default: Optional. The default value to return if no items are found.

<a id="query.Query.count"></a>

### count

```python
def count() -> int
```

Returns the number of elements in the iterable
:return: The number of the elemtns
:rtype: int

<a id="query.Query.to_list"></a>

### to\_list

```python
def to_list() -> List
```

