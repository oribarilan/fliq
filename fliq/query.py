from __future__ import annotations

import collections.abc
import heapq
import itertools
import random
from collections import defaultdict, deque, Counter
from functools import reduce
from itertools import islice, chain, zip_longest
from operator import attrgetter
from typing import Iterable, List, Any, Sized, Iterator, TYPE_CHECKING, Dict, \
    Tuple, Hashable, Type, Generic, Sequence, Generator, Optional, Union, Callable

from fliq._types import (
    T, U,
    Predicate, Selector, IndexSelector, NumericSelector,
    MISSING, MissingOrOptional
)
from fliq.exceptions import (
    QueryIsUnexpectedlyEmptyException, MultipleElementsFoundException, NotEnoughElementsException,
    ElementNotFoundException
)

if TYPE_CHECKING:
    from fliq import q  # noqa: F401 (used in docs)  # pragma: no cover


class Query(Generic[T], Iterable[T]):
    def __init__(self, iterable: Iterable[T]):
        """
        Create a Query object to allow fluent iterable processing
        """
        self._items: Iterable[T] = iterable
        self._iterator: Optional[Iterator[T]] = None

        # COW mode: copy-on-write mode, used to support snapshots
        self._cow_pending: bool = False

    def __iter__(self) -> Query[T]:
        if self._iterator is None:
            self._iterator = iter(self._items)
        return self

    def __next__(self) -> Union[T]:
        if self._iterator is None:
            self._iterator = iter(self._items)
        return next(self._iterator)

    def __contains__(self, item: Any) -> bool:
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

    def _self(self, updated_items: Optional[Iterable[U]] = None, in_snap: bool = False) -> Query[U]:
        """
        Adjusts the iterable of the query, and returns the query itself.
        This method abstract the need to create a new Query in some situations, to support
        the snapshot functionality.
        """
        updated_items = self._items if updated_items is None else updated_items  # type: ignore

        if in_snap:
            # COW prep: coming from snap, transform to list, don't copy object
            # This will allow multiple passes on this snapshot
            self._items = list(updated_items)  # type: ignore
            return self  # type: ignore
        elif self._cow_pending:
            # COW mode: coming from operation in COW mode, copy object
            # This will create a new query object in the first streamer following a snapshot
            # Following streamers will work on that same query object, minimizing object creations
            snapped_query = Query(iterable=updated_items)  # type: ignore
            return snapped_query
        else:
            # non-COW mode: coming from operation in non-COW mode, update iterable
            self._items = updated_items  # type: ignore
            return self  # type: ignore

    def __repr__(self) -> str:  # pragma: no cover
        """
        Returns a string representation of the query, while peeking at actual elements within
        the query. Query stays intact (i.e., no items are consumed).
        If representation is long, only the first 10 elements are shown, followed by an ellipsis.
        Elements are represented using their `repr` function.
        Inner iterable is represented as a list.

        Examples:
            >>> from fliq import q
            >>> q(range(10))
            Query([0, 1, 2, 3, 4, 5, 6, 7, 8, 9])
            >>> q(range(100))
            Query([0, 1, 2, 3, 4, 5, 6, 7, 8, 9, ...])
            >>> q([])
            Query([])
            >>> repr(q(range(3)))
            'Query([0, 1, 2])'

        Returns:
            A string representation of the query.
        """
        repr_length = 10
        sentinel = object()
        elements = [
            repr(e) for e in
            self.peek(n=repr_length+1, pad=sentinel) if e is not sentinel  # type: ignore
        ]
        peeked = ", ".join(elements[:repr_length])
        has_additional_items = len(elements) == repr_length+1
        if has_additional_items:
            peeked = peeked + ", ..."
        return f"Query([{peeked}])"

    # region Special Functionality

    def snap(self) -> Query[T]:
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

    def partition(self, by: Union[IndexSelector[T], Predicate[T]], n: int = 2) \
            -> Tuple[Query[T], ...]:
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

        partition_queues: Dict[int, List[T]] = {i: [] for i in range(n)}

        def partition_generator(queue_partition_idx: int) -> Iterable[T]:
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

    def peek(self, n: int = 1, pad: Optional[T] = None) \
            -> Union[Optional[T], Sequence[Optional[T]]]:
        """
        Return the first n elements of the query, without exhausting the query.
        If n is 1, returns the first element as a single item, otherwise returns a tuple
        (that can be unpacked).
        If n is greater than the number of elements in the query,
        `pad` will be returned for the remaining items (defaults to None).
        Use this to inspect the first n elements of the query, before consuming the query itself.
        Common use cases are logging and debugging.

        Examples:
            >>> from fliq import q
            >>> items = q(range(10))
            >>> i0, i1 = items.peek(2)
            >>> i0, i1
            (0, 1)
            >>> items.to_list()
            [0, 1, 2, 3, 4, 5, 6, 7, 8, 9]
            >>> a, b = q([]).peek(n=2)
            >>> a, b
            (None, None)

        Notes:
            Uses O(n) memory, as it materializes the first n elements.
            Supports infinite iterables.

        Args:
            n: Optional. The number of elements to peek. Defaults to 1.
            pad: Optional. The value to use for padding when the query is exhausted.

        Raises:
            ValueError: In case n is not positive.

        Returns:
            A tuple of the first n elements of the query. If the query has less than n elements, the
                other missing elements will be returned as None.
        """
        if n < 1:
            raise ValueError(f"n must be positive, got {n}")

        # If we already have an iterator, use it; otherwise, get one from _items
        if self._iterator is None:
            self._iterator = iter(self._items)

        # Consume the first n items
        first_n_items: List[T] = list(islice(self._iterator, n))

        # If we consumed less than n items, pad the result
        padding: List[Optional[T]] = [pad] * (n - len(first_n_items))

        # Adjust self._items to a new iterator that starts with the consumed items
        # followed by the remaining items
        self._items = chain(first_n_items, self._iterator)

        # Create a new iterator from the adjusted self._items
        self._iterator = iter(self._items)

        padded_result: Sequence[Optional[T]] = first_n_items + padding

        return padded_result if n > 1 else padded_result[0]

    # endregion

    # region Mappers

    def where(self, predicate: Optional[Predicate[T]] = None) -> Query[T]:
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

    def select(self, selector: Selector[T, U]) -> Query[U]:
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

    def exclude(self, predicate: Predicate[T]) -> Query[T]:
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

    def distinct(self) -> Query[T]:
        """
        Yields distinct elements while preserving order.
        Distinct supports infinite iterables.
        Note that elements must be hashable.

        Examples:
            >>> from fliq import q
            >>> q([0, 1, 0, 2, 2]).distinct().to_list()
            [0, 1, 2]

        Raises:
            TypeError: In case one or more items in the query are not hashable.
            """

        def generator(internal_items: Iterable[T]) -> Iterable[T]:
            seen = set()
            for item in internal_items:
                if item not in seen:
                    seen.add(item)
                    yield item

        items = generator(self._items)

        return self._self(items)

    def order(self,
              by: Optional[Selector[T, U]] = None,
              ascending: bool = True) -> Query[T]:
        """Yields elements in sorted order.

        Examples:
            >>> from fliq import q
            >>> q([4, 3, 2, 1, 0]).order().to_list()
            [0, 1, 2, 3, 4]

        Args:
            by: a selector function to extract the key from an item, defaults to None.
                If None, the default ordering is used.
                If exists, assumes the key is comparable.
            ascending: whether to sort in ascending or descending order, defaults to True.
        """
        # assumed to be comparable
        if by is None:
            items = sorted(self._items, reverse=not ascending)  # type: ignore
        else:
            items = sorted(self._items, key=by, reverse=not ascending)  # type: ignore
        return self._self(items)

    def shuffle(self,
                buffer_size: int = 10,
                seed: Optional[Hashable] = None,
                fair: bool = False) -> Query[T]:
        """
        Yields elements in a random order.
        Supports infinite iterables.

        Args:
            buffer_size (int): The size of the shuffle buffer for an unfair shuffle. Defaults to 10.
                Increasing the size of the buffer will require more memory.
                However, it will also result in a shuffle that is more evenly distributed (fair).
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
                    Use this for scenarios where fairness is not top priority,
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

        def shuffled_generator(internal_items: Iterable[T]) -> Iterable[T]:
            buffer: List[T] = []
            sentinel = object()
            items_iter = iter(internal_items)

            # fill the buffer
            for _ in range(buffer_size):
                item = next(items_iter, sentinel)
                if item is sentinel:
                    # iterable exhausted (smaller than buffer size)
                    break
                buffer.append(item)  # type: ignore # (item is of type T)

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

    def reverse(self) -> Query[T]:
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

    def slice(self, start: int = 0, stop: Optional[int] = None, step: int = 1) -> Query[T]:
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

    def take(self, n: int = 1, predicate: Optional[Predicate[T]] = None) -> Query[T]:
        """
        Yields up to n items that satisfy the predicate (if provided).
        In case the query is ordered, the first n elements are returned.

        Args:
            n: Optional. The number of elements to take. Defaults to 1.
            predicate: Optional. The predicate to filter the query by.
        """
        query = self.where(predicate).slice(stop=n)
        return self._self(query._items)

    def skip(self, n: int = 1) -> Query[T]:
        """
        Yields the elements after skipping the first n (as returned from the iterator).
        In case n is greater than the number of elements in the query, an empty query is returned.

        Examples:
            >>> from fliq import q
            >>> q([1, 2, 3, 4]).skip(n=2).to_list()
            [3, 4]
            >>> q([1, 2, 3, 4]).skip(n=0).to_list()
            [1, 2, 3, 4]
            >>> q([1]).skip(n=5).to_list()
            []

        Args:
            n: Optional. The number of items to take. Defaults to 1.
                If n=0, query is returned as is.
        """
        query = self.slice(start=n)
        return self._self(query._items)

    def zip(self,
            *iterables: Iterable[U],
            longest: bool = False,
            fill: Optional[Tuple[T, U]] = None) -> Query[Tuple[T, U]]:
        """
        Yields tuples of the elements of the query with the input iterables.
        The zipping stops as soon as the smallest of the iterables and the query is exhausted,
        unless longest is set to True, in which case the zipping stops when the longest iterable is
            exhausted. If strict mode is enabled, all iterables must have the same length.

        Examples:
            >>> from fliq import q
            >>> q(range(5)).zip([5, 6, 7]).to_list()
            [(0, 5), (1, 6), (2, 7)]
            >>> q(range(5)).zip([5, 6, 7], longest=True).to_list()
            [(0, 5), (1, 6), (2, 7), (3, None), (4, None)]
            >>> q(range(5)).zip([5, 6, 7], [8, 9, 10]).to_list()
            [(0, 5, 8), (1, 6, 9), (2, 7, 10)]
            >>> q(range(5)).zip([5, 6, 7], [8, 9, 10], longest=True, fill=-1).to_list()
            [(0, 5, 8), (1, 6, 9), (2, 7, 10), (3, -1, -1), (4, -1, -1)]

        Args:
            *iterables: One or more iterables to zip with the query.
            longest: If True, stop zipping when the longest iterable is exhausted.
                If False (default), stop when the shortest iterable is exhausted.
            fill: The value to use for padding when the longest iterable is exhausted.
                relevant only when `longest` is True.
        """
        zip_func: Callable[..., Iterable[Tuple[T, U]]]
        if longest:
            zip_func = lambda *args: zip_longest(*args, fillvalue=fill)  # noqa: E731
        else:
            zip_func = zip

        items: Iterable[Tuple[T, U]] = zip_func(self._items, *iterables)
        return self._self(items)

    def slide(self, window: int, overlap: int, pad: Optional[T] = None) -> Query[Tuple[T, ...]]:
        """
        Yields a sliding window over the iterable. In practice, these are tuples of size 'window'
         containing the current element and the next 'size-1' elements
         in the iterable. The tuples overlap by 'overlap' elements.

        Args:
            window: The size of the tuples to be returned.
            overlap: The number of elements that should overlap between consecutive tuples.
            pad: The value to use for padding the last window when the iterable is exhausted.

        Examples:
            >>> from fliq import q
            >>> q([1, 2, 3, 4]).slide(window=3, overlap=2).to_list()
            [(1, 2, 3), (2, 3, 4)]
            >>> q([1, 2, 3, 4]).slide(window=3, overlap=1).to_list()
            [(1, 2, 3), (3, 4, None)]
            >>> q([1, 2, 3, 4]).slide(window=3, overlap=1, pad=-1).to_list()
            [(1, 2, 3), (3, 4, -1)]
        """
        deque_window: deque[Optional[T]] = deque(maxlen=window)

        def _window(items: Iterable[T]) -> Generator[Tuple[Optional[T], ...], None, None]:
            has_any_items = False

            for item in items:
                has_any_items = True
                if len(deque_window) == window:
                    # make room for new items (leave 'overlap' items in the window)
                    for _ in range(window - overlap):
                        deque_window.popleft()
                # insert new items to the window
                deque_window.append(item)
                if len(deque_window) == window:
                    yield tuple(deque_window)

            if not has_any_items or len(deque_window) == window:
                # last window contained the last item, no need for another window
                return

            # another window needed, pad with 'fill'
            while len(deque_window) < window:
                deque_window.append(pad)
            yield tuple(deque_window)

        return self._self(_window(self._items))  # type: ignore

    def pairwise(self, pad: Optional[T] = None) -> Query[Tuple[T, T]]:
        """
        Yields tuples of consecutive elements in the query.
        Practically this is a sliding window of size 2, with overlap 0.

        Args:
            pad: The value to use for padding the last window in case the iterable size is odd.

        Examples:
            >>> from fliq import q
            >>> q([1, 2, 3, 4]).pairwise().to_list()
            [(1, 2), (3, 4)]
            >>> q([1, 2, 3, 4, 5]).pairwise().to_list()
            [(1, 2), (3, 4), (5, None)]
        """
        return self.slide(window=2, overlap=0, pad=pad)  # type: ignore

    def append(self, *single_items: T) -> Query[T]:
        """
        Yields the elements of the original query, followed by the input element(s).
        This supports multiple arguments, where each is considered as a single element.

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

    def append_many(self, items: Iterable[T]) -> Query[T]:
        """
        Yields the elements of the original query, followed by the elements given.

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

    def prepend(self, *single_items: T) -> Query[T]:
        """
        Yields the element(s) given, followed by the elements of the original query.
        This supports multiple arguments, where each is considered as a single element.

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

    def prepend_many(self, items: Iterable[T]) -> Query[T]:
        """
        Yields the elements given, followed by the elements of the original query.

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

    def group_by(self, key: Union[str, Selector[T, U]]) -> Query[List[T]]:
        """
        Yields an iterable of groups (as lists), where each group has identical key.
        If you require the group key, consider using `to_dict()` instead.

        Examples:
            >>> from fliq import q
            >>> q([1, 2, 3]).group_by(lambda x: x % 2 == 0).to_list()
            [[1, 3], [2]]

        Args:
            key: A function that takes an element and returns its grouping key,
                or a string representing the name of an attribute to group by.
        """
        groups = self._group_by(key)

        return self._self(groups.values())

    def _group_by(self, key: Union[str, Selector[T, U]]) -> Dict[U, List[T]]:
        groups = defaultdict(list)
        key_selector: Selector[T, U]
        if callable(key):
            key_selector = key
        else:
            # key is a string
            key_selector = attrgetter(key)
        for item in self._items:
            group_key = key_selector(item)
            groups[group_key].append(item)
        return groups

    def top(self, n: int = 1, by: Optional[NumericSelector[T]] = None) -> Query[T]:
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
        items: Iterable[T]
        if n <= 0:
            return self._self([])

        # heap holds tuples of (value, item), where value is either a numeric value
        # from the selector or the item itself if no selector is provided
        heap: List[Tuple[Union[T, int, float], T]] = []
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

    def bottom(self, n: int = 1, by: Optional[NumericSelector[T]] = None) -> Query[T]:
        """
        Yields the bottom n elements of the query, according to the selector (if provided).

        This is done in O(N log n) time, and O(n) space. Where n is the number of elements to take,
        and N is the number of elements in the query.

        Examples:
            >>> from fliq import q
            >>> q(range(10)).bottom(n=3).to_list()
            [0, 1, 2]

        Args:
            n: Optional. The number of elements to take. Defaults to 1.
            by: Optional. The selector function to apply to each element. Defaults to the identity.
                If by is None, the default ordering is used, which requires elements to be able to
                be multiplied by integers.
        """
        if by is None:
            return self.top(n=n, by=lambda x: -1 * x)  # type: ignore
        else:
            return self.top(n=n, by=lambda x: -1 * by(x))  # type: ignore # (by is not None)

    def flatten(
            self,
            max_depth: Optional[int] = None,
            ignore_types: Optional[Tuple[Type[Any], ...]] = (str, bytes)) -> Query[T]:
        """
        Yields a flattened iterable to a specified depth.

        Examples:
            >>> from fliq import q
            >>> q([[[1], 2], [3, 4]]).flatten().to_list()
            [1, 2, 3, 4]
            >>> q([[[1], 2], [3, 4]]).flatten(max_depth=1).to_list()
            [[1], 2, 3, 4]
            >>> q([['hello', 'world'], ['I', 'am', 'Fliq']]).flatten().to_list()
            ['hello', 'world', 'I', 'am', 'Fliq']
            >>> q([['hello', 'world'], ['I', 'am', 'Fliq']]).flatten(ignore_types=None).to_list()
            ['h', 'e', 'l', 'l', 'o', 'w', 'o', 'r', 'l', 'd', 'I', 'a', 'm', 'F', 'l', 'i', 'q']

        Args:
            max_depth: Optional. Non-negative. The maximum depth to flatten to. Defaults to none
                (no limit, completely flat). If max_depth is 0, the query is left unchanged.
            ignore_types: Optional. A tuple of types to ignore flattening for.
                Defaults to (str, bytes).

        Raises:
            ValueError: In case max_depth is non-positive.
        """
        if max_depth is not None and max_depth < 0:
            raise ValueError(f"max_depth must be non-negative (or -1 by default), got {max_depth}")

        def _flatten(iterable: Iterable[Any], current_depth: int) -> Iterable[Any]:
            for item in iterable:
                type_ignored = ignore_types is not None and isinstance(item, ignore_types)
                single_char_byte = isinstance(item, (str, bytes)) and len(item) == 1
                if not single_char_byte and isinstance(item, Iterable) and not type_ignored:
                    if max_depth is None or current_depth < max_depth:
                        yield from _flatten(item, current_depth + 1)
                    else:
                        yield item
                else:
                    yield item

        return self._self(_flatten(self._items, 0))

    def interleave(self, *iterables: Iterable[U]) -> Query[Union[T, U]]:
        """
        Combines the elements of the query with the elements of the provided iterables
        into a single Query. The elements are interleaved in the order they appear in their
        respective sources (similar to zip). The process continues until all sources are exhausted.
        No padding is done in case the iterables are of different lengths.

        Examples:
            >>> from fliq import q
            >>> q([1, 2, 3]).interleave([4], [5, 6]).to_list()
            [1, 4, 5, 2, 6, 3]

        Args:
            *iterables: One or more iterables to unify with the query.
        """
        sentinel = object()
        items: zip_longest[Tuple[T, U]] = zip_longest(self._items, *iterables,
                                                      fillvalue=sentinel)  # type: ignore
        flattened_items: Iterable[Union[T, U]] = chain.from_iterable(items)
        non_sentinel_items: Iterable[Union[T, U]] = filter(lambda x: x is not sentinel,
                                                           flattened_items)
        return self._self(non_sentinel_items)

    def most_common(self, n: int = 1) -> Query[T]:
        """
        Yields the most common n elements, in descending order of frequency.
        By definition, does not support inifinte iterables.

        Examples:
            >>> from fliq import q
            >>> q([1, 2, 3, 1, 2, 1]).most_common(n=1).single()
            1
            >>> q([1, 2, 3, 1, 2, 1]).most_common(n=2).to_list()
            [1, 2]

        Args:
            n: Optional. The number of elements to return. Defaults to 1.

        Raises:
            NotEnoughElementsException: In case the query does not have n items.
        """
        top_counts = Counter(self._items).most_common(n)
        if len(top_counts) < n:
            raise NotEnoughElementsException(f"Found {len(top_counts)} items, expected {n}")
        top_elements = [item for item, count in top_counts]
        return self._self(top_elements)

    # endregion

    # region Materializers

    def first(self,
              predicate: Optional[Predicate[T]] = None,
              default: MissingOrOptional[T] = MISSING) -> Optional[T]:
        """
        Returns the first element in the query that satisfies the predicate (if provided),
            or a default value if the query is empty.
            If default is not provided, raises QueryIsUnexpectedlyEmptyException in case the query
            is empty.

        Args:
            predicate: Optional. The predicate to filter the query by.
            default: Optional. The default value to return in case the query is empty.
                Defaults to raise an exception if the query is empty.

        Raises:
            QueryIsUnexpectedlyEmptyException: In case the query is empty.

        Examples:
            >>> from fliq import q
            >>> q([1, 2, 3]).first()
            1
            >>> q([]).first()
            Traceback (most recent call last):
            ...
            fliq.exceptions.QueryIsUnexpectedlyEmptyException
            >>> q([]).first(default=-1)
            -1
            >>> q([]).first(default=None) # returns None
        """
        query = self.where(predicate)
        first_item = next(query, MISSING)
        if first_item is MISSING:
            # query is empty
            if default is MISSING:
                # no default value provided
                raise QueryIsUnexpectedlyEmptyException()
            else:
                return default  # type: ignore # default is not MISSING
        else:
            return first_item  # type: ignore # first_item is not MISSING

    def single(self,
               predicate: Optional[Predicate[T]] = None,
               default: MissingOrOptional[T] = MISSING) -> Optional[T]:
        """
        Returns the single element in the query, or a default value if the query is empty.
            Single expects the query to have at most one element (if default is provided), or
            exactly one element (if default is not provided).

        Args:
            predicate: Optional. The predicate to filter the query by.
            default: Optional. The default value to return in case the query is empty.
                Defaults to raise an exception if the query is empty.

        Examples:
            >>> from fliq import q
            >>> q([1]).single()
            1
            >>> q([]).single()
            Traceback (most recent call last):
            ...
            fliq.exceptions.QueryIsUnexpectedlyEmptyException
            >>> q([1]).single(default=None)
            1
            >>> q([]).single(default=None) # returns None

            >>> q([1, 2, 3]).single(default=None)
            Traceback (most recent call last):
            ...
            fliq.exceptions.MultipleElementsFoundException

        Raises:
            QueryIsUnexpectedlyEmptyException: In case the query is empty.
            MultipleElementsFoundException: In case the query has more than one element.
        """
        query = self.where(predicate)
        first_item = next(query, default)

        sentinel = object()
        second_item = next(query, sentinel)
        if second_item is sentinel:
            # query has 0 or 1 items
            if default is MISSING and first_item is default:
                # query is empty, user did not allow default
                raise QueryIsUnexpectedlyEmptyException()
            else:
                return first_item  # type: ignore # MISSING isn't returned
        else:
            # query has more than 1 item
            raise MultipleElementsFoundException()

    def at(self,
           index: int,
           default: MissingOrOptional[T] = MISSING) -> Optional[T]:
        """
        Returns the element in the query at the specified index, or a default value if the query is
            too short.
            If default is not provided, raises ElementNotFoundException in case the query
            is too short.

        Args:
            index: The index of the element to return.
            default: Optional. The default value to return in case the query is too short.
                Defaults to raise an exception if the query is too short.

        Examples:
            >>> from fliq import q
            >>> q([1, 2, 3]).at(0)
            1
            >>> q([]).at(0)
            Traceback (most recent call last):
            ...
            fliq.exceptions.ElementNotFoundException
            >>> q([1, 2, 3]).at(index=5, default=None) # returns None

        Raises:
            ElementNotFoundException: In case the query is too short.
            QueryIsUnexpectedlyEmptyException: In case the query is empty.
        """
        # if items can be accessed using index, do that
        if isinstance(self._items, collections.abc.Sequence):
            try:
                return self._items[index]  # type: ignore # (item is of type T)
            except IndexError:
                if default is MISSING:
                    raise ElementNotFoundException()
                else:
                    return default  # type: ignore # default is not MISSING
        try:
            return self.skip(index).first(default=default)
        except QueryIsUnexpectedlyEmptyException:
            raise ElementNotFoundException()

    def sample(self,
               n: int = 1,
               seed: Optional[Hashable] = None,
               budget_factor: Optional[int] = 10,
               stop_factor: Optional[int] = 10) -> Union[T, List[T]]:
        """
        Returns a random sample of n elements from the query.
        If n is 1, returns a single item, otherwise returns a tuple (that can be unpacked).

        Examples:
            >>> from fliq import q
            >>> q(range(10)).sample(n=2, seed=42)
            [0, 4]
            >>> q(range(10)).sample(n=1, seed=42)
            1

        Args:
            n: Optional. The number of elements to sample. Defaults to 1.
            seed: Optional. The seed to use for the random sample. Defaults to None.
            budget_factor: Optional. Limits the number of attempts to sample n items,
                as a factor of n. Defaults to 10, which means a budget of 10 * n.
                None will disable budgeting, and may exhaust the iterable
                (depending on stop_factor).
            stop_factor: Optional. The probability to stop re-sampling once the sample is full,
                as a factor of n: 1 / ( stop_factor * n). Defaults to 10, which means a factor of
                1 / (10 * n). None will disable early stopping, and may exhaust the iterable
                (depending on budget_factor).

        Note:
            * To safely support infinite iterables, make sure you use
                budget_factor and/or stop_factor (they are set by default).

        Raises:
            NotEnoughItemsFoundException: In case the query is exhausted before n items are sampled.
            ValueError: In case n is not positive.
        """
        if n < 1:
            raise ValueError(f"n must be positive, got {n}")

        if budget_factor is not None and budget_factor < 1:
            raise ValueError(f"budget factor must be bigger than 1, got {budget_factor}")

        if stop_factor is not None and stop_factor < 1:
            raise ValueError(f"budget factor must be bigger than 1, got {stop_factor}")

        rand = random.Random(seed)

        reservoir: List[T] = []
        total_processed = 0
        budget = None if budget_factor is None else n * budget_factor
        stop_probability = None if stop_factor is None else 1 / (stop_factor * n)

        for element in itertools.islice(self._items, budget):
            total_processed += 1
            if len(reservoir) < n:
                reservoir.append(element)
            else:
                # Replace elements with decreasing probability
                replace_index = rand.randint(1, total_processed)
                if replace_index <= n:
                    reservoir[replace_index - 1] = element

                # Check for early stopping condition
                if stop_probability is not None and rand.random() < stop_probability:
                    break

        if len(reservoir) < n:
            raise NotEnoughElementsException("too many items requested")

        return reservoir[0] if n == 1 else reservoir

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

    def any(self, predicate: Optional[Predicate[T]] = None) -> bool:
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

    def all(self, predicate: Optional[Predicate[T]] = None) -> bool:
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

    def aggregate(self, by: Callable[[T, T], U], initial: Optional[U] = None) -> T:
        """
        Applies an accumulator function over the query.

        For an optimized summation of numeric values, use `sum`.

        Examples:
            >>> from fliq.tests.fliq_test_utils import Point
            >>> from fliq import q
            >>> q([Point(0, 0), Point(1, 1), Point(2, 2)]).aggregate(by=lambda a, b: a + b)
            Point(x=3, y=3)
            >>> q([Point(1, 1), Point(2, 2)]).aggregate(by=lambda a, b: a + b, initial=Point(0, 0))
            Point(x=3, y=3)

        Args:
            by: The accumulator function to apply to each two elements.
            initial: Optional. The initial value of the accumulator. Defaults to None.
                If provided, it will also serve as the default value for an empty query.
                If not provided, the first element of the query will be used as the initial value.
        """
        if initial is not None:
            return reduce(by, self._items, initial)  # type: ignore # (by items of the same type)
        else:
            return reduce(by, self._items)  # type: ignore # (by items of the same type)

    def max(self,
            by: Optional[Selector[T, U]] = None) -> T:
        """
        Returns the maximal element in the query.
        If a selector is provided, maximality is determined by the selected value.

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
                If None, the default ordering is used.
                If exists, assumes the key is comparable.

        Raises:
            ValueError: In case the query is empty.
        """
        # assumed to be comparable
        if by is None:
            return max(self)  # type: ignore
        else:
            return max(self, key=by)  # type: ignore

    def min(self,
            by: Optional[Selector[T, U]] = None) -> T:
        """
        Returns the minimal element in the query.
        If a selector is provided, minimality is determined by the selected value.

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
                If None, the default ordering is used.
                If exists, assumes the key is comparable.

        Raises:
            ValueError: In case the query is empty.
        """
        # assumed to be comparable
        if by is None:
            return min(self)  # type: ignore
        else:
            return min(self, key=by)  # type: ignore

    def contains(self, item: Any) -> bool:
        """
        Returns whether the query contains the given item (by equality, not identity).
        Query also supports the `in` and `not in` syntax, which are identical in functionality.

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

    def equals(self, other: Iterable[T], bag_compare: bool = False) -> bool:
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

    def sum(self,
            by: Optional[NumericSelector[T]] = None,
            accumulator: Union[int, float] = 0) -> Union[int, float]:
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
            query = self.select(by)  # type: ignore # (here `by` is subtype of select `by`)
        return sum(query, start=accumulator)  # type: ignore # (query type is okay)

    # endregion

    def to_list(self) -> List[T]:
        """
        Returns the elements of the query as a list.
        """
        return list(self)

    def to_dict(self, key: Union[str, Selector[T, U]]) -> Dict[U, List[T]]:
        """
        Returns the elements of the query as a dictionary, grouped by the given key.
        If you don't require the group key, consider using `group_by()` instead.

        Examples:
            >>> from fliq import q
            >>> q([1, 2, 3]).to_dict(key=lambda x: x % 2 == 0)
            {False: [1, 3], True: [2]}

        Args:
            key: The selector function to apply to each element, or a string representing
                the name of an attribute to group by.
        """
        return dict(self._group_by(key))

    # endregion

    @staticmethod
    def _validate_partition_index(item_partition_idx: Union[int, bool], n: int) -> None:
        if isinstance(item_partition_idx, bool) and n != 2:
            raise TypeError(f"Partitioning by predicate is only supported for n=2, found n=`{n}`")
        if not (0 <= item_partition_idx < n):
            raise ValueError(f"Partition index {item_partition_idx} is not in range [0, {n})")
