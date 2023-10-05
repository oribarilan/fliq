import pytest

from fliq import q
from fliq.exceptions import NoItemsFoundException
from fliq.tests.fliq_test_utils import Params


class TestCollectorFirst:
    @pytest.mark.parametrize(Params.sig, Params.iterable_empty())
    def test_first_hasNoItems(self, iter_type, iterable):
        with pytest.raises(NoItemsFoundException):
            q(iterable).first()

    @pytest.mark.parametrize(Params.sig, Params.iterable_single())
    def test_first_hasSingleItem(self, iter_type, iterable):
        assert int(q(iterable).first()) == 0

    @pytest.mark.parametrize(Params.sig, Params.iterable_multi())
    def test_first_hasMultipleItems_withoutFilter(self, iter_type, iterable):
        assert int(q(iterable).first()) == 0

    @pytest.mark.parametrize(Params.sig, Params.iterable_multi())
    def test_first_hasMultipleItems_withFilter(self, iter_type, iterable):
        assert int(q(iterable).first(lambda x: int(x) > 0)) == 1
