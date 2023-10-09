import pytest

from fliq import q
from fliq.exceptions import NoItemsFoundException, MultipleItemsFoundException
from fliq.tests.fliq_test_utils import Params


class TestCollectorGet:
    @pytest.mark.parametrize(Params.sig_iterable, Params.iterable_empty())
    def test_get_hasNoItems(self, iter_type, iterable, iterable_list):
        with pytest.raises(NoItemsFoundException):
            q(iterable).get()

    @pytest.mark.parametrize(Params.sig_iterable, Params.iterable_single())
    def test_get_hasSingleItem(self, iter_type, iterable, iterable_list):
        assert q(iterable).get() == iterable_list[0]

    @pytest.mark.parametrize(Params.sig_iterable, Params.iterable_multi())
    def test_get_hasMultipleItems(self, iter_type, iterable, iterable_list):
        with pytest.raises(MultipleItemsFoundException):
            q(iterable).get()
