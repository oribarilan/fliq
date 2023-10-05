from types import GeneratorType
from typing import Iterable


class QueryBase:
    def __init__(self, iterable: Iterable):
        if iterable is None:
            raise TypeError("iterable cannot be None")

        self._collected = False
        self._items = iterable
