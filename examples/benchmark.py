from dataclasses import dataclass
from fliq import q
import timeit

@dataclass
class Person:
    name: str
    age: int


people = [Person('Alice', 28), Person('Bob', 24), Person('Charlie', 29), Person('David', 23)]


def using_fliq():
    return q(people).where(lambda p: p.age > 25).select(lambda p: p.name).first()


# Standard library
def using_standard_lib():
    return next(map(lambda p: p.name, filter(lambda p: p.age > 25, people)))


# Benchmark
fliq_time = timeit.timeit(using_fliq, number=1000000)
std_lib_time = timeit.timeit(using_standard_lib, number=1000000)

print(f"Using fliq: {fliq_time:.5f} seconds")
print(f"Using standard lib: {std_lib_time:.5f} seconds")