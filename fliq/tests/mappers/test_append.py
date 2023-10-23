import pytest

from fliq import q
from fliq.tests.fliq_test_utils import Params


class TestAppend:
    @pytest.mark.parametrize(Params.sig_iterable, Params.iterable_empty())
    def test_append_hasNoItems(self,
                               iter_type,
                               iterable,
                               iterable_list):
        assert list(q(iterable).append(5)) == [5]

    @pytest.mark.parametrize(Params.sig_iterable, Params.iterable_single())
    def test_append_hasSingleItem(self,
                                  iter_type,
                                  iterable,
                                  iterable_list):
        assert list(q(iterable).append(1)) == iterable_list + [1]

    @pytest.mark.parametrize(Params.sig_iterable, Params.iterable_multi())
    def test_append_hasMultipleItems(self,
                                     iter_type,
                                     iterable,
                                     iterable_list):
        assert list(q(iterable).append(5)) == iterable_list + [5]

    @pytest.mark.parametrize(Params.sig_iterable, Params.iterable_multi())
    def test_append_hasMultipleItems_addingMultipleItems(self,
                                                       iter_type,
                                                       iterable,
                                                       iterable_list):
        assert list(q(iterable).append(1, 2, 3, 4)) == iterable_list + [1, 2, 3, 4]

    @pytest.mark.parametrize(Params.sig_iterable, Params.iterable_multi())
    def test_append_hasMultipleItems_addingSingleItemThatIsList(self,
                                                              iter_type,
                                                              iterable,
                                                              iterable_list):
        assert list(q(iterable).append([1, 2, 3])) == iterable_list + [[1, 2, 3]]
