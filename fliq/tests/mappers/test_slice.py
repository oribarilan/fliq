import pytest

from fliq import q
from fliq.tests.fliq_test_utils import Params


class TestSlice:
    # start
    @pytest.mark.parametrize(Params.sig_iterable, Params.iterable_empty())
    def test_skip_empty_start(self, iter_type, iterable, iterable_list):
        assert list(q(iterable).slice(start=2)) == iterable_list

    @pytest.mark.parametrize(Params.sig_iterable, Params.iterable_single())
    def test_skip_hasSingleItem_start(self, iter_type, iterable, iterable_list):
        assert list(q(iterable).slice(start=2)) == []

    @pytest.mark.parametrize(Params.sig_iterable, Params.iterable_multi())
    def test_skip_hasMultipleItems_start(self, iter_type, iterable, iterable_list):
        assert list(q(iterable).slice(start=2)) == iterable_list[2:]

    # stop
    @pytest.mark.parametrize(Params.sig_iterable, Params.iterable_empty())
    def test_skip_empty_stop(self, iter_type, iterable, iterable_list):
        assert list(q(iterable).slice(stop=2)) == iterable_list

    @pytest.mark.parametrize(Params.sig_iterable, Params.iterable_single())
    def test_skip_hasSingleItem_stop(self, iter_type, iterable, iterable_list):
        assert list(q(iterable).slice(stop=1)) == iterable_list

    @pytest.mark.parametrize(Params.sig_iterable, Params.iterable_multi())
    def test_skip_hasMultipleItems_stop(self, iter_type, iterable, iterable_list):
        assert list(q(iterable).slice(stop=2)) == iterable_list[:2]

    # step
    @pytest.mark.parametrize(Params.sig_iterable, Params.iterable_empty())
    def test_skip_empty_step(self, iter_type, iterable, iterable_list):
        assert list(q(iterable).slice(step=2)) == iterable_list

    @pytest.mark.parametrize(Params.sig_iterable, Params.iterable_single())
    def test_skip_hasSingleItem_step(self, iter_type, iterable, iterable_list):
        assert list(q(iterable).slice(step=1)) == iterable_list

    @pytest.mark.parametrize(Params.sig_iterable, Params.iterable_multi())
    def test_skip_hasMultipleItems_step(self, iter_type, iterable, iterable_list):
        assert list(q(iterable).slice(step=2)) == iterable_list[::2]

    # start, stop, step
    def test_skip_hasMultipleItems_startStopStep(self):
        assert list(q(range(10)).slice(start=1, stop=6, step=2)) == [1, 3, 5]