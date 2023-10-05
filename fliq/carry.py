from typing import Callable, Iterable, Any


class Carry:
    def __init__(self, func: Callable[[Iterable[Any]], Any]):
        self._func = func

    def __call__(self, iterable: Iterable[Any]) -> Any:
        return self._func(iterable)

    def __repr__(self):
        return f"Carry({self._func.__name__})"
