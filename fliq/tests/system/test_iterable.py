import pytest

from fliq.tests.fliq_test_utils import Params
from fliq import q


class TestIterations:
    @pytest.mark.parametrize(Params.sig, Params.iterable_empty())
    def test_forIterable_empty(self, iter_type, iterable):
        iterated = []
        for i in q(iterable):
            iterated.append(int(i))

        assert iterated == []

    @pytest.mark.parametrize(Params.sig, Params.iterable_single())
    def test_forIterable_single(self, iter_type, iterable):
        iterated = []
        for i in q(iterable):
            iterated.append(int(i))

        assert iterated == [0]

    @pytest.mark.parametrize(Params.sig, Params.iterable_multi())
    def test_forIterable_multi(self, iter_type, iterable):
        iterated = []
        for i in q(iterable):
            iterated.append(int(int(i)))

        assert iterated == [0, 1, 2, 3, 4]

    @pytest.mark.parametrize(Params.sig, Params.iterable_empty())
    def test_stdIntegration_empty(self, iter_type, iterable):
        filtered = map(lambda x: int(x), filter(lambda x: int(x) > 2, q(iterable)))
        assert list(filtered) == []

    @pytest.mark.parametrize(Params.sig, Params.iterable_single())
    def test_stdIntegration_single(self, iter_type, iterable):
        filtered = map(lambda x: int(x), filter(lambda x: 2 > int(x), q(iterable)))
        assert list(filtered) == [0]

    @pytest.mark.parametrize(Params.sig, Params.iterable_multi())
    def test_stdIntegration_multi(self, iter_type, iterable):
        filtered = map(lambda x: int(x), filter(lambda x: int(x) > 2, q(iterable)))
        assert list(filtered) == [3, 4]
