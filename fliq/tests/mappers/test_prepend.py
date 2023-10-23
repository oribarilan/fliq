import pytest

from fliq import q
from fliq.tests.fliq_test_utils import Params


class TestPrepend:
    @pytest.mark.parametrize(Params.sig_iterable, Params.iterable_empty())
    def test_prepend_hasNoItems(self,
                                iter_type,
                                iterable,
                                iterable_list):
        assert list(q(iterable).prepend(5)) == [5]

    @pytest.mark.parametrize(Params.sig_iterable, Params.iterable_single())
    def test_prepend_hasSingleItem(self,
                                   iter_type,
                                   iterable,
                                   iterable_list):
        assert list(q(iterable).prepend(1)) == [1] + iterable_list

    @pytest.mark.parametrize(Params.sig_iterable, Params.iterable_multi())
    def test_prepend_hasMultipleItems(self,
                                      iter_type,
                                      iterable,
                                      iterable_list):
        assert list(q(iterable).prepend(5)) == [5] + iterable_list

    @pytest.mark.parametrize(Params.sig_iterable, Params.iterable_multi())
    def test_prepend_hasMultipleItems_addingMultipleItems(self,
                                                          iter_type,
                                                          iterable,
                                                          iterable_list):
        assert list(q(iterable).prepend(1, 2, 3, 4)) == [1, 2, 3, 4] + iterable_list

    @pytest.mark.parametrize(Params.sig_iterable, Params.iterable_multi())
    def test_prepend_hasMultipleItems_addingSingleItemThatIsList(self,
                                                                 iter_type,
                                                                 iterable,
                                                                 iterable_list):
        assert list(q(iterable).prepend([1, 2, 3])) == [[1, 2, 3]] + iterable_list
