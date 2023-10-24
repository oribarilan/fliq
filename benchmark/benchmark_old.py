from dataclasses import dataclass
from fliq import q
import timeit


@dataclass
class Person:
    name: str
    age: int


def gen_data(num: int):
    return [Person(f"Person {i}", i) for i in range(num)]


# get the last letter of the name of the first person over 25 years old


def using_fliq(num: int):
    return lambda: (
        q(gen_data(num))
        .where(lambda p: p.age > 25)
        .select(lambda p: p.name)
        .select(lambda name: name[-1])
        .first_or_default(default=Person("No one", 0))
    )


# Standard library
def using_standard_lib(num: int):
    return lambda: next(
        map(lambda name: name[-1],
            map(lambda p: p.name,
                filter(lambda p: p.age > 25, gen_data(num))))) or Person("No one", 0)


results = []
for b in [100, 1000, 10_000, 100_000, 1_000_000]:
    print(f"running benchmark: {b} items")
    fliq_time = timeit.timeit(using_fliq(b), number=100)
    std_lib_time = timeit.timeit(using_standard_lib(b), number=100)
    print(f"Using fliq: {fliq_time:.5f} seconds")
    print(f"Using standard lib: {std_lib_time:.5f} seconds")
    print(f"Ratio: fliq is {fliq_time / std_lib_time:.2f} times slower")
    results.append(fliq_time / std_lib_time)
    print()

print(f"on avg, fliq is {sum(results) / len(results):.2f} "
      f"times slower than standard lib")
