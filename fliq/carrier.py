from typing import Callable, Any, Iterable, Optional

from fliq.carry import Carry
from fliq.queryable_base import QueryableBase
from fliq.types import Predicate


class Carrier(QueryableBase):
    def __init__(self, iterable: Iterable):
        super().__init__(iterable)
        self._carries = []

    def where(self, predicate: Optional[Predicate]) -> 'Carrier':
        if predicate is None:
            # supported to ease syntax in higher level carriers and collectors
            return self

        c = Carry(lambda iterable: filter(predicate, iterable))
        self._carries.append(c)
        return self

    def select(self, selector: Callable[[Predicate], Any]) -> 'Carrier':
        c = Carry(lambda iterable: map(selector, iterable))
        self._carries.append(c)
        return self
