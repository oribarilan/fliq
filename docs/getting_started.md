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

### ⚡ **</>** Speed up your code 

Data will only be materialized when you ask for it. This means that you can
create a `Query` from a very large iterable, and only materialize a small
portion of it. This is extremely efficient.

### 🔥👨‍💻 Speed up your development 
1. 📖 **Readability.** The methods provided by `Query` are designed to be chained together, so you
   can create complex data pipelines with much less cognitive load.
2. 🐞🔍 **Inspectability.** `Query` provides functionality that speeds development. 
   For example, despite being lazy and exhaustible, you can always
   [peek()](reference/code_api/peeking.md) into a query. 
   Moreover, queries have a meaningful [string representation](reference/code_api/representation.md).
   So you can view the contents of a query, without consuming it. This is extremely useful for debugging.

So the question is... Why not?

## I am excited! What's next? 🤩

1. We know it is hard to believe, but it is true! Breath in, breath out, and continue to (2).
2. Take a look at our easy-to-follow examples: [Examples](examples.md)
3. Wonder around our API Reference
   * Understand what are mappers and materializers at [API Intro](reference/api_intro.md)
   * Check out our rich functionality at [API Index](reference/code_api/api_index.md)
   * Make sure you don't miss our special functionality, linked from the top of the API Index.