import pytest

from fliq import q
from fliq.tests.fliq_test_utils import Params


class TestToList:
    @pytest.mark.parametrize(Params.sig_iterable, Params.iterable_empty())
    def test_toList_hasNoItems(self, iter_type, iterable, iterable_list):
        assert q(iterable).to_list() == iterable_list

    @pytest.mark.parametrize(Params.sig_iterable, Params.iterable_single())
    def test_toList_hasSingleItem(self, iter_type, iterable, iterable_list):
        assert q(iterable).to_list() == iterable_list

    @pytest.mark.parametrize(Params.sig_iterable, Params.iterable_multi())
    def test_toList_hasMultipleItems(self, iter_type, iterable, iterable_list):
        assert q(iterable).to_list() == iterable_list
