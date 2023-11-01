import pytest

from fliq import q
from fliq.tests.fliq_test_utils import Params, MyTestClass


class TestTop:
    def test_top_topZero(self):
        assert q(range(10)).top(n=0) == []

    @pytest.mark.parametrize(Params.sig_iterable, Params.iterable_empty())
    def test_top_hasNoItems(self,
                            iter_type,
                            iterable,
                            iterable_list):
        assert q(iterable).top(n=5) == iterable_list

    @pytest.mark.parametrize(Params.sig_iterable, Params.iterable_single())
    def test_top_hasSingleItem(self,
                               iter_type,
                               iterable,
                               iterable_list):
        assert q(iterable).top(n=5) == iterable_list

    @pytest.mark.parametrize(Params.sig_iterable, Params.iterable_multi())
    def test_top_hasMultipleItems_withoutSelector(self,
                                                  iter_type,
                                                  iterable,
                                                  iterable_list):
        assert q(iterable).top(n=3) == sorted(iterable_list, reverse=True)[:3]

    @pytest.mark.parametrize(Params.sig_iterable, Params.iterable_multi())
    def test_top_hasMultipleItems_withSelector(self,
                                               iter_type,
                                               iterable,
                                               iterable_list):
        assert q(iterable).top(n=1, by=lambda x: -int(x)) == [min(iterable_list)]

    @pytest.mark.parametrize(Params.sig_iterable_obj, Params.iterable_obj_multi())
    def test_top_hasMultipleObjectItems_withSelector(self,
                                                     iter_type,
                                                     iterable):
        assert q(iterable).top(n=2, by=lambda x: x.a) == [
            MyTestClass(4, 4 * 2),
            MyTestClass(3, 3 * 2)
        ]

    @pytest.mark.parametrize(Params.sig_iterable, Params.iterable_multi())
    def test_top_hasMultipleItems_notEnoughItems(self,
                                                 iter_type,
                                                 iterable,
                                                 iterable_list):
        assert q(iterable).top(n=100) == sorted(iterable_list, reverse=True)
