# 🫣 Query Peeking

Queries are lazy and can only be used once (they are exhausted after being iterated).
While this provides a significant performance boost, it can be inconvenient in some cases.

Peeking is a way to look at items in a query, without consuming it.

## Common Use Cases

### Debugging

When debugging a query, it is often useful to see what the next item is, without
consuming the query, since consuming may change the course of the function.
```python
from fliq import q
numbers = q([1, 2, 3, 4, 5])
# Breakpoint here: dev takes a look at the next item using `numbers.peek()`
even = numbers.where(lambda x: x % 2 == 0)  # flow continues as usual
```

### Logging

In some cases, developers may want to log a sample of the data.
However, this may be needed at a point in time where the query does not need to be materialized.
For such case, peeking is useful.
```python
from fliq import q
import logging
numbers = q([1, 2, 3, 4, 5])
logging.info(f"Sample item: {numbers.peek()}")  # logging a sample item
even = numbers.where(lambda x: x % 2 == 0)  # flow continues as usual
```

## Peeking
Peeking is done using the `peek` method.

What makes peeking very powerful, is that you can peek a query at any point in its lifetime.
Yes, even during iteration!
```python hl_lines="7"
from fliq import q
items = q(range(5))
iterated = []
peeked = None
for i, element in enumerate(items):
    if i == 1:
        peeked = items.peek()  # 🫣 peeking during iteration!
    iterated.append(element)
assert iterated == [i for i in range(5)]
assert peeked == 2
```

## `peek()`
::: fliq.query.Query.peek