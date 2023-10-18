import collections.abc
from itertools import islice
from typing import Iterable, List, Optional, Any, Sized, Iterator, Callable, TYPE_CHECKING

from fliq.exceptions import NoItemsFoundException, MultipleItemsFoundException
from fliq.types import Predicate

if TYPE_CHECKING:
    from fliq import q  # noqa: F401 (used in docs)  # pragma: no cover


class Query(collections.abc.Iterable):
    def __init__(self, iterable: Iterable):
        """
        Create a Query object to allow fluent iterable processing
        """
        self._items = iterable
        self._iterator: Optional[Iterator] = None

        # described the operation distance from the last snapshot.
        # -1 means there was no snapshot
        # 0 means the last operation was a snapshot
        # 1 means the previous operation was a snapshot
        # ...
        self._cow_pending: bool = False
    def __iter__(self):
        if self._iterator is None:
            self._iterator = iter(self._items)
        return self

    def __next__(self):
        if self._iterator is None:
            self._iterator = iter(self._items)
        return next(self._iterator)

    def _self(self, updated_items: Optional[Iterable] = None, in_snap: bool = False) -> 'Query':
        """
        Adjusts the iterable of the query, and returns the query itself.
        This method abstract the need to create a new Query in some situations, to support
        the snapshot functionality.
        """
        updated_items = self._items if updated_items is None else updated_items

        if in_snap:
            # COW prep: coming from snap, transform to list, don't copy object
            # This will allow multiple passes on this snapshot
            self._items = list(updated_items)
            return self
        elif self._cow_pending:
            # COW mode: coming from operation in COW mode, copy object
            # This will create a new query object in the first streamer following a snapshot
            # Following streamers will work on that same query object, minimizing object creations
            snapped_query = Query(iterable=updated_items)
            return snapped_query
        else:
            # non-COW mode: coming from operation in non-COW mode, update iterable
            self._items = updated_items
            return self

    def __repr__(self) -> str:  # pragma: no cover
        return f"Query({repr(self._items)}, cow_pending={self._cow_pending})"

    def snap(self) -> 'Query':
        """
        Snap is a unique streamer.
        Yields the same elements, and creates a snapshot for the query.
        This snapshot allows for multiple iterations over the same elements,
        as they were at the point of the snapshot.
        If multiple snapshots are created in a query lifetime, the last one is considered.

        Assumes a finite iterable.

        Example:
            <br />
            `evens = q(range(10)).where(lambda x: x % 2 == 0).cache()`
            <br />
            `count = evens.count()  # 5`
            <br />
            `first_even = evens.first()  # 0`
            <br />
            `even_pows = evens.select(lambda x: x ** 2)  # [0, 4, 16, 36, 64]`
        """
        self._cow_pending = True
        return self._self(in_snap=True)

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
            return self._self()

        items = filter(predicate, self._items)
        return self._self(items)

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
        items = map(selector, self._items)
        return self._self(items)

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
        items = filter(lambda x: not predicate(x), self._items)
        return self._self(items)

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
        if preserve_order:
            seen = set()

            def generator(internal_items: Iterable):
                for item in internal_items:
                    if item not in seen:
                        seen.add(item)
                        yield item

            items = generator(self._items)
        else:
            items = set(self._items)

        return self._self(items)

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
            items = sorted(self._items, reverse=not ascending)
        else:
            items = sorted(self._items, key=by, reverse=not ascending)
        return self._self(items)

    def reverse(self) -> 'Query':
        """
        Yields elements in reverse order.
        Notes:
         - in case of an irreversible iterable, TypeError is raised (e.g., set)
         - in case of a generator, the iterable is first converted to a list, then reversed,
         this has a performance and memory impact, and assumes a finite generator

         Example:
            <br />
            `q([0, 1, 2, 3, 4]).order()`
            <br />
            `[4, 3, 2, 1, 0]`

        Raises:
            TypeError: In case the iterable is irreversible.
        """
        if isinstance(self._items, collections.abc.Generator):
            items = reversed(list(self._items))
        else:
            items = reversed(self._items)  # type: ignore
        return self._self(items)

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
        items = islice(self._items, start, stop, step)
        return self._self(items)

    def take(self, n: int, predicate: Optional[Predicate] = None) -> 'Query':
        """
        Yields up to n items that satisfies the predicate (if provided).
        In case the iterable is ordered, the first n items are returned.
        Args:
            <br />
            n: Optional. The number of items to take. Defaults to 1.
            <br />
            predicate: Optional. The predicate to filter the iterable by.
        """
        query = self.where(predicate)
        query = query.slice(stop=n)
        return query

    # endregion

    # region Collectors

    def first(self, predicate: Optional[Predicate] = None) -> Any:
        query = self.where(predicate)
        try:
            return next(query)
        except StopIteration:
            raise NoItemsFoundException()

    def first_or_default(self, predicate: Optional[Predicate] = None, default: Any = None) -> Any:
        query = self.where(predicate)
        try:
            return next(query)
        except StopIteration:
            return default

    def single(self, predicate: Optional[Predicate] = None) -> Any:
        query = self.where(predicate)
        try:
            first = next(query)
        except StopIteration:
            raise NoItemsFoundException()

        try:
            second = next(query)
        except StopIteration:
            return first

        raise MultipleItemsFoundException(f"Found at least two items: {first}, {second}")

    def single_or_default(self, predicate: Optional[Predicate] = None, default: Any = None) -> Any:
        query = self.where(predicate)
        try:
            first = next(query)
        except StopIteration:
            return default

        try:
            next(query)
        except StopIteration:
            return first

        raise MultipleItemsFoundException()

    def count(self) -> int:
        """
        Returns the number of elements in the iterable
        :return: The number of the elements in the iterable
        :rtype: int
        """
        # If the iterable is sized, return the length
        if isinstance(self._items, Sized):
            return len(self._items)

        # Otherwise, iterate over the iterable
        return sum(1 for _ in self._items)

    def any(self, predicate: Optional[Predicate] = None) -> bool:
        """
        Returns whether any element in the iterable evaluates to true.
        If a predicate is provided, only elements that satisfy the predicate are considered.
        Args:
            predicate: Optional. The predicate to filter the iterable by.

        Returns:
            True if any element evaluates to true, False otherwise.
        """
        query = self.where(predicate)
        return any(query._items)

    def all(self, predicate: Optional[Predicate] = None) -> bool:
        """
        Returns whether all elements in the iterable evaluate to true.
        If a predicate is provided, only elements that satisfy the predicate are considered.
        Args:
            predicate: Optional. The predicate to filter the iterable by.

        Returns:
            True if all elements evaluate to true, False otherwise.
        """
        query = self.where(predicate)
        return all(query._items)

    def to_list(self) -> List:
        return list(self)

    # endregion
