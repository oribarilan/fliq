import collections.abc
import typing
from itertools import islice
from typing import Iterable, List, Optional, Any, Sized, Iterator, Callable

from fliq.exceptions import NoItemsFoundException, MultipleItemsFoundException
from fliq.types import Predicate

if typing.TYPE_CHECKING:
    from fliq import q  # noqa: F401 (used in docs)  # pragma: no cover


class Query(collections.abc.Iterable):
    def __init__(self, iterable: Iterable):
        """
        Create a Query object to allow fluent iterable processing
        """
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

    # region Streamers

    def where(self, predicate: Optional[Predicate] = None) -> 'Query':
        """
        Yields elements that satisfy the predicate (aka filter).

        Example:
            <br />
            `q(range(10)).where(lambda x: x % 2 == 0)`
            <br />
            `[0, 2, 4, 6, 8]`

        Args:
            <br />
            predicate: Optional. The predicate to filter the iterable by. If None is
            given, no filtering takes place.
        """
        if predicate is None:
            # supported to ease syntax in higher level streamers and collectors
            return self

        self._items = filter(predicate, self._items)
        return self

    def select(self, selector: Callable[[Any], Any]) -> 'Query':
        """
        Yields the result of applying the selector function to each element (aka map).

        Example:
            <br />
            `q(range(5)).select(lambda x: x * 2 == 0)`
            <br />
            `[0, 2, 4, 6, 8, 10]`

        Args:
            <br />
            selector: The selector function to apply to each element.
        """
        self._items = map(selector, self._items)
        return self

    def exclude(self, predicate: Predicate) -> 'Query':
        """
        Yields elements that do not satisfy the predicate.

        Example:
            <br />
            `q(range(5)).exclude(lambda x: x > 3)`
            <br />
            `[0, 1, 2, 3]`

        Args:
            <br />
            predicate: The predicate to filter the iterable by.
        """
        self._items = filter(lambda x: not predicate(x), self._items)
        return self

    def distinct(self, preserve_order: bool = True) -> 'Query':
        """
        Yields distinct elements, preserving order if specified.

        Example:
            <br />
            `q([0, 1, 0, 2, 2]).distinct()`
            <br />
            `[0, 1, 2]`

        Args:
            <br />
            preserve_order: Optional. Whether to preserve the order of the items. Defaults to True.
        """
        self._items = dict.fromkeys(self._items).keys() if preserve_order else set(self._items)
        return self

    def order(self,
              by: Optional[Callable[[Any], Any]] = None,
              ascending: bool = True) -> 'Query':
        """Yields elements in sorted order.

        Example:
            <br />
            `q([4, 3, 2, 1, 0]).order()`
            <br />
            `[0, 1, 2, 3, 4]`

        Args:
            <br />
            by: a selector function to extract the key from an item, defaults to None.
            If None, the default ordering is used.
            <br />
            ascending: whether to sort in ascending or descending order, defaults to True.
        """
        if by is None:
            # natural order
            self._items = sorted(self._items, reverse=not ascending)
        else:
            self._items = sorted(self._items, key=by, reverse=not ascending)
        return self

    def reverse(self) -> 'Query':
        """
        Yields elements in reverse order.
        Notes:
         - in case of an irreversible iterable, TypeError is raised (e.g., set)
         - in case of a generator, the iterable is first converted to a list, then reversed,
         this has a performance impact, and assume a finite generator

         Example:
            <br />
            `q([0, 1, 2, 3, 4]).order()`
            <br />
            `[4, 3, 2, 1, 0]`
        """
        if isinstance(self._items, collections.abc.Generator):
            self._items = reversed(list(self._items))
        else:
            self._items = reversed(self._items)  # type: ignore
        return self

    def slice(self, start: int = 0, stop: Optional[int] = None, step: int = 1) -> 'Query':
        """
        Yields a slice of the iterable.
        Examples:
            <br />
            `q(range(10)).slice(start=1, stop=6, step=2)`
            <br />
            `[1, 3, 5]`

        Args:
            <br />
            start: Optional. The start index of the slice. Defaults to 0.
            <br />
            stop: Optional. The stop index of the slice. Defaults to None.
            <br />
            step: Optional. The step of the slice. Defaults to 1.
        """
        self._items = islice(self._items, start, stop, step)
        return self

    # endregion

    # region Collectors

    def single(self, predicate: Optional[Predicate] = None) -> Any:
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

    def single_or_default(self, predicate: Optional[Predicate] = None, default: Any = None) -> Any:
        self.where(predicate)
        try:
            first = next(self)
        except StopIteration:
            return default

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
        """
        Returns the number of elements in the iterable
        :return: The number of the elemtns
        :rtype: int
        """
        # If the iterable is sized, return the length
        if isinstance(self._items, Sized):
            return len(self._items)

        # Otherwise, iterate over the iterable
        return sum(1 for _ in self._items)

    def to_list(self) -> List:
        return list(self)

    # endregion
