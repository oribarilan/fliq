import pytest

from fliq import q
from fliq.tests.fliq_test_utils import Params


class TestCount:
    @pytest.mark.parametrize(Params.sig_iterable, Params.iterable_empty())
    def test_count_hasNoItems(self, iter_type, iterable, iterable_list):
        assert q(iterable).count() == len(iterable_list)

    @pytest.mark.parametrize(Params.sig_iterable, Params.iterable_single())
    def test_get_hasSingleItem(self, iter_type, iterable, iterable_list):
        assert q(iterable).count() == len(iterable_list)

    @pytest.mark.parametrize(Params.sig_iterable, Params.iterable_multi())
    def test_get_hasMultipleItems(self, iter_type, iterable, iterable_list):
        assert q(iterable).count() == len(iterable_list)
