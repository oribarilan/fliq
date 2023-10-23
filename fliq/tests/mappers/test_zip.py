import pytest

from fliq import q
from fliq.tests.fliq_test_utils import Params


class TestZip:
    @pytest.mark.parametrize(Params.sig_iterable, Params.iterable_empty())
    def test_zip_hasNoItems(self, iter_type, iterable, iterable_list):
        assert list(q(iterable).zip(range(5))) == iterable_list

    @pytest.mark.parametrize(Params.sig_iterable, Params.iterable_single())
    def test_zip_hasSingleItem(self, iter_type, iterable, iterable_list):
        if iter_type == "str":
            return
        assert list(q(iterable).zip(range(5))) == [(0, 0)]

    @pytest.mark.parametrize(Params.sig_iterable, Params.iterable_multi())
    def test_zip_hasMultipleItems(self, iter_type, iterable, iterable_list):
        if iter_type == "str":
            return
        assert list(q(iterable).zip(range(5, 10))) == [
            (0, 5),
            (1, 6),
            (2, 7),
            (3, 8),
            (4, 9),
        ]

    @pytest.mark.parametrize(Params.sig_iterable, Params.iterable_multi())
    def test_zip_hasMultipleItems_multipleIterables(self, iter_type, iterable, iterable_list):
        if iter_type == "str":
            return
        assert list(q(iterable).zip(range(5, 10), range(10, 15))) == [
            (0, 5, 10),
            (1, 6, 11),
            (2, 7, 12),
            (3, 8, 13),
            (4, 9, 14),
        ]
