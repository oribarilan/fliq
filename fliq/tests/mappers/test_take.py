import pytest

from fliq import q
from fliq.tests.fliq_test_utils import Params


class TestTake:
    @pytest.mark.parametrize(Params.sig_iterable, Params.iterable_empty())
    def test_take_hasNoItems(self,
                             iter_type,
                             iterable,
                             iterable_list):
        assert list(q(iterable).take(n=5)) == iterable_list

    @pytest.mark.parametrize(Params.sig_iterable, Params.iterable_single())
    def test_take_hasSingleItem(self,
                                iter_type,
                                iterable,
                                iterable_list):
        assert list(q(iterable).take(n=5)) == iterable_list

    @pytest.mark.parametrize(Params.sig_iterable, Params.iterable_multi())
    def test_take_hasMultipleItems_withoutPredicate(self,
                                                    iter_type,
                                                    iterable,
                                                    iterable_list):
        query = q(iterable).take(n=3)
        assert list(query) == iterable_list[:3]

    @pytest.mark.parametrize(Params.sig_iterable, Params.iterable_multi())
    def test_take_hasMultipleItems_withPredicate(self,
                                                 iter_type,
                                                 iterable,
                                                 iterable_list):
        query = q(iterable).take(n=1, predicate=lambda x: int(x) > 1)
        assert list(query) == iterable_list[2:3]

    @pytest.mark.parametrize(Params.sig_iterable, Params.iterable_multi())
    def test_take_hasMultipleItems_notEnoughItems(self,
                                                  iter_type,
                                                  iterable,
                                                  iterable_list):
        assert list(q(iterable).take(n=100)) == iterable_list
