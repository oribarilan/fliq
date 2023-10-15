* [Streamers](#query.Streamers)
  * [where](#query.Query.where)
  * [select](#query.Query.select)
  * [exclude](#query.Query.exclude)
  * [distinct](#query.Query.distinct)
  * [order](#query.Query.order)
  * [reverse](#query.Query.reverse)
  * [slice](#query.Query.slice)
  * [take](#query.Query.take)
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

<a id="query.Query.where"></a>

### where

```python
def where(predicate: Optional[Predicate] = None) -> 'Query'
```

Yields elements that satisfy the predicate (aka filter).

Example:
    <br />
    `q(range(10)).where(lambda x: x % 2 == 0)`
    <br />
    `[0, 2, 4, 6, 8]`

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
    <br />
    `q(range(5)).select(lambda x: x * 2 == 0)`
    <br />
    `[0, 2, 4, 6, 8, 10]`

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
    <br />
    `q(range(5)).exclude(lambda x: x > 3)`
    <br />
    `[0, 1, 2, 3]`

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
    <br />
    `q([0, 1, 0, 2, 2]).distinct()`
    <br />
    `[0, 1, 2]`

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
    <br />
    `q([4, 3, 2, 1, 0]).order()`
    <br />
    `[0, 1, 2, 3, 4]`

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
 - in case of an irreversible iterable, TypeError is raised (e.g., set)
 - in case of a generator, the iterable is first converted to a list, then reversed,
 this has a performance impact, and assume a finite generator

 Example:
    <br />
    `q([0, 1, 2, 3, 4]).order()`
    <br />
    `[4, 3, 2, 1, 0]`

<a id="query.Query.slice"></a>

### slice

```python
def slice(start: int = 0,
          stop: Optional[int] = None,
          step: int = 1) -> 'Query'
```

Yields a slice of the iterable.
Examples:
    <br />
    `q(range(10)).slice(start=1, stop=6, step=2)`
    <br />
    `[1, 3, 5]`

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
def take(n: int, predicate: Optional[Predicate] = None) -> 'Query'
```

Yields up to n items that satisfies the predicate (if provided).
In case the iterable is ordered, the first n items are returned.
Args:
    <br />
    n: Optional. The number of items to take. Defaults to 1.
    <br />
    predicate: Optional. The predicate to filter the iterable by.

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
def first_or_default(default: Any = None,
                     predicate: Optional[Predicate] = None) -> Any
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
:return: The number of the elemtns
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

