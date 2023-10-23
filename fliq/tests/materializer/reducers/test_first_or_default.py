from unittest.mock import Mock

import pytest

from fliq import q
from fliq.tests.fliq_test_utils import Params


class TestFirstOrDefault:
    @pytest.mark.parametrize(Params.sig_iterable, Params.iterable_empty())
    def test_firstOrDefault_hasNoItems_defaultNotProvided(self,
                                                          iter_type,
                                                          iterable,
                                                          iterable_list):
        assert q(iterable).first_or_default() is None

    @pytest.mark.parametrize(Params.sig_iterable, Params.iterable_empty())
    def test_firstOrDefault_hasNoItems_defaultProvided(self,
                                                       iter_type,
                                                       iterable,
                                                       iterable_list):
        some_obj = Mock()
        assert q(iterable).first_or_default(default=some_obj) == some_obj

    @pytest.mark.parametrize(Params.sig_iterable, Params.iterable_single())
    def test_firstOrDefault_hasSingleItem(self, iter_type, iterable, iterable_list):
        assert q(iterable).first_or_default() == iterable_list[0]

    @pytest.mark.parametrize(Params.sig_iterable, Params.iterable_multi())
    def test_firstOrDefault_hasMultipleItems_withoutFilter(self,
                                                           iter_type,
                                                           iterable,
                                                           iterable_list):
        assert q(iterable).first_or_default(default=10) == iterable_list[0]

    @pytest.mark.parametrize(Params.sig_iterable, Params.iterable_multi())
    def test_firstOrDefault_hasMultipleItems_withFilter(self,
                                                        iter_type,
                                                        iterable,
                                                        iterable_list):
        assert q(iterable).first_or_default(predicate=lambda x: int(x) > 10) is None
