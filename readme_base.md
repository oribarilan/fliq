#  <img src="docs/assets/flick_emoji_2_small.png" alt="drawing" width="40" height="40"/> Fliq

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

{{auto_api}}

## Roadmap

### Special Functionality
- [ ] arithmetic (aka add, +, subtract, -, multiply, *, divide, /, modulo, %)
- [ ] conversion (aka to_list, to_set, to_dict, to_tuple, to_string, to_int, to_float, to_bool)
- [ ] iteration (aka for_each, for_each_indexed, for_each_pair, for_each_pair_indexed)
- [ ] len

### Streamers

#### Special Streamers

- [x] snap (aka cache, materialize)

#### Common Streamers

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

#### Special Collectors

- [x] in / not in (aka membership)
- [x] == / != (aka equality)

#### Common Collectors

- [x] first
- [x] first_or_default
- [x] get
- [x] to_list
- [x] count
- [x] any
- [x] all
- [x] aggregate
- [x] contains
- [x] equals

#### Numeric Collectors
- [x] sum
- [x] min
- [x] max
- [ ] average