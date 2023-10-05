from typing import Iterable


class QueryBase:
    def __init__(self, iterable: Iterable):
        if iterable is None:
            raise TypeError("iterable cannot be None")

        if not isinstance(iterable, Iterable):
            raise TypeError("iterable must be an iterable")

        self._items = iterable
