import pytest

from fliq import q
from fliq.tests.fliq_test_utils import Params


class TestContains:
    @pytest.mark.parametrize(Params.sig_iterable, Params.iterable_empty())
    def test_contains_hasNoItems(self, iter_type, iterable, iterable_list):
        if iter_type == 'str':
            assert not q(iterable).contains('0')
        else:
            assert not q(iterable).contains(0)

    def test_contains_hasSingleItem_itemIsContained(self):
        assert q([0]).contains(0)

    def test_contains_hasSingleItem_itemIsNotContained(self):
        assert not q([0]).contains(1)

    def test_contains_hasSingleNoneItem_nonesContained(self):
        assert q([None]).contains(None)

    @pytest.mark.parametrize(Params.sig_iterable, Params.iterable_multi())
    def test_contains_hasMultipleItems(self, iter_type, iterable, iterable_list):
        if iter_type == 'str':
            assert q(iterable).contains('3')
        else:
            assert q(iterable).contains(3)
