from unittest.mock import Mock

import pytest

from fliq import q
from fliq.exceptions import NoItemsFoundException
from fliq.tests.fliq_test_utils import Params


class TestFirst:
    # region with default

    @pytest.mark.parametrize(Params.sig_iterable, Params.iterable_empty())
    def test_first_hasNoItems_defaultNotProvided(self,
                                                          iter_type,
                                                          iterable,
                                                          iterable_list):
        assert q(iterable).first(default=None) is None

    @pytest.mark.parametrize(Params.sig_iterable, Params.iterable_empty())
    def test_firstOrDefault_hasNoItems_defaultProvided(self,
                                                       iter_type,
                                                       iterable,
                                                       iterable_list):
        some_obj = Mock()
        assert q(iterable).first(default=some_obj) == some_obj

    @pytest.mark.parametrize(Params.sig_iterable, Params.iterable_single())
    def test_firstOrDefault_hasSingleItem(self, iter_type, iterable, iterable_list):
        assert q(iterable).first(default=None) == iterable_list[0]

    @pytest.mark.parametrize(Params.sig_iterable, Params.iterable_multi())
    def test_firstOrDefault_hasMultipleItems_withoutFilter(self,
                                                           iter_type,
                                                           iterable,
                                                           iterable_list):
        assert q(iterable).first(default=10) == iterable_list[0]

    @pytest.mark.parametrize(Params.sig_iterable, Params.iterable_multi())
    def test_firstOrDefault_hasMultipleItems_withFilter(self,
                                                        iter_type,
                                                        iterable,
                                                        iterable_list):
        assert q(iterable).first(predicate=lambda x: int(x) > 10, default=None) is None

    # endregion

    # region without default

    @pytest.mark.parametrize(Params.sig_iterable, Params.iterable_empty())
    def test_first_missingDefault_hasNoItems(self,
                              iter_type,
                              iterable,
                              iterable_list):
        with pytest.raises(NoItemsFoundException):
            q(iterable).first()

    @pytest.mark.parametrize(Params.sig_iterable, Params.iterable_single())
    def test_first_missingDefault_hasSingleItem(self,
                                 iter_type,
                                 iterable,
                                 iterable_list):
        assert q(iterable).first() == iterable_list[0]

    @pytest.mark.parametrize(Params.sig_iterable, Params.iterable_multi())
    def test_first_missingDefault_hasMultipleItems_withoutFilter(self,
                                                  iter_type,
                                                  iterable,
                                                  iterable_list):
        assert q(iterable).first() == iterable_list[0]

    @pytest.mark.parametrize(Params.sig_iterable, Params.iterable_multi())
    def test_first_missingDefault_hasMultipleItems_withFilter(self,
                                               iter_type,
                                               iterable,
                                               iterable_list):
        assert q(iterable).first(lambda x: int(x) > 0) == iterable_list[1]

    # endregion
