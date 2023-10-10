from time import perf_counter
from typing import Optional


class Timer:
    def __init__(self):
        self.elapsed: float = 0
        self.start: float = 0
        self.readout: Optional[str] = None

    def __enter__(self):
        self.start = perf_counter()
        return self

    def __exit__(self, type, value, traceback):
        self.elapsed = perf_counter() - self.start
        self.readout = f'Time: {self.elapsed:.10f} seconds'
