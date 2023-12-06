# Getting Started

## Installation
```bash
pip install fliq
```

## Usage
Fliq's main class is called `Query`.
We suggest you import it as `q`, because you will use it all the time 😉
```python
from fliq import q
q([1, 2, 3, 4, 5]).take(1)
```
You can also import it as `Query` if you prefer, we don't judge:
```python
from fliq import Query
Query([1, 2, 3, 4, 5]).take(1)
```

## What is a Query, and why should you use it?
A `Query` can be viewed as a wrapper for any python iterable.
It guarantees that the iterable will be evaluated lazily,
and provides a rich set of methods for transforming and querying the data.

1. ⚡️ Data will only be materialized when you ask for it. This means that you can
   create a `Query` from a very large iterable, and only materialize a small
   portion of it. This is extremely efficient.
2. 🔗 The methods provided by `Query` are designed to be chained together, so you
   can create complex data pipelines in a very readable way.
3. 🧩 `Query` supports a wide range of data sources, including lists, tuples,
   dictionaries, generators, other `Query` objects and even infinite iterables. This means that
   you can easily combine data from multiple sources into a single pipeline.`
4. The list goes on...

So the question is... Why not?

## I am excited! What's next? 🤩

1. We know it is hard to believe, but it is true! Breath in, breath out, and continue to (2).
2. Take a look at our easy-to-follow examples: [Examples](examples.md)
3. Wonder around our API Reference
   * Understand what are mappers and materializers at [API Intro](reference/api_intro.md)
   * Check out our rich functionality at [API Index](reference/code_api/api_index.md)
   * Make sure you don't miss our special functionality, linked from the top of the API Index.