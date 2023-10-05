from typing import Iterable, Optional, Any, Sized, List

from fliq.carrier import Carrier
from fliq.exceptions import NoItemsFoundException, MultipleItemsFoundException
from fliq.types import Predicate


class Collector(Carrier):
    def __init__(self, iterable: Iterable):
        super().__init__(iterable)

    def all(self) -> Iterable:
        items = self._items
        while self._carries:
            c = self._carries.pop(0)
            items = c(items)
        return (i for i in items)

    def get(self, predicate: Optional[Predicate] = None) -> Any:
        self.where(predicate)
        count = self.count()
        if count == 0:
            raise NoItemsFoundException()
        elif count > 1:
            raise MultipleItemsFoundException()
        return self.first()

    def first(self, predicate: Optional[Predicate] = None) -> Any:
        """
        Collector.
        Returns the first item in the iterable that satisfies the predicate (if provided).
        This assumes at least one item exists in the iterable.
        If no items exist, a NoItemsFoundException is raised.
        :param predicate: Optional. The predicate to filter the iterable by.
        """
        self.where(predicate)
        try:
            return next(iter(self.all()))
        except StopIteration:
            raise NoItemsFoundException()

    def first_or_default(self,
                         predicate: Optional[Predicate] = None,
                         default: Any = None) -> Any:
        """
        Collector.
        Returns the first item in the iterable that satisfies the predicate (if provided).
        If no items exist, the default value is returned (None, if not provided).
        :param predicate: Optional. The predicate to filter the iterable by.
        :param default: Optional. The default value to return if no items are found.
        """
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

    def to_list(self) -> List:
        return list(self.all())
