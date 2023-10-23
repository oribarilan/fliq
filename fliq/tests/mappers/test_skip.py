import pytest

from fliq import q
from fliq.tests.fliq_test_utils import Params


class TestSkip:
    @pytest.mark.parametrize(Params.sig_iterable, Params.iterable_empty())
    def test_skip_hasNoItems(self,
                             iter_type,
                             iterable,
                             iterable_list):
        assert list(q(iterable).skip(n=5)) == iterable_list

    @pytest.mark.parametrize(Params.sig_iterable, Params.iterable_single())
    def test_skip_hasSingleItem_takeBiggerThanIterableSize(self,
                                                           iter_type,
                                                           iterable,
                                                           iterable_list):
        assert list(q(iterable).skip(n=5)) == []

    @pytest.mark.parametrize(Params.sig_iterable, Params.iterable_multi())
    def test_take_hasMultipleItems(self,
                                   iter_type,
                                   iterable,
                                   iterable_list):
        assert list(q(iterable).skip(n=3)) == iterable_list[3:]
