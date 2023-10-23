import pytest

from fliq import q
from fliq.tests.fliq_test_utils import Params


class TestAggregate:
    @pytest.mark.parametrize(Params.sig_iterable, Params.iterable_empty())
    def test_aggregate_hasNoItems_customInitial(self, iter_type, iterable, iterable_list):
        assert q(iterable).aggregate(by=lambda x, y: x+y, initial=0) == 0

    @pytest.mark.parametrize(Params.sig_iterable, Params.iterable_empty())
    def test_aggregate_hasNoItems_noInitial_errorRaised(self, iter_type, iterable, iterable_list):
        with pytest.raises(TypeError):
            q(iterable).aggregate(by=lambda x, y: x+y)

    @pytest.mark.parametrize(Params.sig_iterable, Params.iterable_single())
    def test_aggregate_hasSingleItem_noInitial(self, iter_type, iterable, iterable_list):
        assert q(iterable).aggregate(by=lambda x, y: x+y) == iterable_list[0]

    @pytest.mark.parametrize(Params.sig_iterable, Params.iterable_multi())
    def test_aggregate_hasMultipleItems(self, iter_type, iterable, iterable_list):
        if iter_type == 'str':
            assert q(iterable).aggregate(by=lambda x, y: x+y) == ''.join(iterable_list)
        else:
            assert q(iterable).aggregate(by=lambda x, y: x+y) == sum(iterable_list)
