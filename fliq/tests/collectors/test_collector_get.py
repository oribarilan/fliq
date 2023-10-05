from unittest import TestCase

import pytest

from fliq import q
from parameterized import parameterized

from fliq.exceptions import NoItemsFoundException, MultipleItemsFoundException
from fliq.tests.fliq_test_utils import FliqTestUtils


class TestCollectorGet:
    @pytest.mark.parametrize("iter_type,iterable", FliqTestUtils.iterable_parameters_empty)
    def test_get_hasNoItems(self, iter_type, iterable):
        with pytest.raises(NoItemsFoundException):
            q(iterable).get()

    @pytest.mark.parametrize("iter_type,iterable", FliqTestUtils.iterable_parameters_single)
    def test_get_hasSingleItem(self, iter_type, iterable):
        assert int(q(iterable).get()) == 0

    @pytest.mark.parametrize("iter_type,iterable", FliqTestUtils.iterable_parameters_multi)
    def test_get_hasMultipleItems(self, iter_type, iterable):
        with pytest.raises(MultipleItemsFoundException):
            q(iterable).get()
