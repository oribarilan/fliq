#  <img src="assets/flick_emoji_2_small.png" alt="drawing" width="40" height="40"/> Fliq

Fluent-syntax Lazily-evaluated Integrated Query.

[![Python Versions](https://img.shields.io/badge/python-3.9%20|%203.10%20|%203.11-blue)](https://www.python.org/downloads/)
[![Downloads](https://img.shields.io/pypi/dm/fliq?link=https%3A%2F%2Fpypi.org%2Fproject%2Fop-log%2F)](https://pypi.org/project/fliq/)
[![build](https://img.shields.io/github/actions/workflow/status/oribarilan/fliq/package_build.yml)](https://github.com/oribarilan/fliq/actions/workflows/package_build.yml)
[![lint](https://img.shields.io/github/actions/workflow/status/oribarilan/fliq/lint.yml?label=lint)](https://github.com/oribarilan/fliq/actions/workflows/lint.yml)
[![coverage](https://img.shields.io/github/actions/workflow/status/oribarilan/fliq/coverage.yml?label=coverage%3E95%25)](https://github.com/oribarilan/fliq/actions/workflows/coverage.yml)
[![Ruff](https://img.shields.io/endpoint?url=https://raw.githubusercontent.com/astral-sh/ruff/main/assets/badge/v2.json)](https://github.com/astral-sh/ruff)

Fliq is a lightweight Python library for high-performance processing of iterables,
inspired by [Django's ORM](https://docs.djangoproject.com/en/4.2/topics/db/queries/)
and [LINQ](https://learn.microsoft.com/en-us/dotnet/standard/linq/).
It provides a fluent syntax for lazily-evaluated operations on iterables, 
and it is tested to have on-par performance with the standard library.

Fluent is:

- **Readable & Easy**: Designed for readability and ease of use. Using fluent syntax.
- **Lightweight**: Thin wrapper for the standard library. No dependencies.
- **Performant**: On-par with the standard library. 
Abstraction overhead is kept to a minimum, keeping CPython performance. 
- **Lazy**: All operations are lazy, and only evaluated when needed. 
This provides a performance boost for cases where user would have used list-comprehension otherwise.
- **Compatible**: Compatible with APIs consuming iterables.

## Query (aka q) API

{{auto_api}}

## Roadmap
### Carriers
- [x] where (aka filter)
- [x] select (aka map)
- [x] exclude (aka where_not) 
- [x] distinct
- [ ] group_by
- [x] order_by
- [x] reverse
- [ ] skip
- [ ] take
- [ ] zip
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
- [ ] any
- [ ] all
- [ ] sum
- [ ] min
- [ ] max
- [ ] average