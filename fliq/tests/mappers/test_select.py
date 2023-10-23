import pytest

from fliq import q
from fliq.tests.fliq_test_utils import Params


class TestSelect:
    @pytest.mark.parametrize(Params.sig_iterable, Params.iterable_empty())
    def test_select_hasNoItems(self, iter_type, iterable, iterable_list):
        assert list(q(iterable).select(lambda x: x.a)) == []

    @pytest.mark.parametrize(Params.sig_iterable_obj, Params.iterable_obj_single())
    def test_select_hasSingleItem(self, iter_type, iterable):
        assert list(q(iterable).select(lambda x: x.a)) == [0]

    @pytest.mark.parametrize(Params.sig_iterable_obj, Params.iterable_obj_multi())
    def test_select_hasMultipleItems(self, iter_type, iterable):
        assert list(q(iterable).select(lambda x: x.a)) == [0, 1, 2, 3, 4]
