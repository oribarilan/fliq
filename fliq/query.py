import collections.abc
from typing import Iterable, List, Optional, Any, Sized, Iterator, Callable

from fliq.exceptions import NoItemsFoundException, MultipleItemsFoundException
from fliq.types import Predicate


class Query(collections.abc.Iterable):
    def __init__(self, iterable: Iterable):
        self._items = iterable
        self._iterator: Optional[Iterator] = None

    def __iter__(self):
        if self._iterator is None:
            self._iterator = iter(self._items)
        return self

    def __next__(self):
        if self._iterator is None:
            self._iterator = iter(self._items)
        return next(self._iterator)

    # region Carriers

    def where(self, predicate: Optional[Predicate] = None) -> 'Query':
        if predicate is None:
            # supported to ease syntax in higher level carriers and collectors
            return self

        self._items = filter(predicate, self._items)
        return self

    def select(self, selector: Callable[[Any], Any]) -> 'Query':
        self._items = map(selector, self._items)
        return self

    def exclude(self, predicate: Predicate) -> 'Query':
        self._items = filter(lambda x: not predicate(x), self._items)
        return self

    def distinct(self, preserve_order: bool = True) -> 'Query':
        """
        Yields distinct elements, preserving order if specified.
        :param preserve_order: Optional. Whether to
            preserve the order of the items. Defaults to True.
        """
        self._items = dict.fromkeys(self._items).keys() if preserve_order else set(self._items)
        return self

    def order_by(self,
                 selector: Optional[Callable[[Any], Any]] = None,
                 ascending: bool = True) -> 'Query':
        """
        Yields sorted elements in an ascending or descending order,
            based on the selector or default ordering.
        :param selector: Optional. The selector to sort the iterable by.
            If not provided, default ordering is used.
        :param ascending: Optional. Whether to sort in ascending or
            descending order. Defaults to ascending.
        """
        if selector is None:
            # natural order
            self._items = sorted(self._items, reverse=not ascending)
        else:
            self._items = sorted(self._items, key=selector, reverse=not ascending)
        return self


    # endregion

    # region Collectors

    def get(self, predicate: Optional[Predicate] = None) -> Any:
        self.where(predicate)
        try:
            first = next(self)
        except StopIteration:
            raise NoItemsFoundException()

        try:
            next(self)
        except StopIteration:
            return first

        raise MultipleItemsFoundException()

    def first(self, predicate: Optional[Predicate] = None) -> Any:
        """
        Collector.
        Returns the first item that satisfies the predicate (if provided).
        This assumes at least one item exists in the query.
        If no items exist, a NoItemsFoundException is raised.
        :param predicate: Optional. The predicate to filter the iterable by.
        """
        self.where(predicate)
        try:
            return next(iter(self))
        except StopIteration:
            raise NoItemsFoundException()

    def first_or_default(self,
                         predicate: Optional[Predicate] = None,
                         default: Any = None) -> Any:
        """
        Collector.
        Returns the first item that satisfies the predicate (if provided).
        If no items exist, the default value is returned (None, if not provided).
        :param predicate: Optional. The predicate to filter the iterable by.
        :param default: Optional. The default value to return if no items are found.
        """
        try:
            return self.first(predicate)
        except NoItemsFoundException:
            return default

    def count(self) -> int:
        # If the iterable is sized, return the length
        if isinstance(self._items, Sized):
            return len(self._items)

        # Otherwise, iterate over the iterable
        return sum(1 for _ in self._items)

    def to_list(self) -> List:
        return list(self)

    # endregion