import pytest

from fliq import q
from fliq.exceptions import MultipleItemsFoundException
from fliq.tests.fliq_test_utils import Params


class TestSingleOrDefault:
    @pytest.mark.parametrize(Params.sig_iterable, Params.iterable_empty())
    def test_singleOrDefault_hasNoItems(self, iter_type, iterable, iterable_list):
        assert q(iterable).single_or_default() is None

    @pytest.mark.parametrize(Params.sig_iterable, Params.iterable_single())
    def test_singleOrDefault_hasSingleItem(self, iter_type, iterable, iterable_list):
        assert q(iterable).single_or_default() == iterable_list[0]

    @pytest.mark.parametrize(Params.sig_iterable, Params.iterable_multi())
    def test_singleOrDefault_hasMultipleItems(self, iter_type, iterable, iterable_list):
        with pytest.raises(MultipleItemsFoundException):
            q(iterable).single_or_default()