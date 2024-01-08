import pytest

from fliq import q
from fliq.tests.fliq_test_utils import Params


class TestPairwise:
    @pytest.mark.parametrize(Params.sig_iterable, Params.iterable_empty())
    def test_pairwise_hasNoItems(self, iter_type, iterable, iterable_list):
        assert q(iterable).pairwise().to_list() == []

    @pytest.mark.parametrize(Params.sig_iterable, Params.iterable_single())
    def test_pairwise_hasSingleItem_fillNeeded(self, iter_type, iterable, iterable_list):
        if iter_type == "str":
            return
        assert q(iterable).pairwise() == [(0, None)]

    @pytest.mark.parametrize(Params.sig_iterable, Params.iterable_single())
    def test_pairwise_hasSingleItem_fillNeeded_customPad(self, iter_type, iterable, iterable_list):
        if iter_type == "str":
            return
        assert q(iterable).pairwise(pad=-1) == [(0, -1)]

    @pytest.mark.parametrize(Params.sig_iterable, Params.iterable_multi())
    def test_pairwise_hasMultipleItems_fillNeeded(self, iter_type, iterable, iterable_list):
        if iter_type == "str":
            return
        assert (q(iterable).pairwise().to_list() ==
                [(0, 1), (2, 3), (4, None)])
    def test_pairwise_hasMultipleItems_noFillNeeded(self):
        assert (q([0, 1, 2, 3]).pairwise().to_list() ==
                [(0, 1), (2, 3)])
