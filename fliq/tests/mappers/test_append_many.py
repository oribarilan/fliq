import pytest

from fliq import q
from fliq.tests.fliq_test_utils import Params


class TestAppendMany:
    @pytest.mark.parametrize(Params.sig_iterable, Params.iterable_empty())
    def test_appendMany_hasNoItems(self,
                                   iter_type,
                                   iterable,
                                   iterable_list):
        assert list(q(iterable).append_many([1, 2, 3])) == [1, 2, 3]

    @pytest.mark.parametrize(Params.sig_iterable, Params.iterable_single())
    def test_appendMany_hasSingleItem(self,
                                      iter_type,
                                      iterable,
                                      iterable_list):
        assert list(q(iterable).append_many([1, 2, 3])) == iterable_list + [1, 2, 3]

    @pytest.mark.parametrize(Params.sig_iterable, Params.iterable_multi())
    def test_appendMany_hasMultipleItems(self,
                                         iter_type,
                                         iterable,
                                         iterable_list):
        assert list(q(iterable).append_many([5, 6, 7])) == iterable_list + [5, 6, 7]
