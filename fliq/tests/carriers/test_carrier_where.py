import pytest

from fliq.tests.fliq_test_utils import Params
from fliq import q


class TestCarrierWhere:
    @pytest.mark.parametrize(Params.sig, Params.iterable_empty())
    def test_where_hasNoItems_withPredicate(self, iter_type, iterable):
        assert list(q(iterable).where(lambda x: int(x) > 0)) == []

    @pytest.mark.parametrize(Params.sig, Params.iterable_empty())
    def test_where_hasNoItems_withoutPredicate(self, iter_type, iterable):
        assert list(q(iterable).where()) == []

    @pytest.mark.parametrize(Params.sig, Params.iterable_single())
    def test_where_hasSingleItem_withoutPredicate(self, iter_type, iterable):
        lst = list(iterable)
        assert list(q(lst).where()) == list(lst)

    @pytest.mark.parametrize(Params.sig, Params.iterable_single())
    def test_where_hasSingleItem_withPredicate(self, iter_type, iterable):
        lst = list(iterable)
        assert list(q(lst).where(lambda x: int(x) < 0)) == []

    @pytest.mark.parametrize(Params.sig, Params.iterable_multi())
    def test_where_hasMultipleItems_withoutFilter(self, iter_type, iterable):
        lst = list(iterable)
        query = q(lst).where(lambda x: int(x) > 2)
        assert [int(i) for i in query] == [3, 4]
