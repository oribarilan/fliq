import pytest

from fliq import q
from fliq.tests.fliq_test_utils import Params


class TestSlide:
    @pytest.mark.parametrize(Params.sig_iterable, Params.iterable_empty())
    def test_slide_hasNoItems(self, iter_type, iterable, iterable_list):
        assert q(iterable).slide(window=2, overlap=1).to_list() == []

    @pytest.mark.parametrize(Params.sig_iterable, Params.iterable_single())
    def test_slide_hasSingleItem_fillNeeded(self, iter_type, iterable, iterable_list):
        if iter_type == "str":
            return
        assert q(iterable).slide(window=2, overlap=1, pad=None) == [(0, None)]

    @pytest.mark.parametrize(Params.sig_iterable, Params.iterable_single())
    def test_slide_hasSingleItem_multiFillNeeded(self, iter_type, iterable, iterable_list):
        if iter_type == "str":
            return
        assert q(iterable).slide(window=3, overlap=1, pad=None) == [(0, None, None)]

    @pytest.mark.parametrize(Params.sig_iterable, Params.iterable_multi())
    def test_slide_hasMultipleItems_noFillNeeded(self, iter_type, iterable, iterable_list):
        if iter_type == "str":
            return
        assert (q(iterable).slide(window=2, overlap=1).to_list() ==
                [(0, 1), (1, 2), (2, 3), (3, 4)])

    @pytest.mark.parametrize(Params.sig_iterable, Params.iterable_multi())
    def test_slide_hasMultipleItems_fillNeeded(self, iter_type, iterable, iterable_list):
        if iter_type == "str":
            return
        assert (q(iterable).slide(window=4, overlap=2).to_list() ==
                [(0, 1, 2, 3), (2, 3, 4, None)])

    @pytest.mark.parametrize(Params.sig_iterable, Params.iterable_multi())
    def test_slide_hasMultipleItems_fillNeededCustom(self, iter_type, iterable, iterable_list):
        if iter_type == "str":
            return
        assert (q(iterable).slide(window=4, overlap=2, pad=-1).to_list() ==
                [(0, 1, 2, 3), (2, 3, 4, -1)])

    def test_slide_hasMultipleItems_fillNotRequired(self):
        assert (q([0,1,2,3]).slide(window=2, overlap=1).to_list() == [(0, 1), (1, 2), (2, 3)])

    def test_slide_hasMultipleItems_fillRequired(self):
        assert (q([0,1,2,3]).slide(window=3, overlap=1).to_list() == [(0, 1, 2), (2, 3, None)])