import pytest

from fliq import q
from fliq.tests.fliq_test_utils import Params


class TestCarrierSelect:
    @pytest.mark.parametrize(Params.sig, Params.iterable_empty())
    def test_select_hasNoItems(self, iter_type, iterable):
        assert list(q(iterable).select(lambda x: x.a)) == []

    @pytest.mark.parametrize(Params.sig, Params.iterable_obj_single())
    def test_select_hasSingleItem(self, iter_type, iterable):
        assert list(q(iterable).select(lambda x: x.a)) == [0]

    @pytest.mark.parametrize(Params.sig, Params.iterable_obj_multi())
    def test_select_hasMultipleItems(self, iter_type, iterable):
        assert list(q(iterable).select(lambda x: x.a)) == [0, 1, 2, 3, 4]
