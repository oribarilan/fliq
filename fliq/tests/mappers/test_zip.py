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

    def test_zip_longest(self):
        iterable = [1, 2, 3]
        assert list(q(iterable).zip([4, 5], [6], longest=True)) == [
            (1, 4, 6),
            (2, 5, None),
            (3, None, None),
        ]

    def test_zip_longestWithFillValue(self):
        iterable = [1, 2, 3]
        fill_value = -1
        assert list(q(iterable).zip([4, 5], [6], longest=True, fillvalue=fill_value)) == [
            (1, 4, 6),
            (2, 5, -1),
            (3, -1, -1),
        ]

    def test_zip_shortestWithDifferentLengths(self):
        query = q(range(5))
        zipped = query.zip(range(3))
        assert list(zipped) == [(0, 0), (1, 1), (2, 2)]
