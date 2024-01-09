import pytest

from fliq import q
from fliq.exceptions import NotEnoughElementsException
from fliq.tests.fliq_test_utils import Params


class TestMostCommon:
    @pytest.mark.parametrize(Params.sig_iterable, Params.iterable_empty())
    def test_mostCommon_hasNoItems_singleMostCommonRequested(self,
                                                             iter_type,
                                                             iterable,
                                                             iterable_list):
        with pytest.raises(NotEnoughElementsException):
            q(iterable).most_common()

    @pytest.mark.parametrize(Params.sig_iterable, Params.iterable_empty())
    def test_mostCommon_hasNoItems_multiMostCommonRequests(self,
                                                           iter_type,
                                                           iterable,
                                                           iterable_list):
        with pytest.raises(NotEnoughElementsException):
            q(iterable).most_common(n=2)

    @pytest.mark.parametrize(Params.sig_iterable, Params.iterable_single())
    def test_mostCommon_hasSingleItem_singleRequested(self,
                                                      iter_type,
                                                      iterable,
                                                      iterable_list):
        assert q(iterable).most_common() == iterable_list

    @pytest.mark.parametrize(Params.sig_iterable, Params.iterable_single())
    def test_mostCommon_hasSingleItem_multiRequested(self,
                                                     iter_type,
                                                     iterable,
                                                     iterable_list):
        with pytest.raises(NotEnoughElementsException):
            q(iterable).most_common(n=2)

    @pytest.mark.parametrize(Params.sig_iterable, Params.iterable_multi())
    def test_mostCommon_hasMultipleItems_multiRequested(self,
                                                        iter_type,
                                                        iterable,
                                                        iterable_list):
        a, b, c = q(iterable).most_common(n=3).to_list()
        # not testing for sorting, they all appear once
        assert a in iterable_list
        assert b in iterable_list
        assert c in iterable_list

    def test_mostCommon_returnedByFrequencyDesc(self):
        a, b, c = q([1, 2, 2, 3, 3, 3]).most_common(n=3).to_list()
        assert a == 3
        assert b == 2
        assert c == 1
