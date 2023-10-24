import csv
import timeit
from dataclasses import dataclass
from typing import Callable, Iterable


@dataclass
class NamedMethod:
    name: str
    method: Callable[[Iterable], None]


class BenchmarkRunner:
    def __init__(self, scenario_name: str, m1: NamedMethod, m2: NamedMethod,
                 dataset_generator: Callable[[int], Iterable]):
        self.scenario_name = scenario_name
        self.methods = [m1.method, m2.method]
        self.method_names = [m1.name, m2.name]
        self.dataset_generator = dataset_generator

    def _benchmark(self, method: Callable[[Iterable], None], dataset: Iterable):
        start_time = timeit.default_timer()
        method(dataset)
        return timeit.default_timer() - start_time

    def run(self, sizes: Iterable[int], output_csv: str):
        with open(output_csv, 'w', newline='') as csvfile:
            csv_writer = csv.writer(csvfile)
            header = ['Dataset'] + self.method_names
            csv_writer.writerow(header)

            for size in sizes:
                print(f"Running benchmark for dataset size: {size}")
                results = [size]
                for i, method in enumerate(self.methods):
                    print(f"Running benchmark for method: {self.method_names[i]}")
                    results.append(self._benchmark(method, self.dataset_generator(size)))
                csv_writer.writerow(results)
