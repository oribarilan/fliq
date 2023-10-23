import pytest

from fliq import q
from fliq.tests.fliq_test_utils import Params, MyTestClass


class TestSum:
    @pytest.mark.parametrize(Params.sig_iterable, Params.iterable_empty())
    def test_sum_hasNoItems_customAccumulator(self, iter_type, iterable, iterable_list):
        assert q(iterable).sum(accumulator=1) == 1

    @pytest.mark.parametrize(Params.sig_iterable, Params.iterable_empty())
    def test_sum_hasNoItems(self, iter_type, iterable, iterable_list):
        assert q(iterable).sum() == 0

    @pytest.mark.parametrize(Params.sig_iterable, Params.iterable_single())
    def test_sum_hasSingleItem(self, iter_type, iterable, iterable_list):
        if iter_type == 'str':
            # sum should be used with numbers only
            return
        assert q(iterable).sum() == iterable_list[0]

    @pytest.mark.parametrize(Params.sig_iterable, Params.iterable_multi())
    def test_sum_hasMultipleItems(self, iter_type, iterable, iterable_list):
        if iter_type == 'str':
            # sum should be used with numbers only
            return
        assert q(iterable).sum() == sum(iterable_list)

    @pytest.mark.parametrize(Params.sig_iterable, Params.iterable_multi())
    def test_sum_hasMultipleItems_customSelector(self, iter_type, iterable, iterable_list):
        if iter_type == 'str':
            # sum should be used with numbers only
            return
        assert q(iterable).sum(by=lambda x: x*2) == sum([x*2 for x in iterable_list])

    @pytest.mark.parametrize(Params.sig_iterable_obj, Params.iterable_obj_single())
    def test_sum_hasSingleItem_customObjects(self, iter_type, iterable):
        assert q(iterable).sum(by=lambda o: o.a) == 0

    @pytest.mark.parametrize(Params.sig_iterable_obj, Params.iterable_obj_multi())
    def test_sum_hasMultipleItems_customObjects(self, iter_type, iterable):
        assert q(iterable).sum(by=lambda o: o.a) == 10

    @pytest.mark.parametrize(Params.sig_iterable_obj, Params.iterable_obj_single())
    def test_sum_hasSingleItem_customObjects_customAccumulator(self, iter_type, iterable):
        assert q(iterable).sum(accumulator=MyTestClass(0, 0)) == MyTestClass(0, 0)

    @pytest.mark.parametrize(Params.sig_iterable_obj, Params.iterable_obj_multi())
    def test_sum_hasMultipleItems_customObjects_customAccumulator(self, iter_type, iterable):
        assert q(iterable).sum(accumulator=MyTestClass(0, 0)) == MyTestClass(10, 10 * 2)

    @pytest.mark.parametrize(Params.sig_iterable_obj, Params.iterable_obj_multi())
    def test_sum_hasMultipleItems_customObjectsNoAccumulator(self, iter_type, iterable):
        assert q(iterable).sum() == MyTestClass(10, 10 * 2)
