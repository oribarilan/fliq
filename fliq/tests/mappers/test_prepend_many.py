import pytest

from fliq import q
from fliq.tests.fliq_test_utils import Params


class TestPrependMany:
    @pytest.mark.parametrize(Params.sig_iterable, Params.iterable_empty())
    def test_prependMany_hasNoItems(self,
                                    iter_type,
                                    iterable,
                                    iterable_list):
        assert list(q(iterable).prepend_many([5])) == [5]

    @pytest.mark.parametrize(Params.sig_iterable, Params.iterable_single())
    def test_prependMany_hasSingleItem(self,
                                       iter_type,
                                       iterable,
                                       iterable_list):
        assert list(q(iterable).prepend_many([1, 2, 3])) == [1, 2, 3] + iterable_list

    @pytest.mark.parametrize(Params.sig_iterable, Params.iterable_multi())
    def test_prependMany_hasMultipleItems(self,
                                          iter_type,
                                          iterable,
                                          iterable_list):
        assert list(q(iterable).prepend_many([5, 6, 7])) == [5, 6, 7] + iterable_list
