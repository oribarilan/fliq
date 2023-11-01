# Query Partitioning

Query partitioning is a way to split a query into n sub-queries, 
that a mutually exclusive and collectively exhaustive (MECE).

!!! note

    Paritioning is done lazily: 

    - It does not incur any performance penalty.
        Thus, it can be freely used even where logic 
        may lead to some sub-queries eventually not being consumed.
    - It supports infinite iterables, as long as there are 
        finite sequences between elements of different partitions.

One common use case is to split a query into two sub-queries.

## `partition()`
::: fliq.query.Query.partition