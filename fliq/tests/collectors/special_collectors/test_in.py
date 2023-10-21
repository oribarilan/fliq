import pytest

from fliq import q
from fliq.tests.fliq_test_utils import Params


class TestIn:
    @pytest.mark.parametrize(Params.sig_iterable, Params.iterable_empty())
    def test_in_hasNoItems(self, iter_type, iterable, iterable_list):
        if iter_type == 'str':
            assert '0' not in q(iterable)
        else:
            assert 0 not in q(iterable)

    def test_contains_hasSingleItem_itemIsContained(self):
        assert 0 in q([0])

    def test_contains_hasSingleItem_itemIsNotContained(self):
        assert 1 not in q([0])

    def test_contains_hasSingleNoneItem_nonesContained(self):
        assert None in q([None])

    @pytest.mark.parametrize(Params.sig_iterable, Params.iterable_multi())
    def test_contains_hasMultipleItems(self, iter_type, iterable, iterable_list):
        if iter_type == 'str':
            assert '3' in q(iterable)
        else:
            assert 3 in q(iterable)
