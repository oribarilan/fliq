import pytest

from fliq import q
from fliq.tests.fliq_test_utils import Params


class TestEquals:
    @pytest.mark.parametrize(Params.sig_iterable, Params.iterable_empty())
    def test_equals_hasNoItems(self, iter_type, iterable, iterable_list):
        assert q(iterable).equals(iterable_list)

    def test_equals_listQueryToGenerator_equals(self):
        assert q([0, 1, 2]).equals(range(3))

    def test_equals_generatorQueryToList_equals(self):
        assert q(range(3)).equals([0, 1, 2])

    def test_equals_queryToQuery_equals(self):
        assert q([0, 1, 2]).equals(q([0, 1, 2]))

    def test_eq_listQueryToGenerator_notEquals(self):
        assert not q([0, 1, 2]).equals(range(2))

    def test_eq_generatorQueryToList_notEquals(self):
        assert not q(range(2)).equals([0, 1, 2])

    def test_eq_queryToQuery_notEquals(self):
        assert not q([0, 2, 1]).equals(q([0, 1, 2]))

    def test_eq_bagCompare(self):
        assert q([0, 2, 1]).equals(q([0, 1, 2]), bag_compare=True)

    def test_eq_bagCompareWithDuplicates(self):
        assert q([0, 2, 1]).equals(q([0, 1, 2, 1]), bag_compare=True)

    def test_eq_subset_notEquals(self):
        assert not q([0, 1]).equals(q([0, 1, 2]))

    @pytest.mark.parametrize(Params.sig_iterable, Params.iterable_multi())
    def test_eq_hasMultipleItems(self, iter_type, iterable, iterable_list):
        assert q(iterable).equals(iterable_list)
