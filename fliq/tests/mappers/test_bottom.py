import pytest

from fliq import q
from fliq.tests.fliq_test_utils import Params, MyTestClass


class TestBottom:
    @pytest.mark.parametrize(Params.sig_iterable, Params.iterable_empty())
    def test_bottom_hasNoItems(self,
                               iter_type,
                               iterable,
                               iterable_list):
        assert q(iterable).bottom(n=5) == iterable_list

    @pytest.mark.parametrize(Params.sig_iterable, Params.iterable_single())
    def test_bottom_hasSingleItem(self,
                                  iter_type,
                                  iterable,
                                  iterable_list):
        assert q(iterable).bottom(n=5) == iterable_list

    @pytest.mark.parametrize(Params.sig_iterable, Params.iterable_multi())
    def test_bottom_hasMultipleItems_withoutSelector(self,
                                                     iter_type,
                                                     iterable,
                                                     iterable_list):
        if iter_type == "str":
            # not testing str because it requires a selector here, irrelevant for this case
            return
        assert q(iterable).bottom(n=3) == sorted(iterable_list, reverse=False)[:3]

    @pytest.mark.parametrize(Params.sig_iterable, Params.iterable_multi())
    def test_bottom_hasMultipleItems_withSelector(self,
                                                  iter_type,
                                                  iterable,
                                                  iterable_list):
        assert q(iterable).bottom(n=1, by=lambda x: -int(x)) == [max(iterable_list)]

    @pytest.mark.parametrize(Params.sig_iterable_obj, Params.iterable_obj_multi())
    def test_bottom_hasMultipleObjectItems_withSelector(self,
                                                        iter_type,
                                                        iterable):
        assert q(iterable).bottom(n=2, by=lambda x: x.a) == [
            MyTestClass(0, 0),
            MyTestClass(1, 1 * 2)
        ]

    def test_bottom_hasMultipleItems_notEnoughItems(self):
        assert q(range(5)).bottom(n=100) == sorted(range(5), reverse=False)
