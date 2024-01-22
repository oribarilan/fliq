from unittest.mock import Mock

import pytest

from fliq import q
from fliq.utils import Point
from fliq.tests.fliq_test_utils import Params


class TestBinarySearch:
    @pytest.mark.parametrize(Params.sig_iterable, Params.iterable_empty())
    def test_binarySearch_hasNoItems_defaultProvided(self,
                                                     iter_type,
                                                     iterable,
                                                     iterable_list):
        some_obj = Mock()
        assert q(iterable).binary_search(1, default=some_obj) == some_obj

    @pytest.mark.parametrize(Params.sig_iterable, Params.iterable_single())
    def test_binarySearch_hasSingleItem(self, iter_type, iterable, iterable_list):
        if iter_type == 'str':
            return
        assert q(iterable).binary_search(0, default=1) == 0

    @pytest.mark.parametrize(Params.sig_iterable, Params.iterable_multi())
    def test_binarySearch_hasMultipleItems(self,
                                           iter_type,
                                           iterable,
                                           iterable_list):
        if iter_type == 'str':
            return
        assert q(iterable).binary_search(3, default=10) == 3

    def test_binarySearch_hasMultipleItems_complexObject(self):
        items = [Point(0, 0), Point(1, 1), Point(2, 2), Point(3, 3), Point(4, 4)]
        assert q(items).binary_search(2, key=lambda p: p.x) == items[2]
