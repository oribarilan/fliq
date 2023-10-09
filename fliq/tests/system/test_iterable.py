import pytest

from fliq.tests.fliq_test_utils import Params
from fliq import q


class TestIterations:
    @pytest.mark.parametrize(Params.sig_iterable, Params.iterable_empty())
    def test_forIterable_empty(self, iter_type, iterable, iterable_list):
        iterated = []
        for i in q(iterable):
            iterated.append(i)

        assert iterated == iterable_list

    @pytest.mark.parametrize(Params.sig_iterable, Params.iterable_single())
    def test_forIterable_single(self, iter_type, iterable, iterable_list):
        iterated = []
        for i in q(iterable):
            iterated.append(i)

        assert iterated == iterable_list

    @pytest.mark.parametrize(Params.sig_iterable, Params.iterable_multi())
    def test_forIterable_multi(self, iter_type, iterable, iterable_list):
        iterated = []
        for i in q(iterable):
            iterated.append(i)

        assert iterated == iterable_list

    @pytest.mark.parametrize(Params.sig_iterable, Params.iterable_empty())
    def test_stdIntegration_empty(self, iter_type, iterable, iterable_list):
        filtered = filter(lambda x: int(x) > 2, q(iterable))
        assert list(filtered) == iterable_list

    @pytest.mark.parametrize(Params.sig_iterable, Params.iterable_single())
    def test_stdIntegration_single(self, iter_type, iterable, iterable_list):
        filtered = filter(lambda x: 2 > int(x), q(iterable))
        assert list(filtered) == iterable_list

    @pytest.mark.parametrize(Params.sig_iterable, Params.iterable_multi())
    def test_stdIntegration_multi(self, iter_type, iterable, iterable_list):
        filtered = filter(lambda x: int(x) > 2, q(iterable))
        assert list(filtered) == list(filter(lambda x: int(x) > 2, iterable_list))
