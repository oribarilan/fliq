from unittest.mock import Mock

import pytest

from fliq import q
from fliq.exceptions import NoItemsFoundException
from fliq.tests.fliq_test_utils import Params


class TestCollectorFirstOrDefault:
    @pytest.mark.parametrize(Params.sig, Params.iterable_empty())
    def test_first_hasNoItems_defaultNotProvided(self, iter_type, iterable):
        assert q(iterable).first_or_default() is None

    @pytest.mark.parametrize(Params.sig, Params.iterable_empty())
    def test_first_hasNoItems_defaultProvided(self, iter_type, iterable):
        some_obj = Mock()
        assert q(iterable).first_or_default(default=some_obj) == some_obj

    @pytest.mark.parametrize(Params.sig, Params.iterable_single())
    def test_first_hasSingleItem(self, iter_type, iterable):
        assert int(q(iterable).first_or_default()) == 0

    @pytest.mark.parametrize(Params.sig, Params.iterable_multi())
    def test_first_hasMultipleItems_withoutFilter(self, iter_type, iterable):
        assert int(q(iterable).first_or_default(default=10)) == 0

    @pytest.mark.parametrize(Params.sig, Params.iterable_multi())
    def test_first_hasMultipleItems_withFilter(self, iter_type, iterable):
        assert q(iterable).first_or_default(lambda x: int(x) > 10) is None
