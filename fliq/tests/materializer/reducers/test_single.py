import pytest

from fliq import q
from fliq.exceptions import MultipleElementsFoundException, QueryIsUnexpectedlyEmptyException
from fliq.tests.fliq_test_utils import Params


class TestSingle:
    @pytest.mark.parametrize(Params.sig_iterable, Params.iterable_empty())
    def test_single_withDefault_hasNoItems(self, iter_type, iterable, iterable_list):
        assert q(iterable).single(default=None) is None

    @pytest.mark.parametrize(Params.sig_iterable, Params.iterable_single())
    def test_single_withDefault_hasSingleItem(self, iter_type, iterable, iterable_list):
        assert q(iterable).single(default=None) == iterable_list[0]

    @pytest.mark.parametrize(Params.sig_iterable, Params.iterable_multi())
    def test_single_withDefault_hasMultipleItems(self, iter_type, iterable, iterable_list):
        with pytest.raises(MultipleElementsFoundException):
            q(iterable).single(default=None)

    @pytest.mark.parametrize(Params.sig_iterable, Params.iterable_empty())
    def test_single_hasNoItems(self, iter_type, iterable, iterable_list):
        with pytest.raises(QueryIsUnexpectedlyEmptyException):
            q(iterable).single()

    @pytest.mark.parametrize(Params.sig_iterable, Params.iterable_single())
    def test_single_hasSingleItem(self, iter_type, iterable, iterable_list):
        assert q(iterable).single() == iterable_list[0]

    @pytest.mark.parametrize(Params.sig_iterable, Params.iterable_multi())
    def test_single_hasMultipleItems(self, iter_type, iterable, iterable_list):
        with pytest.raises(MultipleElementsFoundException):
            q(iterable).single()