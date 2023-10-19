import collections.abc
from functools import reduce
from itertools import islice, chain
from typing import Iterable, List, Optional, Any, Sized, Iterator, Callable, TYPE_CHECKING

from fliq.exceptions import NoItemsFoundException, MultipleItemsFoundException
from fliq.types import Predicate, Selector

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

            evens = q(range(10)).where(lambda x: x % 2 == 0).cache()
            count = evens.count()                       # <-- 5
            first_even = evens.first()                  # <-- 0
            even_pows = evens.select(lambda x: x ** 2)  # <-- [0, 4, 16, 36, 64]
        """
        self._cow_pending = True
        return self._self(in_snap=True)

    # region Streamers

    def where(self, predicate: Optional[Predicate] = None) -> 'Query':
        """
        Yields elements that satisfy the predicate (aka filter).

        Example:

            q(range(10)).where(lambda x: x % 2 == 0)
            >> [0, 2, 4, 6, 8]

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

    def select(self, selector: Selector) -> 'Query':
        """
        Yields the result of applying the selector function to each element (aka map).

        Example:

            q(range(5)).select(lambda x: x * 2 == 0)
            >> [0, 2, 4, 6, 8, 10]

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

            q(range(5)).exclude(lambda x: x > 3)
            >> [0, 1, 2, 3]

        Args:
            <br />
            predicate: The predicate to filter the iterable by.
        """
        items = filter(lambda x: not predicate(x), self._items)
        return self._self(items)

    def distinct(self, preserve_order: bool = True) -> 'Query':
        """
        Yields distinct elements, preserving order if specified.
        Distinct supports infinite iterables, when preserver_order is True.
        Note that the items must be hashable.

        Example:

            q([0, 1, 0, 2, 2]).distinct()
            >> [0, 1, 2]

        Args:
            <br />
            preserve_order: Optional. Whether to preserve the order of the items. Defaults to True.
            If True, distinct supports infinite iterables.
            If order is not important and iterable is finite, set to False for better performance.

        Raises:
            <br />
            TypeError: In case one or more items in the iterable are not hashable.
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
              by: Optional[Selector] = None,
              ascending: bool = True) -> 'Query':
        """Yields elements in sorted order.

        Example:

            q([4, 3, 2, 1, 0]).order()
            >> [0, 1, 2, 3, 4]

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
         - in case of an irreversible iterable, TypeError is raised (e.g., set).
         - in case of an iterator, it is first converted to a list, then reversed,
         this has a performance and memory impact, and assumes a finite iterator.

         Example:

            q([0, 1, 2, 3, 4]).order()
            >> [4, 3, 2, 1, 0]

        Raises:
            <br />
            TypeError: In case the iterable is irreversible.
        """
        if isinstance(self._items, collections.abc.Iterator):
            items = reversed(list(self._items))
        else:
            items = reversed(self._items)  # type: ignore
        return self._self(items)

    def slice(self, start: int = 0, stop: Optional[int] = None, step: int = 1) -> 'Query':
        """
        Yields a slice of the iterable.
        Example:

            q(range(10)).slice(start=1, stop=6, step=2)
            >> [1, 3, 5]

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

    def take(self, n: int = 1, predicate: Optional[Predicate] = None) -> 'Query':
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
        return self._self(query._items)

    def skip(self, n: int = 1) -> 'Query':
        """
        Yields the items after skipping the first n items (as returned from the iterator).

        Example:

            q(range(10)).skip(n=5)
            >> [5, 6, 7, 8, 9]

        Args:
            <br />
            n: Optional. The number of items to take. Defaults to 1.
        """
        query = self.slice(start=n)
        return self._self(query._items)

    def zip(self, *iterables: Iterable) -> 'Query':
        """
        Yields tuples of the items of the iterable with the input iterables.
        The iteration stops as soon as one of the input iterables is exhausted.

        Example:

            q(range(5)).zip(range(5, 10), range(10, 15)
            >> [(0, 5, 10), (1, 6, 11), (2, 7, 12), (3, 8, 13), (4, 9, 14)]

        Args:
            <br />
            *iterables: One or more iterables to zip with the iterable.
        """
        items = zip(self._items, *iterables)
        return self._self(items)

    def append(self, *single_items) -> 'Query':
        """
        Yields the items of the iterable, followed by the item(s) given.
        API also supports multiple arguments, where each is considered as a single item.

        Infinite iterables are supported, behaving as expected.

        Examples:

            q(range(5)).append(5)
            >> [0, 1, 2, 3, 4, 5]

            q(range(5)).append(5, 6, 7)
            >> [0, 1, 2, 3, 4, 5, 6, 7]

        Args:
            <br />
            *single_items: One or more items to add to the end of the iterable.
        """
        items = chain(self._items, single_items)
        return self._self(items)

    def append_many(self, items: Iterable) -> 'Query':
        """
        Yields the items of the iterable, followed by the items given.

        Infinite iterables are supported, behaving as expected.

        Examples:

            q(range(5)).append_many([5, 6, 7])
            >> [0, 1, 2, 3, 4, 5, 6, 7]

        Args:
            <br />
            items: The items to add to the end of the iterable.

        Raises:
            <br />
            TypeError: In case the items are not iterable.
            Error will be raised when item is consumed.
        """
        items = chain(self._items, items)
        return self._self(items)

    def prepend(self, *single_items) -> 'Query':
        """
        Yields the item(s) given, followed by the items of the iterable.
        API also supports multiple arguments, where each is considered as a single item.

        Infinite iterables are supported, behaving as expected.

        Examples:

            q(range(5)).prepend(5)
            >> [5, 0, 1, 2, 3, 4]

            q(range(5)).prepend(5, 6, 7)
            >> [5, 6, 7, 0, 1, 2, 3, 4]

        Args:
            <br />
            *single_items: One or more items to add to the start of the iterable.
        """
        items = chain(single_items, self._items)
        return self._self(items)

    def prepend_many(self, items) -> 'Query':
        """
        Yields the items given, followed by the items of the iterable.

        Infinite iterables are supported, behaving as expected.

        Examples:

            q(range(5)).prepend_many([5, 6, 7])
            >> [5, 6, 7, 0, 1, 2, 3, 4]

        Args:
            <br />
            items: The items to add to the start of the iterable.

        Raises:
            <br />
            TypeError: In case the items are not iterable.
            Error will be raised when item is consumed.
        """
        items = chain(items, self._items)
        return self._self(items)

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
        return sum(1 for _ in self)

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
        return any(query)

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
        return all(query)

    def aggregate(self, by: Callable[[Any, Any], Any], initial: Any = None):
        """
        Applies an accumulator function over the iterable.

        Args:
            <br />
            by: The accumulator function to apply to each two elements.
            initial: Optional. The initial value of the accumulator. Defaults to None.
            If provided, it will also serve as the default value for an empty iterable.
            If not provided, the first element of the iterable will be used as the initial value.
        """
        if initial is not None:
            return reduce(by, self._items, initial)
        else:
            return reduce(by, self._items)

    # def sum(self, by: Optional[Selector] = None, accumulator: Any = 0) -> Any:
    #     """
    #     Returns the sum of the elements in the iterable.
    #     If a selector is provided, the sum of the selected elements is returned.
    #     If an accumulator is provided, it is used as the initial value for the summation.
    #     For use with custom classes, the class must implement `__add__`.
    #
    #     Args:
    #         <br />
    #         by: Optional. The selector function to apply to each element.
    #         accumulator: Optional. The initial value of the sum. Defaults to 0.
    #
    #     Returns:
    #         The sum of the elements in the iterable.
    #     """
    #     query = self
    #     if by is None:
    #         query = self.select(lambda x: x)
    #     return sum(query, start=accumulator)

    def to_list(self) -> List:
        return list(self)

    # endregion
