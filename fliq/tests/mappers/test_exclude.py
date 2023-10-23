import pytest

from fliq.tests.fliq_test_utils import Params
from fliq import q


class TestExclude:
    @pytest.mark.parametrize(Params.sig_iterable, Params.iterable_empty())
    def test_exclude_hasNoItems(self,
                                iter_type,
                                iterable,
                                iterable_list):
        assert list(q(iterable).exclude(lambda x: int(x) > 0)) == iterable_list

    @pytest.mark.parametrize(Params.sig_iterable, Params.iterable_single())
    def test_exclude_hasSingleItem(self,
                                   iter_type,
                                   iterable,
                                   iterable_list):
        assert list(q(iterable).exclude(lambda x: int(x) < 1)) == iterable_list[1:]

    @pytest.mark.parametrize(Params.sig_iterable, Params.iterable_multi())
    def test_exclude_hasMultipleItem(self,
                                     iter_type,
                                     iterable,
                                     iterable_list):
        assert list(q(iterable).exclude(lambda x: int(x) < 1)) == iterable_list[1:]
