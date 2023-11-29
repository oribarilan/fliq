from __future__ import annotations

from typing import Any


class TrackingIterator:
    def __init__(self, iterable) -> None:
        self.iterable = iter(iterable)
        self.count = 0

    def __iter__(self) -> TrackingIterator:
        return self

    def __next__(self) -> Any:
        self.count += 1
        return next(self.iterable)
