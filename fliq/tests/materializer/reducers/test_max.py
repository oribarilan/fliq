import pytest

from fliq import q
from fliq.tests.fliq_test_utils import Params, MyTestClass


class TestMax:
    @pytest.mark.parametrize(Params.sig_iterable, Params.iterable_empty())
    def test_max_hasNoItems_raisesException(self, iter_type, iterable, iterable_list):
        with pytest.raises(ValueError):
            q(iterable).max()

    @pytest.mark.parametrize(Params.sig_iterable, Params.iterable_single())
    def test_max_hasSingleItem(self, iter_type, iterable, iterable_list):
        assert q(iterable).max() == iterable_list[0]

    @pytest.mark.parametrize(Params.sig_iterable, Params.iterable_multi())
    def test_max_hasMultipleItems(self, iter_type, iterable, iterable_list):
        assert q(iterable).max() == max(iterable_list)

    @pytest.mark.parametrize(Params.sig_iterable, Params.iterable_multi())
    def test_sum_hasMultipleItems_customSelector(self, iter_type, iterable, iterable_list):
        assert int(q(iterable).max(by=lambda x: int(x)*-1)) == 0

    @pytest.mark.parametrize(Params.sig_iterable_obj, Params.iterable_obj_single())
    def test_max_hasSingleItem_customObjects(self, iter_type, iterable):
        assert q(iterable).max() == MyTestClass(0, 0)

    @pytest.mark.parametrize(Params.sig_iterable_obj, Params.iterable_obj_multi())
    def test_max_hasMultipleItems_customObjects(self, iter_type, iterable):
        assert q(iterable).max() == MyTestClass(4, 4 * 2)

    @pytest.mark.parametrize(Params.sig_iterable_obj, Params.iterable_obj_single())
    def test_max_hasSingleItem_customObjectsCustomAccumulator(self, iter_type, iterable):
        assert q(iterable).max(by=lambda o: o.a) == MyTestClass(0, 0)

    @pytest.mark.parametrize(Params.sig_iterable_obj, Params.iterable_obj_multi())
    def test_max_hasMultipleItems_customObjectsCustomAccumulator(self, iter_type, iterable):
        assert q(iterable).max(by=lambda o: o.a) == MyTestClass(4, 4 * 2)
