# API Introduction

Fliq provides rich functionality to perform processing on datasets (aka iterables).
This *reference* section provides concepts and a detailed description of the API.

!!! note

    API docs contain type aliases to improve readability:

    - Predicate. ```Predicate = Callable[[T], bool]```
    - Selector. ```Selector = Callable[[T], U]```
    - NumericSelector = ```Selector[T, Union[int, float]]```
    - IndexSelector = ```Selector[T, int]```

## Query
Query is the main object in Fliq. It is an abstracted lazy iterable, 
which can be used to perform processing on datasets.

Query should be perceived as a generator-like collection.

* It provides built-in iterable functionality (such as `for`, `in` etc.).
* It can be exhausted (used only once).

```python
from fliq import q
q([1, 2, 3, 4]).where(lambda x: x % 2 == 0).select(lambda x: x * 2).to_list() 
# [4, 8]  
```

The main functionality of Query can be divided into two categories: 
Mappers methods and Materializer methods.

## Mapper Methods

Mapper methods (aka mappers) are used to transform the data in the Query. They are lazy, and follow fluent syntax.
They can be chained together to create complex transformations that are lazy, 
so they are only executed on demand.
Mappers are implemented using the standard python library, 
so they are highly efficient and performant.

```python
from fliq import q
q([0, 1, 2]).where(lambda x: x % 2 == 0).select(lambda x: x + 1) 
# Query object similar to [1, 3]
```

For the full list of mappers, please refer to the [Mapper Methods](code_api/mapper_methods.md) section.

## Materializer Methods

Materializer methods (aka materializers) are used to perform some action, and return a concrete result.
To do that, they materialize the data in the Query 
(i.e., execute delayed computation, chained thus far).

A Materializer that aggregates the iterable to return a single value is called a _Reducer_.
Most materializers are in-fact reducers.

```python
from fliq import q
q([0, 1, 2]).max() 
# 2
```

There are other materializers, which do not aggregate the iterable to a single value.
For example, `to_list` returns a list of all the items in the iterable.

```python
from fliq import q
q([0, 1, 2]).where(lambda x: x % 2 == 0).to_list() 
# [0, 2]
```

For the full list of mappers, please refer to the [Materializer Methods](code_api/materializer_methods.md) section.

## Special Functionality

You can also find special functionality in the Query API, such as snapshots (`snap()`).
See the relevant pages under the Reference section for more information.