import pytest

from fliq import q
from fliq.exceptions import NoItemsFoundException
from fliq.tests.fliq_test_utils import Params


class TestFirst:
    @pytest.mark.parametrize(Params.sig_iterable, Params.iterable_empty())
    def test_first_hasNoItems(self,
                              iter_type,
                              iterable,
                              iterable_list):
        with pytest.raises(NoItemsFoundException):
            q(iterable).first()

    @pytest.mark.parametrize(Params.sig_iterable, Params.iterable_single())
    def test_first_hasSingleItem(self,
                                 iter_type,
                                 iterable,
                                 iterable_list):
        assert q(iterable).first() == iterable_list[0]

    @pytest.mark.parametrize(Params.sig_iterable, Params.iterable_multi())
    def test_first_hasMultipleItems_withoutFilter(self,
                                                  iter_type,
                                                  iterable,
                                                  iterable_list):
        assert q(iterable).first() == iterable_list[0]

    @pytest.mark.parametrize(Params.sig_iterable, Params.iterable_multi())
    def test_first_hasMultipleItems_withFilter(self,
                                               iter_type,
                                               iterable,
                                               iterable_list):
        assert q(iterable).first(lambda x: int(x) > 0) == iterable_list[1]
