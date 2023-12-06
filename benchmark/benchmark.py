import random
from pathlib import Path
from typing import Iterable

import pandas as pd
import matplotlib.pyplot as plt

from benchmark_runner import NamedMethod, BenchmarkRunner
from csv_plotter import CsvPlotter
from fliq import q
from fliq.tests.fliq_test_utils import Person, gen_people


# s1: get the oldest male

def s1_fliq(dataset: Iterable):
    shuffled = list(dataset)
    random.shuffle(shuffled)
    return (q(dataset)
            .zip(shuffled)
            .where(lambda ps: ps[0].gender != ps[1].gender)
            .order(by=lambda ps: ps[0].age+ps[1].age)
            .take(5)
            .to_list())


def s1_std_lib(dataset: Iterable):
    shuffled = list(dataset)
    random.shuffle(shuffled)
    return sorted(
        filter(lambda ps: ps[0].gender != ps[1].gender, zip(dataset, shuffled)),
        key=lambda ps: ps[0].age+ps[1].age
    )[:5]


def s2_fliq(dataset: Iterable):
    first = [Person(name="Invitee1", age=i, gender='F') for i in range(len(dataset))]
    last = [Person(name="Invitee1", age=i, gender='F') for i in range(len(dataset))]
    return (q(dataset)
            .where(lambda p: 0 <= p.age < 100)
            .prepend_many(first)
            .append_many(last)
            .select(lambda p: p.name)
            .to_list())


def s2_std_lib(dataset: Iterable):
    first = [Person(name="Invitee1", age=i, gender='F') for i in range(len(dataset))]
    last = [Person(name="Invitee1", age=i, gender='F') for i in range(len(dataset))]
    return list(
        map(lambda p: p.name, first + list(
            filter(lambda p: 0 <= p.age < 100, dataset)) + last)
    )


def s3_fliq(dataset: Iterable):
    return q(dataset).select(lambda p: p.age * 2 if p.age % 2 == 0 else Person.default()).to_list()


def s3_std_lib(dataset: Iterable):
    return list((p.age * 2 if p.age % 2 == 0 else Person.default() for p in dataset))


def plot_benchmark(csv_path):
    # Read CSV file
    df = pd.read_csv(csv_path)

    # Rename x axis ticks to be the dataset size in thousands in the format of 1k, 10k, 1M
    def format_ticks(x):
        if x < 1000:
            return x
        elif x < 1_000_000:
            return f"{x // 1000}k"
        else:
            return f"{x // 1_000_000}M"
    df['Dataset'] = df['Dataset'].apply(format_ticks)

    # Set dataset as index
    df.set_index('Dataset', inplace=True)

    # Rename x axis to "Dataset Size"
    df.rename(columns={'Dataset': 'Dataset Size'}, inplace=True)

    # Plot the results in a compact way
    df.plot(kind='bar', figsize=(8, 4), rot=0, width=0.7)

    plt.title('Benchmark Results')
    plt.ylabel('Execution Time (seconds)')
    plt.xlabel('Dataset')

    plt.yscale('log')
    plt.grid(axis='y')
    plt.tight_layout()

    # add label to the top of each bar with a white background behind the black label
    for p in plt.gca().patches:
        plt.gca().annotate(f"{p.get_height():.3f}",
                           (p.get_x() + p.get_width() / 2, p.get_height()),
                           ha='center', va='center', color='b', xytext=(0, 10),
                           textcoords='offset points', bbox=dict(facecolor='white'))

    # save to the same filename as the csv file
    plt.savefig(csv_path.replace(".csv", ".png"))


BenchmarkRunner(
    scenario_name="Scenario 1",
    m1=NamedMethod("Fliq", s1_fliq),
    m2=NamedMethod("Standard Library", s1_std_lib),
    dataset_generator=gen_people,
).run(
    sizes=[
        1_00,
        10_000,
        1_000_000,
    ],
    output_csv="s1.csv",
)

BenchmarkRunner(
    scenario_name="Scenario 2",
    m1=NamedMethod("Fliq", s2_fliq),
    m2=NamedMethod("Standard Library", s2_std_lib),
    dataset_generator=gen_people,
).run(
    sizes=[
        1_00,
        10_000,
        1_000_000,
    ],
    output_csv="s2.csv",
)

BenchmarkRunner(
    scenario_name="Scenario 3",
    m1=NamedMethod("Fliq", s3_fliq),
    m2=NamedMethod("Standard Library", s3_std_lib),
    dataset_generator=gen_people,
).run(
    sizes=[
        1_00,
        10_000,
        1_000_000,
    ],
    output_csv="s3.csv",
)

CsvPlotter(Path('s1.csv')).plot_benchmark()
CsvPlotter(Path('s2.csv')).plot_benchmark()
CsvPlotter(Path('s3.csv')).plot_benchmark()


