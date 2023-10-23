import pytest

from fliq import q
from fliq.tests.fliq_test_utils import Params, MyTestClass


class TestMin:
    @pytest.mark.parametrize(Params.sig_iterable, Params.iterable_empty())
    def test_min_hasNoItems_raisesException(self, iter_type, iterable, iterable_list):
        with pytest.raises(ValueError):
            q(iterable).min()

    @pytest.mark.parametrize(Params.sig_iterable, Params.iterable_single())
    def test_min_hasSingleItem(self, iter_type, iterable, iterable_list):
        assert q(iterable).min() == iterable_list[0]

    @pytest.mark.parametrize(Params.sig_iterable, Params.iterable_multi())
    def test_min_hasMultipleItems(self, iter_type, iterable, iterable_list):
        assert q(iterable).min() == min(iterable_list)

    @pytest.mark.parametrize(Params.sig_iterable, Params.iterable_multi())
    def test_sum_hasMultipleItems_customSelector(self, iter_type, iterable, iterable_list):
        assert int(q(iterable).min(by=lambda x: int(x)*-1)) == 4

    @pytest.mark.parametrize(Params.sig_iterable_obj, Params.iterable_obj_single())
    def test_min_hasSingleItem_customObjects(self, iter_type, iterable):
        assert q(iterable).min() == MyTestClass(0, 0)

    @pytest.mark.parametrize(Params.sig_iterable_obj, Params.iterable_obj_multi())
    def test_min_hasMultipleItems_customObjects(self, iter_type, iterable):
        assert q(iterable).min() == MyTestClass(0, 0)

    @pytest.mark.parametrize(Params.sig_iterable_obj, Params.iterable_obj_single())
    def test_min_hasSingleItem_customObjectsCustomAccumulator(self, iter_type, iterable):
        assert q(iterable).min(by=lambda o: o.a) == MyTestClass(0, 0)

    @pytest.mark.parametrize(Params.sig_iterable_obj, Params.iterable_obj_multi())
    def test_min_hasMultipleItems_customObjectsCustomAccumulator(self, iter_type, iterable):
        assert q(iterable).min(by=lambda o: o.a) == MyTestClass(0, 0)

