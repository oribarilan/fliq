from types import GeneratorType
from typing import Iterable


class QueryableBase:
    def __init__(self, iterable: Iterable):
        self.items = None

        if iterable is None:
            raise TypeError("iterable cannot be None")

        if isinstance(iterable, GeneratorType):
            iterable = list(iterable)

        self._items = iterable
