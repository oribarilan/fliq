from __future__ import annotations  # For Python 3.7+

from typing import Callable, Iterable, Any, List
from typing import TypeVar, Generic

T = TypeVar('T')


class Channel(Generic[T]):
    def __init__(self, func: Callable[[Iterable[T]], Any]):
        self._func = func

    def __call__(self, iterable: Iterable[T]) -> Any:
        return self._func(iterable)

    def __repr__(self):
        return f"Channel({self._func.__name__})"
