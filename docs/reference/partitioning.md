# ✂️ Query Partitioning

Query partitioning is a time and space efficient way to split a query into n sub-queries, 
that a mutually exclusive and collectively exhaustive (MECE).
The original iterable is only iterated once, and the sub-queries are lazily evaluated.

!!! note

    Paritioning is done lazily. It does not incur any performance penalty.
    Thus, it can be freely used even where logic 
    may lead to some sub-queries eventually not being consumed.
    
One common use case is to split a query into two sub-queries, depending on a condition.
So, for example, instead of writing:
```python
numbers = [1, 2, 3, 4, 5]
even = [x for x in numbers if x % 2 == 0]
od = [x for x in numbers if x % 2 != 0]
```
Using Fliq, you can write:
```python
from fliq import q
numbers = q([1, 2, 3, 4, 5])
even, od = numbers.partition(lambda x: x % 2 == 0)
```

This is more:

* **Time-efficient**. The iterable is only iterated once.
* **Space-efficient**. Both sub-queries are lazily evaluated, so they do not materialize the iterable, 
thus using less memory.
* **Readable**. Less repetitive, more declarative.

## `partition()`
::: fliq.query.Query.partition