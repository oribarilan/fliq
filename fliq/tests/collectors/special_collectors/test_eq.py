import pytest

from fliq import q
from fliq.tests.fliq_test_utils import Params


class TestEq:
    @pytest.mark.parametrize(Params.sig_iterable, Params.iterable_empty())
    def test_eq_hasNoItems(self, iter_type, iterable, iterable_list):
        assert q(iterable) == iterable_list

    def test_eq_otherIsNotIterable_false(self):
        assert not q([0, 1, 2]) == 3

    def test_eq_listQueryToGenerator_equals(self):
        assert q([0, 1, 2]) == (range(3))

    def test_eq_generatorQueryToList_equals(self):
        assert q(range(3)) == [0, 1, 2]

    def test_eq_queryToQuery_equals(self):
        assert q([0, 1, 2]) == q([0, 1, 2])

    def test_eq_listQueryToGenerator_notEquals(self):
        assert q([0, 1, 2]) != (range(2))

    def test_eq_generatorQueryToList_notEquals(self):
        assert q(range(2)) != [0, 1, 2]

    def test_eq_queryToQuery_notEquals(self):
        assert q([0, 2, 1]) != q([0, 1, 2])

    def test_eq_subset_notEquals(self):
        assert q([0, 1]) != q([0, 1, 2])

    @pytest.mark.parametrize(Params.sig_iterable, Params.iterable_multi())
    def test_eq_hasMultipleItems(self, iter_type, iterable, iterable_list):
        assert q(iterable) == iterable_list
