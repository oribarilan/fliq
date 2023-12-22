import pytest

from fliq import q
from fliq.tests.fliq_test_utils import Params


class TestRepr:
    @pytest.mark.parametrize(Params.sig_iterable, Params.iterable_empty())
    def test_repr_empty(self, iter_type, iterable, iterable_list):
        r = repr(q(iterable))
        assert r == "Query([])"

    @pytest.mark.parametrize(Params.sig_iterable, Params.iterable_single())
    def test_repr_single(self, iter_type, iterable, iterable_list):
        if iter_type == 'str':
            return
        r = repr(q(iterable))
        assert r == "Query([0])"

    @pytest.mark.parametrize(Params.sig_iterable, Params.iterable_multi())
    def test_repr_multiple(self, iter_type, iterable, iterable_list):
        if iter_type == 'str':
            return
        r = repr(q(iterable))
        assert r == "Query([0, 1, 2, 3, 4])"

    def test_repr_biggerThanMaxRepresentation(self):
        r = repr(q(range(100)))
        assert (r == "Query([0, 1, 2, 3, 4, 5, 6, 7, 8, 9, ...])")
