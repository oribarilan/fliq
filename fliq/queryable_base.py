from typing import Iterable


class QueryableBase:
    def __init__(self, iterable: Iterable):
        self._items = iterable
