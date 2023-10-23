import pytest

from fliq import q
from fliq.tests.fliq_test_utils import Params


class TestOrderBy:
    @pytest.mark.parametrize(Params.sig_iterable, Params.iterable_empty())
    def test_orderBy_hasNoItems(self,
                                iter_type,
                                iterable,
                                iterable_list):
        assert list(q(iterable).order()) == iterable_list

    @pytest.mark.parametrize(Params.sig_iterable, Params.iterable_single())
    def test_orderBy_hasSingleItem(self,
                                   iter_type,
                                   iterable,
                                   iterable_list):
        assert list(q(iterable).order()) == iterable_list

    @pytest.mark.parametrize(Params.sig_iterable, Params.iterable_multi())
    def test_orderBy_hasMultipleItems_defaultSorting(self,
                                                     iter_type,
                                                     iterable,
                                                     iterable_list):
        assert list(q(iterable).order()) == list(iterable_list)

    @pytest.mark.parametrize(Params.sig_iterable, Params.iterable_multi())
    def test_orderBy_hasMultipleItems_customSelector(self,
                                                     iter_type,
                                                     iterable,
                                                     iterable_list):
        expected = list(sorted(iterable_list, key=lambda x: (int(x) % 2)))
        actual = list(q(iterable).order(by=lambda x: (int(x) % 2)))
        assert actual == expected
