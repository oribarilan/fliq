from __future__ import annotations  # For Python 3.7+

from collections.abc import Sized
from typing import Callable, Iterable, Any, List, Optional
from typing import TypeVar, Generic

from fliq.channel import Channel
from fliq.exceptions import NoItemsFoundException, MultipleItemsFoundException

T = TypeVar('T')


class Query(Generic[T]):
    def __init__(self, iterable: Iterable[T]):
        self._items = iterable
        self._channels = []

    def where(self, predicate: Callable[[T], bool]) -> Query[T]:
        c = Channel(lambda iterable: filter(predicate, iterable))
        self._channels.append(c)
        return self

    def select(self, selector: Callable[[T], Any]) -> Query[Any]:
        c = Channel(lambda iterable: map(selector, iterable))
        self._channels.append(c)
        return self

    def all(self) -> Iterable[T]:
        items = self._items
        while self._channels:
            c = self._channels.pop(0)
            items = c(items)
        return (i for i in items)

    def get(self, predicate: Optional[Callable[[T], bool]] = None) -> Any:
        self.where(predicate)
        count = self.count()
        if count == 0:
            raise NoItemsFoundException()
        elif count > 1:
            raise MultipleItemsFoundException()
        return self.first()

    def first(self, predicate: Optional[Callable[[T], bool]] = None) -> Any:
        self.where(predicate)
        try:
            return next(iter(self.all()))
        except StopIteration:
            raise NoItemsFoundException()

    def first_or_default(self, predicate: Optional[Callable[[T], bool]] = None, default: Any = None) -> Any:
        try:
            return self.first(predicate)
        except NoItemsFoundException:
            return default

    def count(self) -> int:
        iterable = self.all()

        # If the iterable is sized, return the length
        if isinstance(iterable, Sized):
            return len(iterable)

        # Otherwise, iterate over the iterable
        return sum(1 for _ in iterable)

    def to_list(self) -> List[T]:
        return list(self.all())
