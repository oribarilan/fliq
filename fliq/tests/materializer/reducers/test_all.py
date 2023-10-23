import pytest

from fliq import q
from fliq.tests.fliq_test_utils import Params


class TestAll:
    @pytest.mark.parametrize(Params.sig_iterable, Params.iterable_empty())
    def test_all_hasNoItems(self, iter_type, iterable, iterable_list):
        assert q(iterable).all()

    def test_all_hasSingleItem_integer(self):
        assert q([1]).all()

    def test_all_hasSingleItem_nones(self):
        assert not q([None]).all()

    def test_all_hasMultipleItems(self):
        assert q((1, 2, 3, True)).all()
