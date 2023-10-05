from typing import Callable, Any, Iterable, Optional, List, Union, TYPE_CHECKING

if TYPE_CHECKING:  # pragma: no cover
    from fliq.query import Query

from fliq.query_base import QueryBase

from fliq.types import Predicate


class Carrier(QueryBase):
    def __init__(self, iterable: Iterable):
        super().__init__(iterable)
        self._carries: List = []

    def where(self, predicate: Optional[Predicate] = None) -> Union['Query', 'Carrier']:
        if predicate is None:
            # supported to ease syntax in higher level carriers and collectors
            return self

        c = lambda iterable: filter(predicate, iterable)
        self._carries.append(c)
        return self

    def select(self, selector: Callable[[Any], Any]) -> Union['Query', 'Carrier']:
        c = lambda iterable: map(selector, iterable)
        self._carries.append(c)
        return self
