import pytest

from fliq import q
from fliq.exceptions import ElementNotFoundException
from fliq.tests.fliq_test_utils import Params


class TestAt:
    @pytest.mark.parametrize(Params.sig_iterable, Params.iterable_empty())
    def test_at_withDefault_hasNoItems(self, iter_type, iterable, iterable_list):
        assert q(iterable).at(0, default=None) is None

    @pytest.mark.parametrize(Params.sig_iterable, Params.iterable_empty())
    def test_at_withoutDefault_hasNoItems(self, iter_type, iterable, iterable_list):
        with pytest.raises(ElementNotFoundException):
            assert q(iterable).at(0)

    @pytest.mark.parametrize(Params.sig_iterable, Params.iterable_single())
    def test_at_withDefault_hasSingleItem(self, iter_type, iterable, iterable_list):
        assert q(iterable).at(0, default=None) == iterable_list[0]

    @pytest.mark.parametrize(Params.sig_iterable, Params.iterable_single())
    def test_at_withDefault_hasSinlgeItem_indexIsTooBig(self, iter_type, iterable, iterable_list):
        assert q(iterable).at(1, default=None) is None

    @pytest.mark.parametrize(Params.sig_iterable, Params.iterable_empty())
    def test_at_hasNoItems_raisesException(self, iter_type, iterable, iterable_list):
        with pytest.raises(ElementNotFoundException):
            q(iterable).at(0)

    @pytest.mark.parametrize(Params.sig_iterable, Params.iterable_multi())
    def test_at_hasItems_indexTooBig_raisesException(self, iter_type, iterable, iterable_list):
        with pytest.raises(ElementNotFoundException):
            q(iterable).at(6)

    @pytest.mark.parametrize(Params.sig_iterable, Params.iterable_multi())
    def test_at_hasNoItems(self, iter_type, iterable, iterable_list):
        assert q(iterable).at(3) == iterable_list[3]