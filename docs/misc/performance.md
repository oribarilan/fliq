# Performance

Fliq is geared for performance:

* 🛌 It is lazily evaluated without requiring any intentional effort from the user.
* ⚡️ It is also tested to have on-par performance with the standard library.

## Memory
Fliq is lazy. It does not materialize the iterable, unless the operation requires it (e.g., reverse).
This allows Fliq to make minimal use of memory.

Abstracting the (lazy) evaluation, reduces cognitive load from the user, 
thus implicitly opting in for a more efficient computation,
which in turn improves efficiency compared to eager list processing code.

## Performance
Fliq is designed to be a lightweight wrapper for the standard library.
It keeps abstraction overhead to a minimum, 
and it is tested to have on-par performance with the standard library.

There are two mechanisms for checking Fliq's performance: Performance tests and benchmarking.

### Performance Tests
These tests are ran on every commit, and they compare Fliq's performance to the standard library.
They allow performance difference to be `1%` or smaller, and they are ran on every Python version, 3.9 and above.

You can find the performance tests in 
[Performance tests](https://github.com/oribarilan/fliq/blob/main/fliq/tests/system/test_performance.py).

### Benchmarking
Fliq is being benchmarked against the standard library. The list of 
benchmarked scenarios expands over time. 

Currently, there are 2 scenarios tested with varying dataset sizes (100, 10K, 1M).

* Scenario 1: zipping two iterables of Person objects, 
and taking the first 5 (by age asc) that are of different gender.
```python
from fliq import q
from fliq.tests.fliq_test_utils import gen_people
dataset = gen_people(100)
shuffled = q(dataset).shuffle()
q(dataset).zip(shuffled).where(lambda ps: ps[0].gender != ps[1].gender).order(by=lambda ps: ps[0].age+ps[1].age).take(5).to_list()
```
* Scenario 2: filtering prepending and appending a list of Person objects 
```python
from fliq import q
from fliq.tests.fliq_test_utils import gen_people
dataset = gen_people(100)
first = gen_people(200)
last = gen_people(200)
q(dataset).where(lambda p: 0 <= p.age < 100).prepend_many(first).append_many(last).select(lambda p: p.name).to_list()
```

In both scenarios, Fliq is on-par with the standard library:

![Benchmarking](https://github.com/oribarilan/fliq/blob/main/docs/assets/s1.png?raw=true "Scenario 1")
![Benchmarking](https://github.com/oribarilan/fliq/blob/main/docs/assets/s2.png?raw=true "Scenario 2")

You can find the full benchmarking code at [Benchmark](https://github.com/oribarilan/fliq/blob/main/benchmark/benchmark.py).