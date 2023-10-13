import pytest

from fliq import q
from fliq.tests.fliq_test_utils import Params


class TestCollectorAny:
    @pytest.mark.parametrize(Params.sig_iterable, Params.iterable_empty())
    def test_any_hasNoItems(self, iter_type, iterable, iterable_list):
        assert not q(iterable).any()

    def test_any_hasSingleItem_integer(self):
        assert not q([0, 0]).any()

    def test_any_hasSingleItem_nones(self):
        assert not q([None, None]).any()

    @pytest.mark.parametrize(Params.sig_iterable, Params.iterable_multi())
    def test_get_hasMultipleItems(self, iter_type, iterable, iterable_list):
        assert q(iterable).any()
