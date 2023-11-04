from __future__ import annotations

import collections.abc
import heapq
import random
from collections import defaultdict
from functools import reduce
from itertools import islice, chain, zip_longest
from operator import attrgetter
from typing import Iterable, List, Optional, Any, Sized, Iterator, Callable, TYPE_CHECKING, Dict, \
    Union, Tuple, Hashable

from fliq.exceptions import NoItemsFoundException, MultipleItemsFoundException
from fliq.types import Predicate, Selector, NumericSelector, IndexSelector

if TYPE_CHECKING:
    from fliq import q  # noqa: F401 (used in docs)  # pragma: no cover


class Query(collections.abc.Iterable):
    def __init__(self, iterable: Iterable):
        """
        Create a Query object to allow fluent iterable processing
        """
        self._items = iterable
        self._iterator: Optional[Iterator] = None

        # COW mode: copy-on-write mode, used to support snapshots
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

    def __eq__(self, other: Any) -> bool:
        """
        Compares the query to another iterable.

        Args:
            other: The iterable to compare to. Does not have to be a Query object.

        Returns:
            True if the query is equal to another iterable, item by item, ordered, False otherwise.
        """
        if not isinstance(other, Iterable):
            return False

        sentinel = object()  # To identify iterables of different sizes
        for a, b in zip_longest(self._items, other, fillvalue=sentinel):
            if a != b:
                # If two real objects returned unequal, return False
                # If one of the objects is the sentinel, iterables are of unequal size, return False
                return False

        return True

    def _self(self, updated_items: Optional[Iterable] = None, in_snap: bool = False) -> Query:
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

    # region Special Functionality

    def snap(self) -> Query:
        """
        Yields the same elements, and creates a snapshot for the query.
        This snapshot allows for multiple iterations over the same "snapped" iterable.
        If multiple snapshots are created in a query lifetime, the last one is considered.

        Assumes a finite iterable.

        Examples:
            >>> from fliq import q
            >>> evens = q(range(10)).where(lambda x: x % 2 == 0).snap()
            >>> evens.where(lambda x: x > 3).count()
            3
            >>> evens.first()
            0
            >>> evens.select(lambda x: x ** 2).to_list()
            [0, 4, 16, 36, 64]
        """
        self._cow_pending = True
        return self._self(in_snap=True)

    def partition(self, by: Union[IndexSelector, Predicate], n: int = 2) -> Tuple[Query, ...]:
        # noinspection GrazieInspection
        """
        Yields n queries, each containing the elements that match the partition index selected.
        Supports infinite iterables,
        conditioned that there are finite sequences between elements of different partitions.

        Examples:
            >>> from fliq import q
            >>> first, second, third = q(range(10)).partition(lambda x: x % 3, n=3)
            >>> first.to_list(), second.to_list(), third.to_list()
            ([0, 3, 6, 9], [1, 4, 7], [2, 5, 8])
            >>> even, odd = q([1, 2, 3]).partition(lambda x: x % 2 == 0)
            >>> even.to_list(), odd.to_list()
            ([1, 3], [2])


        Args:
            by: IndexSelector that returns partition index for each element, in the range [0, n).
                Or, a Predicate to be used for a binary partition (when n=2).
                In case of a Selector, the first query will contain the elements in partition 0,
                the second query will contain the elements in partition 1, and so on.
                In case of a Predicate, the first query will contain the elements that don't satisfy
                 the predicate (for alignment between 0 and False as the first index).
            n: Optional. The number of partitions to create. Defaults to 2. Must be positive.
                When n=2, `by` can also be a Predicate.

        Raises:
            ValueError: In case the partition index is outside the range [0, n).
            TypeError: In case the partition index is not an integer.
        """
        if n <= 0:
            raise ValueError("Number of partitions must be positive")

        partition_queues: Dict[int, list] = {i: [] for i in range(n)}

        def partition_generator(queue_partition_idx: int):
            for item in self:
                item_partition_idx: int = by(item)
                self._validate_partition_index(item_partition_idx, n)
                partition_queues[int(item_partition_idx)].append(item)
                if len(partition_queues[queue_partition_idx]) != 0:
                    # item found, stop generating and yield
                    yield partition_queues[queue_partition_idx].pop(0)

            # Iterator exhausted, drain the rest of the partition queue
            while len(partition_queues[queue_partition_idx]) != 0:
                yield partition_queues[queue_partition_idx].pop(0)

        # Create n Queries, each with its own partition generator
        return tuple(Query(partition_generator(i)) for i in range(n))

    # endregion

    # region Mappers

    def where(self, predicate: Optional[Predicate] = None) -> Query:
        """
        Yields elements that satisfy the predicate (aka filter).

        Examples:
            >>> from fliq import q
            >>> q(range(10)).where(lambda x: x % 2 == 0).to_list()
            [0, 2, 4, 6, 8]

        Args:
            predicate: Optional. The predicate to filter the query by. If None is
                given, no filtering takes place.
        """
        if predicate is None:
            # supported to ease syntax in higher level streamers and collectors
            return self._self()

        items = filter(predicate, self._items)
        return self._self(items)

    def select(self, selector: Selector) -> Query:
        """
        Yields the result of applying the selector function to each element (aka map).

        Examples:
            >>> from fliq import q
            >>> q(range(5)).select(lambda x: x * 2).to_list()
            [0, 2, 4, 6, 8]

        Args:
            selector: The selector function to apply to each element.
        """
        items = map(selector, self._items)
        return self._self(items)

    def exclude(self, predicate: Predicate) -> Query:
        """
        Yields elements that do not satisfy the predicate.

        Examples:
            >>> from fliq import q
            >>> q(range(5)).exclude(lambda x: x > 3).to_list()
            [0, 1, 2, 3]

        Args:
            predicate: The predicate to filter the query by.
        """
        items = filter(lambda x: not predicate(x), self._items)
        return self._self(items)

    def distinct(self, preserve_order: bool = True) -> Query:
        """
        Yields distinct elements.
        Distinct supports infinite iterables.
        Note that elements must be hashable.

        Examples:
            >>> from fliq import q
            >>> q([0, 1, 0, 2, 2]).distinct().to_list()
            [0, 1, 2]

        Raises:
            TypeError: In case one or more items in the query are not hashable.
            """

        def generator(internal_items: Iterable):
            seen = set()
            for item in internal_items:
                if item not in seen:
                    seen.add(item)
                    yield item

        items = generator(self._items)

        return self._self(items)

    def order(self,
              by: Optional[Selector] = None,
              ascending: bool = True) -> Query:
        """Yields elements in sorted order.

        Examples:
            >>> from fliq import q
            >>> q([4, 3, 2, 1, 0]).order().to_list()
            [0, 1, 2, 3, 4]

        Args:
            by: a selector function to extract the key from an item, defaults to None.
                If None, the default ordering is used.
            ascending: whether to sort in ascending or descending order, defaults to True.
        """
        if by is None:
            # natural order
            items = sorted(self._items, reverse=not ascending)
        else:
            items = sorted(self._items, key=by, reverse=not ascending)
        return self._self(items)

    def shuffle(self,
                buffer_size: int = 10,
                seed: Optional[Hashable] = None,
                fair: bool = False) -> Query:
        """
        Yields elements in a random order.
        Supports infinite iterables.

        Args:
            buffer_size (int): The size of the shuffle buffer for an unfair shuffle. Defaults to 10.
                The bigger the buffer, the more memory is required,
                but the shuffle is closer to fair.
            seed: Optional. The seed to use for the random shuffle. Defaults to None.
            fair (bool): Whether to use a fair shuffle. Defaults to False.
                If True, each permutation of the elements will be equally likely.
                    This option does not support infinite iterables
                    (specifically, requires a sizeable iterable). This requires materialization
                    of the iterable, which is more memory intensive.
                    Use this for scenarios where fairness is important,
                    like rolling a die or shuffling a deck of cards.
                If False, each permutation of elements will NOT be equally likely.
                    However, this is more memory efficient, and supports infinite iterables.
                    The bigger the buffer size, the closer the shuffle will be to fair
                    (and thus, less memory efficient).
                    Use this for scenarios where perfect fairness is not important,
                    like shuffling a list of songs in a playlist.

        Examples:
            >>> from fliq import q
            >>> q(range(10)).shuffle(seed=42, buffer_size=5).to_list()
            [1, 5, 6, 3, 0, 8, 7, 2, 4, 9]
            >>> q(range(10)).shuffle(seed=42, fair=True).to_list()
            [7, 3, 2, 8, 5, 6, 9, 4, 0, 1]

        Raises:
            TypeError: In case a fair shuffle is requested for a non-sizeable iterable.
        """
        ran = random.Random(seed) if seed is not None else random.Random()

        if fair:
            if isinstance(self._items, List):
                shuffled_items = self._items
            elif isinstance(self._items, Sized):
                shuffled_items = list(self._items)
            else:
                raise TypeError("Fair shuffle is not supported for non-sizeable iterables")
            ran.shuffle(shuffled_items)
            return self._self(shuffled_items)

        def shuffled_generator(internal_items: Iterable):
            buffer = []
            sentinel = object()
            items_iter = iter(internal_items)

            # fill the buffer
            for _ in range(buffer_size):
                item = next(items_iter, sentinel)
                if item is sentinel:
                    # iterable exhausted (smaller than buffer size)
                    break
                buffer.append(item)

            ran.shuffle(buffer)

            # if buffer was not filled, it means the iterable was too short
            if len(buffer) < buffer_size:
                yield from buffer
                return

            for item in items_iter:
                # yield a random item from the buffer and replace it with the new item
                idx = ran.randrange(len(buffer))
                yield buffer[idx]
                buffer[idx] = item

            # yield the remaining items in the buffer
            yield from buffer

        items = shuffled_generator(self._items)

        return self._self(items)

    def reverse(self) -> Query:
        """
        Yields elements in reverse order.
        Notes:
         - in case of an irreversible query, TypeError is raised (e.g., set).
         - in case of an iterator, it is first converted to a list, then reversed,
         this has a performance and memory impact, and assumes a finite iterator.

         Examples:
             >>> from fliq import q
            >>> q([0, 1, 2, 3, 4]).reverse().to_list()
            [4, 3, 2, 1, 0]

        Raises:
            TypeError: In case the iterable is irreversible.
        """
        if isinstance(self._items, collections.abc.Iterator):
            items = reversed(list(self._items))
        else:
            items = reversed(self._items)  # type: ignore
        return self._self(items)

    def slice(self, start: int = 0, stop: Optional[int] = None, step: int = 1) -> Query:
        """
        Yields a slice of the query

        Examples:
            >>> from fliq import q
            >>> q(range(10)).slice(start=1, stop=6, step=2).to_list()
            [1, 3, 5]

        Args:
            start: Optional. The start index of the slice. Defaults to 0.
            stop: Optional. The stop index of the slice. Defaults to None.
            step: Optional. The step of the slice. Defaults to 1.
        """
        items = islice(self._items, start, stop, step)
        return self._self(items)

    def take(self, n: int = 1, predicate: Optional[Predicate] = None) -> Query:
        """
        Yields up to n items that satisfy the predicate (if provided).
        In case the query is ordered, the first n elements are returned.

        Args:
            n: Optional. The number of elements to take. Defaults to 1.
            predicate: Optional. The predicate to filter the query by.
        """
        query = self.where(predicate).slice(stop=n)
        return self._self(query._items)

    def skip(self, n: int = 1) -> Query:
        """
        Yields the elements after skipping the first n (as returned from the iterator).

        Examples:
            >>> from fliq import q
            >>> q(range(10)).skip(n=5).to_list()
            [5, 6, 7, 8, 9]

        Args:
            n: Optional. The number of items to take. Defaults to 1.
        """
        query = self.slice(start=n)
        return self._self(query._items)

    def zip(self, *iterables: Iterable) -> Query:
        """
        Yields tuples of the elements of the query with the input iterables.
        The zipping stops as soon as the smallest of the iterables and the query is exhausted.

        Examples:
            >>> from fliq import q
            >>> q(range(5)).zip(range(5, 10), range(10, 15)).to_list()
            [(0, 5, 10), (1, 6, 11), (2, 7, 12), (3, 8, 13), (4, 9, 14)]

        Args:
            *iterables: One or more iterables to zip with the query.
        """
        items = zip(self._items, *iterables)
        return self._self(items)

    def append(self, *single_items: Any) -> Query:
        """
        Yields the elements of the query, followed by the input element(s).
        API also supports multiple arguments, where each is considered as a single element.

        Infinite iterables are supported, behaving as expected.

        Examples:
            >>> from fliq import q
            >>> q(range(5)).append(5).to_list()
            [0, 1, 2, 3, 4, 5]
            >>> q(range(5)).append(5, 6, 7).to_list()
            [0, 1, 2, 3, 4, 5, 6, 7]

        Args:
            *single_items: One or more elements to add to the end of the query.
        """
        items = chain(self._items, single_items)
        return self._self(items)

    def append_many(self, items: Iterable) -> Query:
        """
        Yields the elements of the iterable, followed by the elements given.

        Infinite iterables are supported, behaving as expected.

        Examples:
            >>> from fliq import q
            >>> q(range(5)).append_many([5, 6, 7]).to_list()
            [0, 1, 2, 3, 4, 5, 6, 7]

        Args:
            items: An iterable to concatenate to the end of the query.

        Raises:
            TypeError: In case the elements are not iterable.
                Error will be raised when query is collected.
        """
        items = chain(self._items, items)
        return self._self(items)

    def prepend(self, *single_items: Any) -> Query:
        """
        Yields the element(s) given, followed by the elements of the query.
        API also supports multiple arguments, where each is considered as a single element.

        Infinite iterables are supported, behaving as expected.

        Examples:
            >>> from fliq import q
            >>> q(range(5)).prepend(5).to_list()
            [5, 0, 1, 2, 3, 4]
            >>> q(range(5)).prepend(5, 6, 7).to_list()
            [5, 6, 7, 0, 1, 2, 3, 4]

        Args:
            *single_items: One or more elements to add to the start of the query.
        """
        items = chain(single_items, self._items)
        return self._self(items)

    def prepend_many(self, items: Iterable) -> Query:
        """
        Yields the elements given, followed by the elements of the query.

        Infinite iterables are supported, behaving as expected.

        Examples:
            >>> from fliq import q
            >>> q(range(5)).prepend_many([5, 6, 7]).to_list()
            [5, 6, 7, 0, 1, 2, 3, 4]

        Args:
            items: The elements to add to the start of the query.

        Raises:
            TypeError: In case the items are not iterable.
                Error will be raised when the query is collected.
        """
        items = chain(items, self._items)
        return self._self(items)

    def group_by(self, key: Union[str, Selector]) -> Query:
        """
        Yields an iterable of groups, where each group has identical key.

        Examples:
            >>> from fliq import q
            >>> q([1, 2, 3]).group_by(lambda x: x % 2 == 0).to_list()
            [[1, 3], [2]]

        Args:
            key: A function that takes an element and returns its grouping key,
                or a string representing the name of an attribute to group by.
        """
        groups = defaultdict(list)

        key_selector: Union[attrgetter, Callable[[Any], Any]]
        if callable(key):
            key_selector = key
        else:
            # key is a string
            key_selector = attrgetter(key)

        for item in self._items:
            key = key_selector(item)
            groups[key].append(item)

        return self._self(groups.values())

    def top(self, n: int = 1, by: Optional[NumericSelector] = None) -> Query:
        """
        Yields the top n elements of the query, according to the selector (if provided).

        This is done in O(N log n) time, and O(n) space. Where n is the number of elements to take,
        and N is the number of elements in the query.

        Examples:
            >>> from fliq import q
            >>> q(range(10)).top(n=3).to_list()
            [9, 8, 7]
            >>> q(range(10)).top(n=3, by=lambda x: x*-1).to_list()
            [0, 1, 2]

        Args:
            n: Optional. The number of elements to take. Defaults to 1.
            by: Optional. The selector function to apply to each element. Defaults to the identity.
        """
        items: Iterable
        if n <= 0:
            return self._self([])

        heap: List = []
        for item in self._items:
            value = item if by is None else by(item)
            if len(heap) < n:
                heapq.heappush(heap, (value, item))
            else:
                heapq.heappushpop(heap, (value, item))

        items = (
            Query(heap)
            .order(ascending=False)
            .select(lambda heap_pair: heap_pair[1])
        )

        return self._self(items)

    def bottom(self, n: int = 1, by: Optional[NumericSelector] = None) -> Query:
        """
        Yields the top n elements of the query, according to the selector (if provided).

        This is done in O(N log n) time, and O(n) space. Where n is the number of elements to take,
        and N is the number of elements in the query.

        Examples:
            >>> from fliq import q
            >>> q(range(10)).bottom(n=3).to_list()
            [0, 1, 2]

        Args:
            n: Optional. The number of elements to take. Defaults to 1.
            by: Optional. The selector function to apply to each element. Defaults to the identity.
        """
        if by is None:
            return self.top(n=n, by=lambda x: -1 * x)
        else:
            return self.top(n=n, by=lambda x: -1 * by(x))  # type: ignore

    # endregion

    # region Materializers

    def first(self, predicate: Optional[Predicate] = None) -> Any:
        """
        Returns the first element in the query.

        Examples:
            >>> from fliq import q
            >>> q([1, 2, 3]).first()
            1
            >>> q([]).first()
            Traceback (most recent call last):
            ...
            fliq.exceptions.NoItemsFoundException

        Args:
            predicate: Optional. The predicate to filter the query by.

        Raises:
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

        Examples:
            >>> from fliq import q
            >>> q([1, 2, 3]).first_or_default()
            1
            >>> q([]).first_or_default() # returns None


        Args:
            predicate: Optional. The predicate to filter the query by.
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

        Examples:
            >>> from fliq import q
            >>> q([1]).single()
            1
            >>> q([]).single()
            Traceback (most recent call last):
            ...
            fliq.exceptions.NoItemsFoundException

        Args:
            predicate: Optional. The predicate to filter the query by.

        Raises:
            NoItemsFoundException: In case the query is empty.
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
            predicate: Optional. The predicate to filter the query by.
            default: Optional. The default value to return in case the query is empty.
                Defaults to None.

        Examples:
            >>> from fliq import q
            >>> q([1]).single_or_default()
            1
            >>> q([]).single_or_default() # returns None

            >>> q([1, 2, 3]).single_or_default()
            Traceback (most recent call last):
            ...
            fliq.exceptions.MultipleItemsFoundException

        Raises:
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

        Examples:
            >>> from fliq import q
            >>> q([1, 2, 3]).count()
            3
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

        Examples:
            >>> from fliq import q
            >>> q([True, False, False]).any()
            True
            >>> q([False, False, False]).any()
            False

        Args:
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

        Examples:
            >>> from fliq import q
            >>> q([True, True, True]).all()
            True
            >>> q([True, False, True]).all()
            False

        Args:
            predicate: Optional. The predicate to filter the query by.
        """
        query = self.where(predicate)
        return all(query)

    def aggregate(self, by: Callable[[Any, Any], Any], initial: Any = None):
        """
        Applies an accumulator function over the query.

        For an optimized summation of numeric values, use `sum`.

        Examples:
            >>> from fliq.tests.fliq_test_utils import Point
            >>> from fliq import q
            >>> q([Point(0, 0), Point(1, 1), Point(2, 2)]).aggregate(by=lambda p1, p2: p1 + p2)
            Point(x=3, y=3)

        Args:
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

        Examples:
            >>> from fliq import q
            >>> q(range(5)).max()
            4
            >>> q(range(5)).max(by=lambda x: x*-1)
            0

        Args:
            by: Optional. The selector function to test for the maximal element.

        Raises:
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

        Examples:
            >>> from fliq import q
            >>> q(range(5)).min()
            0
            >>> q(range(5)).min(by=lambda x: x*-1)
            4

        Args:
            by: Optional. The selector function to test for the minimal element.

        Raises:
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

        Examples:
            >>> from fliq import q
            >>> q([1, 2, 3]).contains(2)
            True
            >>> q([1, 2, 3]).contains(4)
            False
            >>> 2 in q([1, 2, 3])
            True

        Args:
            item: The item to test for.
        """
        return item in self._items

    def equals(self, other: Iterable, bag_compare: bool = False) -> bool:
        """
        Returns whether the query is equal to the given iterable.
        Query also supports the `==` and `!=` operators.

        Examples:
            >>> from fliq import q
            >>> q([1, 2, 3]).equals([1, 2, 3])
            True
            >>> q([1, 2, 3]).equals(q([1, 2]))
            False
            >>> q([1, 2, 3]).equals([3, 2, 1], bag_compare=True)
            True

        Args:
            other: The iterable to test for equality.
            bag_compare: Optional. If True, compares the query and the other iterable as bags,
                ignoring order and duplicate items. Defaults to False.
        """
        if bag_compare:
            return set(self) == set(other)
        else:
            return self == other

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

        Examples:
            >>> from fliq import q
            >>> q(range(5)).sum()
            10
            >>> q(range(5)).sum(by=lambda x: x*2)
            20

        Args:
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

    def to_dict(self, key: Union[str, Selector]) -> Dict[Any, List[Any]]:
        """
        Returns the elements of the query as a dictionary, grouped by the given key.

        Examples:
            >>> from fliq import q
            >>> q([1, 2, 3]).to_dict(key=lambda x: x % 2 == 0)
            {False: [1, 3], True: [2]}

        Args:
            key: The selector function to apply to each element, or a string representing
                the name of an attribute to group by.
        """
        groups = self.group_by(key)

        key_selector: Union[attrgetter, Callable[[Any], Any]]
        if callable(key):
            key_selector = key
        else:
            # key is a string
            key_selector = attrgetter(key)

        return {key_selector(group[0]): list(group) for group in groups}

    # endregion

    @staticmethod
    def _validate_partition_index(item_partition_idx, n) -> None:
        if isinstance(item_partition_idx, bool) and n != 2:
            raise TypeError(f"Partitioning by predicate is only supported for n=2, found n=`{n}`")
        if not (0 <= item_partition_idx < n):
            raise ValueError(f"Partition index {item_partition_idx} is not in range [0, {n})")
