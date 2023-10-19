import collections.abc
from functools import reduce
from itertools import islice, chain
from typing import Iterable, List, Optional, Any, Sized, Iterator, Callable, TYPE_CHECKING

from fliq.exceptions import NoItemsFoundException, MultipleItemsFoundException
from fliq.types import Predicate, Selector, NumericSelector

if TYPE_CHECKING:
    from fliq import q  # noqa: F401 (used in docs)  # pragma: no cover


class Query(collections.abc.Iterable):
    """
    Query is an iterable processing fluent-based API.
    It is lazy, and supports infinite iterables where applicable.
    """
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

    def __contains__(self, item):
        return item in self._items

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
            predicate: Optional. The predicate to filter the query by. If None is
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
            predicate: The predicate to filter the query by.
        """
        items = filter(lambda x: not predicate(x), self._items)
        return self._self(items)

    def distinct(self, preserve_order: bool = True) -> 'Query':
        """
        Yields distinct elements, preserving order if specified.
        Distinct supports infinite iterables, when preserve_order is True.
        Note that elements must be hashable.

        Example:

            q([0, 1, 0, 2, 2]).distinct()
            >> [0, 1, 2]

        Args:
            <br />
            preserve_order: Optional. Whether to preserve the order of the elements.
             Defaults to True.
            If True, distinct supports infinite iterables.
            If order is not important and iterable is finite, set to False for better performance.

        Raises:
            <br />
            TypeError: In case one or more items in the query are not hashable.
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
         - in case of an irreversible query, TypeError is raised (e.g., set).
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
        Yields a slice of the query
        .
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
        Yields up to n items that satisfy the predicate (if provided).
        In case the query is ordered, the first n elements are returned.

        Args:
            <br />
            n: Optional. The number of elements to take. Defaults to 1.
            <br />
            predicate: Optional. The predicate to filter the query by.
        """
        query = self.where(predicate)
        query = query.slice(stop=n)
        return self._self(query._items)

    def skip(self, n: int = 1) -> 'Query':
        """
        Yields the elements after skipping the first n (as returned from the iterator).

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
        Yields tuples of the elements of the query with the input iterables.
        The zipping stops as soon as the smallest of the iterables and the query is exhausted.

        Example:

            q(range(5)).zip(range(5, 10), range(10, 15)
            >> [(0, 5, 10), (1, 6, 11), (2, 7, 12), (3, 8, 13), (4, 9, 14)]

        Args:
            <br />
            *iterables: One or more iterables to zip with the query.
        """
        items = zip(self._items, *iterables)
        return self._self(items)

    def append(self, *single_items) -> 'Query':
        """
        Yields the elements of the query, followed by the input element(s).
        API also supports multiple arguments, where each is considered as a single element.

        Infinite iterables are supported, behaving as expected.

        Examples:

            q(range(5)).append(5)
            >> [0, 1, 2, 3, 4, 5]

            q(range(5)).append(5, 6, 7)
            >> [0, 1, 2, 3, 4, 5, 6, 7]

        Args:
            <br />
            *single_items: One or more elements to add to the end of the query.
        """
        items = chain(self._items, single_items)
        return self._self(items)

    def append_many(self, items: Iterable) -> 'Query':
        """
        Yields the elements of the iterable, followed by the elements given.

        Infinite iterables are supported, behaving as expected.

        Examples:

            q(range(5)).append_many([5, 6, 7])
            >> [0, 1, 2, 3, 4, 5, 6, 7]

        Args:
            <br />
            items: An iterable to concatenate to the end of the query.

        Raises:
            <br />
            TypeError: In case the elements are not iterable.
            Error will be raised when query is collected.
        """
        items = chain(self._items, items)
        return self._self(items)

    def prepend(self, *single_items) -> 'Query':
        """
        Yields the element(s) given, followed by the elements of the query.
        API also supports multiple arguments, where each is considered as a single element.

        Infinite iterables are supported, behaving as expected.

        Examples:

            q(range(5)).prepend(5)
            >> [5, 0, 1, 2, 3, 4]

            q(range(5)).prepend(5, 6, 7)
            >> [5, 6, 7, 0, 1, 2, 3, 4]

        Args:
            <br />
            *single_items: One or more elements to add to the start of the query.
        """
        items = chain(single_items, self._items)
        return self._self(items)

    def prepend_many(self, items) -> 'Query':
        """
        Yields the elements given, followed by the elements of the query.

        Infinite iterables are supported, behaving as expected.

        Examples:

            q(range(5)).prepend_many([5, 6, 7])
            >> [5, 6, 7, 0, 1, 2, 3, 4]

        Args:
            <br />
            items: The elements to add to the start of the query.

        Raises:
            <br />
            TypeError: In case the items are not iterable.
            Error will be raised when the query is collected.
        """
        items = chain(items, self._items)
        return self._self(items)

    # endregion

    # region Collectors

    def first(self, predicate: Optional[Predicate] = None) -> Any:
        """
        Returns the first element in the query.

        Example:

            q([1, 2, 3]).first()
            >> 1

            q([]).first()
            >> NoItemsFoundException

        Args:
            <br />
            predicate: Optional. The predicate to filter the query by.

        Raises:
            <br />
            NoItemsFoundException: In case the query is empty.
        """
        query = self.where(predicate)
        try:
            return next(query)
        except StopIteration:
            raise NoItemsFoundException()

    def first_or_default(self, predicate: Optional[Predicate] = None, default: Any = None) -> Any:
        """
        Returns the first element in the query, or a default value if the query is empty.

        Example:

            q([1, 2, 3]).first_or_default()
            >> 1

            q([]).first_or_default()
            >> None

        Args:
            <br />
            predicate: Optional. The predicate to filter the query by.
            <br />
            default: Optional. The default value to return in case the query is empty.
            Defaults to None.
        """
        query = self.where(predicate)
        try:
            return next(query)
        except StopIteration:
            return default

    def single(self, predicate: Optional[Predicate] = None) -> Any:
        """
        Returns the single element in the query.

        Example:

            q([1]).single()
            >> 1

            q([]).single()
            >> NoItemsFoundException

        Args:
            <br />
            predicate: Optional. The predicate to filter the query by.

        Raises:
            <br />
            NoItemsFoundException: In case the query is empty.
            <br />
            MultipleItemsFoundException: In case the query has more than one element.
        """
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
        """
        Returns the single element in the query, or a default value if the query is empty.

        Args:
            <br />
            predicate: Optional. The predicate to filter the query by.
            <br />
            default: Optional. The default value to return in case the query is empty.
            Defaults to None.

        Example:

            q([1]).single_or_default()
            >> 1

            q([]).single_or_default()
            >> None

            q([1, 2, 3]).single_or_default()
            >> MultipleItemsFoundException

        Raises:
            <br />
            MultipleItemsFoundException: In case the query has more than one element.
        """
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
        Returns the number of elements in the query.

        Example:

            q([1, 2, 3]).count()
            >> 3

        """
        # If the iterable is sized, return the length
        if isinstance(self._items, Sized):
            return len(self._items)

        # Otherwise, iterate over the iterable
        return sum(1 for _ in self)

    def any(self, predicate: Optional[Predicate] = None) -> bool:
        """
        Returns whether any element in the query evaluates to true.
        If a predicate is provided, only elements that satisfy the predicate are considered.

        For custom types, consider providing a predicate or
          implementing `__bool__` or `__len__` to support this method.
         see https://docs.python.org/3/reference/datamodel.html#object.__bool__ .

        Example:

            q([True, False, False]).any()
            >> True

            q([False, False, False]).any()
            >> False

        Args:
            <br />
            predicate: Optional. The predicate to filter the iterable by.
        """
        query = self.where(predicate)
        return any(query)

    def all(self, predicate: Optional[Predicate] = None) -> bool:
        """
        Returns whether all elements in the query evaluate to true.
        If a predicate is provided, only elements that satisfy the predicate are considered.

        For custom types, consider providing a predicate or
          implementing `__bool__` or `__len__` to support this method.
         see https://docs.python.org/3/reference/datamodel.html#object.__bool__ .

        Example:

            q([True, True, True]).all()
            >> True

            q([True, False, True]).all()
            >> False

        Args:
            predicate: Optional. The predicate to filter the query by.
        """
        query = self.where(predicate)
        return all(query)

    def aggregate(self, by: Callable[[Any, Any], Any], initial: Any = None):
        """
        Applies an accumulator function over the query.

        For an optimized summation of numeric values, use `sum`.

        Example:

            q([Point(0, 0), Point(1, 1), Point(2, 2)]).aggregate(by=lambda p1, p2: p1 + p2)
            >> Point(3, 3)

        Args:
            <br />
            by: The accumulator function to apply to each two elements.
            initial: Optional. The initial value of the accumulator. Defaults to None.
            If provided, it will also serve as the default value for an empty query.
            If not provided, the first element of the query will be used as the initial value.
        """
        if initial is not None:
            return reduce(by, self._items, initial)
        else:
            return reduce(by, self._items)

    def max(self, by: Optional[Selector] = None) -> Any:
        """
        Returns the maximal element in the query.
        If a selector is provided, the maximal selected attribute is returned.

        Custom types must provide a selector function or implement value comparisons
        (see https://docs.python.org/3/reference/expressions.html#value-comparisons).

        Example:

            q(range(5)).max()
            >> 4

            q(range(5)).max(by=lambda x: x*-1)
            >> 0

        Args:
            <br />
            by: Optional. The selector function to test for the maximal element.

        Raises:
            <br />
            ValueError: In case the query is empty.
        """
        if by is None:
            return max(self)
        else:
            return max(self, key=by)

    def min(self, by: Optional[Selector] = None) -> Any:
        """
        Returns the minimal element in the query.
        If a selector is provided, the minimal selected attribute is returned.

        Custom types must provide a selector function or implement value comparisons
        (see https://docs.python.org/3/reference/expressions.html#value-comparisons).

        Example:

            q(range(5)).min()
            >> 0

            q(range(5)).min(by=lambda x: x*-1)
            >> 4

        Args:
            <br />
            by: Optional. The selector function to test for the minimal element.

        Raises:
            <br />
            ValueError: In case the query is empty.
        """
        if by is None:
            return min(self)
        else:
            return min(self, key=by)

    def contains(self, item: Any) -> bool:
        """
        Returns whether the query contains the given item (by equality, not identity).
        Query also support the `in` and `not in` operators.

        Example:

            q([1, 2, 3]).contains(2)
            >> True

            q([1, 2, 3]).contains(4)
            >> False

            2 in q([1, 2, 3])
            >> False

        Args:
            <br />
            item: The item to test for.
        """
        return item in self._items

    # region Numeric Collectors

    def sum(self, by: Optional[NumericSelector] = None, accumulator: Any = 0) -> Any:
        """
        Returns the sum of the elements in the query.
        If a selector is provided, the sum of the selected elements is returned.
        If an accumulator is provided, it is used as the initial value for the summation.

        Custom types must provide a selector function or implement `__add__`
        and optionally `__radd__`
        (see https://docs.python.org/3/reference/datamodel.html#emulating-numeric-types).

        Use this method for optimized summation of numeric values, for other types of aggregation,
         use aggregate.

        Example:

            q(range(5)).sum()
            >> 10

            q(range(5)).sum(by=lambda x: x*2)
            >> 20

        Args:
            <br />
            by: Optional. The selector function to apply to each element.
            accumulator: Optional. The initial value of the sum. Defaults to 0.

        Returns:
            The sum of the elements in the iterable.
        """
        query = self
        if by is not None:
            query = self.select(by)
        return sum(query, start=accumulator)

    # endregion

    def to_list(self) -> List:
        """
        Returns the elements of the query as a list.
        """
        return list(self)

    # endregion
