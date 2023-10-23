import pytest

from fliq.tests.fliq_test_utils import Params
from fliq import q


class TestWhere:
    @pytest.mark.parametrize(Params.sig_iterable, Params.iterable_empty())
    def test_where_hasNoItems_withPredicate(self,
                                            iter_type,
                                            iterable,
                                            iterable_list):
        assert list(q(iterable).where(lambda x: int(x) > 0)) == iterable_list

    @pytest.mark.parametrize(Params.sig_iterable, Params.iterable_empty())
    def test_where_hasNoItems_withoutPredicate(self,
                                               iter_type,
                                               iterable,
                                               iterable_list):
        assert list(q(iterable).where()) == iterable_list

    @pytest.mark.parametrize(Params.sig_iterable, Params.iterable_single())
    def test_where_hasSingleItem_withoutPredicate(self,
                                                  iter_type,
                                                  iterable,
                                                  iterable_list):
        assert list(q(iterable).where()) == iterable_list

    @pytest.mark.parametrize(Params.sig_iterable, Params.iterable_single())
    def test_where_hasSingleItem_withPredicate(self,
                                               iter_type,
                                               iterable,
                                               iterable_list):
        assert list(q(iterable).where(lambda x: int(x) < 0)) == []

    @pytest.mark.parametrize(Params.sig_iterable, Params.iterable_multi())
    def test_where_hasMultipleItems_withoutFilter(self,
                                                  iter_type,
                                                  iterable,
                                                  iterable_list):
        query = q(iterable).where(lambda x: int(x) > 2)
        assert list(query) == iterable_list[3:]
