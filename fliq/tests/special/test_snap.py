import pytest

from fliq.exceptions import NoItemsFoundException
from fliq.tests.fliq_test_utils import Params
from fliq import q


class TestSnap:
    @pytest.mark.parametrize(Params.sig_iterable, Params.iterable_multi())
    def test_noSnap_differentPasses_iterableExhausted(self, iter_type, iterable, iterable_list):
        evens = q(iterable).where(lambda x: int(x) % 2 == 0)
        evens.single(lambda x: int(x) > 2)
        with pytest.raises(NoItemsFoundException):
            evens.single(lambda x: int(x) < 0)

    @pytest.mark.parametrize(Params.sig_iterable, Params.iterable_multi())
    def test_snap_differentPasses_snapshotUsed(self, iter_type, iterable, iterable_list):
        evens = q(iterable).where(lambda x: int(x) % 2 == 0).snap()
        big = evens.single(lambda x: int(x) > 2)
        small = evens.single(lambda x: int(x) < 2)

        assert int(big) == 4
        assert int(small) == 0

    @pytest.mark.parametrize(Params.sig_iterable, Params.iterable_multi())
    def test_snap_multipleSnaps_lastIsConsidered(self, iter_type, iterable, iterable_list):
        evens = (
            q(iterable)
            .where(lambda x: int(x) % 2 == 0)
            .snap()
            .select(lambda x: int(x) * 2)
            .snap()
        )
        first = evens.first(lambda x: x > 0)
        second = evens.first(lambda x: x > 0)

        assert first == 4
        assert second == 4

    @pytest.mark.parametrize(Params.sig_iterable, Params.iterable_multi())
    def test_snap_snapNotLast(self, iter_type, iterable, iterable_list):
        evens = (
            q(iterable)
            .where(lambda x: int(x) % 2 == 0)
            .snap()
            .select(lambda x: int(x) * 2)
        )  # [0, 4, 8, 12, 16]
        first = evens.first()
        second = evens.first(lambda x: x > first)

        assert first == 0
        assert second == 4

    @pytest.mark.parametrize(Params.sig_iterable, Params.iterable_multi())
    def test_noSnap_firstTwice_firstAndSecondReturned(self, iter_type, iterable, iterable_list):
        evens = (
            q((i for i in range(5)))
            .where(lambda x: int(x) % 2 == 0)
        )
        first1 = evens.first()
        first2 = evens.first()

        assert first1 == 0
        assert first2 == 2

    @pytest.mark.parametrize(Params.sig_iterable, Params.iterable_multi())
    def test_snap_firstTwice_firstReturnedTwice(self, iter_type, iterable, iterable_list):
        evens = (
            q((i for i in range(5)))
            .where(lambda x: int(x) % 2 == 0)
            .snap()
        )
        first1 = evens.first()
        first2 = evens.first()

        assert first1 == 0
        assert first2 == 0

    @pytest.mark.parametrize(Params.sig_iterable, Params.iterable_multi())
    def test_snap_streamerAndCollector(self, iter_type, iterable, iterable_list):
        evens = (
            q((i for i in range(5)))
            .where(lambda x: int(x) % 2 == 0)
            .snap()
        )  # [0, 2, 4]

        count = evens.count()
        first_doubled1 = evens.select(lambda x: x * 2).first()
        first_doubled2 = evens.select(lambda x: x * 2).first()

        assert count == 3
        assert first_doubled1 == 0
        assert first_doubled2 == 0
