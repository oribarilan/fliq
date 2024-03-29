import pytest

from fliq import q
from fliq.tests.fliq_test_utils import Params


class TestDistinct:
    @pytest.mark.parametrize(Params.sig_iterable, Params.iterable_empty())
    def test_distinct_hasNoItems(self,
                                 iter_type,
                                 iterable,
                                 iterable_list):
        assert list(q(iterable).distinct()) == iterable_list

    @pytest.mark.parametrize(Params.sig_iterable, Params.iterable_single())
    def test_distinct_hasSingleItem(self,
                                   iter_type,
                                   iterable,
                                   iterable_list):
        assert list(q(iterable).distinct()) == iterable_list

    @pytest.mark.parametrize(Params.sig_iterable, Params.iterable_multi())
    def test_distinct_hasMultipleItemsWithoutDups(self,
                                                 iter_type,
                                                 iterable,
                                                 iterable_list):
        assert list(q(iterable).distinct()) == list(iterable_list)

    @pytest.mark.parametrize(Params.sig_iterable, Params.iterable_multi_dup())
    def test_distinct_hasMultipleItemsWithDups_preserveOrder(self,
                                                            iter_type,
                                                            iterable,
                                                            iterable_list):
        assert list(q(iterable).distinct()) == sorted(list(set(iterable_list)))

