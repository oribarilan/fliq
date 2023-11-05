import pytest

from fliq import q
from fliq.tests.fliq_test_utils import Params


class TestFlatten:
    @pytest.mark.parametrize(Params.sig_iterable, Params.iterable_empty())
    def test_flatten_hasNoItems(self,
                                iter_type,
                                iterable,
                                iterable_list):
        assert q(iterable).flatten() == iterable_list

    @pytest.mark.parametrize(Params.sig_iterable, Params.iterable_single())
    def test_flatten_hasSingleItem(self,
                                   iter_type,
                                   iterable,
                                   iterable_list):
        assert q(iterable).flatten() == iterable_list

    @pytest.mark.parametrize(Params.sig_iterable, Params.iterable_multi())
    def test_flatten_hasMultipleItems(self,
                                      iter_type,
                                      iterable,
                                      iterable_list):
        assert q(iterable).flatten() == iterable_list

    def test_flatten_nestedTwoLevels_unlimited(self):
        assert q([[1, 2], [3, 4]]).flatten() == [1, 2, 3, 4]

    def test_flatten_nestedThreeLevels_unlimited(self):
        assert q([[[1, 2]], [[3, 4]]]).flatten() == [1, 2, 3, 4]

    def test_flatten_nestedTwoLevels_limited(self):
        assert q([[1, 2], [3, 4]]).flatten(max_depth=2) == [1, 2, 3, 4]

    def test_flatten_nestedThreeLevels_limited(self):
        assert q([[[1, 2]], [[3, 4]]]).flatten(max_depth=1).to_list() == [[1, 2], [3, 4]]

    def test_flatten_nestedThreeLevels_limitedMoreThanExists(self):
        assert q([[[1, 2]], [[3, 4]]]).flatten(max_depth=10) == [1, 2, 3, 4]

    def test_flatten_nestedString_ignoredByDefault(self):
        assert q([['hello'], 'world']).flatten(max_depth=3) == ['hello', 'world']

    def test_flatten_nestedString_notIgnoredWithLimited(self):
        assert (q([['hello'], 'world']).flatten(max_depth=2, ignore_types=None).to_list() ==
                ['h', 'e', 'l', 'l', 'o', 'w', 'o', 'r', 'l', 'd'])

    def test_flatten_nestedString_notIgnoredUnlimited(self):
        assert (q([['hello', 'world'], ['I', 'am', 'Fliq']]).flatten(ignore_types=None).to_list() ==
                ['h', 'e', 'l', 'l', 'o', 'w', 'o', 'r',
                 'l', 'd', 'I', 'a', 'm', 'F', 'l', 'i', 'q'])

    def test_flatten_nestedStringAsGenerator_notIgnoredUnlimited(self):
        assert (q(str(i) + str(i + 1) for i in range(5)).flatten(ignore_types=None).to_list() ==
                ['0', '1', '1', '2', '2', '3', '3', '4', '4', '5'])

    def test_flatten_negativeDepth_valueErrorRaised(self):
        with pytest.raises(ValueError):
            q([1, 2, 3]).flatten(max_depth=-1)