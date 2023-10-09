from dataclasses import dataclass
from fliq import q
import timeit

@dataclass
class Person:
    name: str
    age: int


people = [Person(f"Person {i}", i) for i in range(10_000_000)]


def using_fliq():
    return q(people).where(lambda p: p.age > 25).select(lambda p: p.name).select(lambda name: name[-1]).first_or_default(default=Person("No one", 0))


# Standard library
def using_standard_lib():
    return next(map(lambda name: name[-1], map(lambda p: p.name, filter(lambda p: p.age > 25, people)))) or Person("No one", 0)


# Benchmark
fliq_time = timeit.timeit(using_fliq, number=10000)
std_lib_time = timeit.timeit(using_standard_lib, number=10000)

print(f"Using fliq: {fliq_time:.5f} seconds")
print(f"Using standard lib: {std_lib_time:.5f} seconds")