import random

import pytest

from fliq import q
from fliq.tests.fliq_test_utils import Params

SEED = 42


@pytest.fixture()
def rand() -> random.Random:
    return random.Random(SEED)


class TestShuffle:
    @pytest.mark.parametrize(Params.sig_iterable, Params.iterable_empty())
    def test_shuffle_hasNoItems_fairShuffle(self,
                                            iter_type,
                                            iterable,
                                            iterable_list):
        if iter_type == 'generator':
            with pytest.raises(TypeError):
                q(iterable).shuffle(fair=True)
        else:
            assert q(iterable).shuffle(fair=True) == iterable_list

    @pytest.mark.parametrize(Params.sig_iterable, Params.iterable_empty())
    def test_shuffle_hasNoItems_unfairShuffle(self,
                                              iter_type,
                                              iterable,
                                              iterable_list):
        assert q(iterable).shuffle(fair=False) == iterable_list

    @pytest.mark.parametrize(Params.sig_iterable, Params.iterable_single())
    def test_shuffle_hasSingleItem(self,
                                   iter_type,
                                   iterable,
                                   iterable_list):
        assert q(iterable).shuffle() == iterable_list

    @pytest.mark.parametrize(Params.sig_iterable, Params.iterable_multi())
    def test_shuffle_hasMultipleItems(self,
                                      iter_type,
                                      iterable,
                                      iterable_list,
                                      rand):
        rand.shuffle(iterable_list)
        assert q(iterable).shuffle(seed=SEED) == iterable_list

    def test_shuffle_hasMultipleItems_unfairShuffle_bufferSmallerThanIterableSize(self):
        shuffled_items = list(range(100))
        unfair_shuffled_items = q(range(100)).shuffle(seed=SEED, buffer_size=10).to_list()
        assert set(unfair_shuffled_items) == set(shuffled_items)
        assert len(unfair_shuffled_items) == len(shuffled_items)

    def test_shuffle_hasMultipleItems_unfairShuffle_bufferBiggerThanIterableSize(self):
        shuffled_items = list(range(10))
        unfair_shuffled_items = q(range(10)).shuffle(seed=SEED, buffer_size=100).to_list()
        assert set(unfair_shuffled_items) == set(shuffled_items)
        assert len(unfair_shuffled_items) == len(shuffled_items)

    def test_shuffle_hasMultipleItems_unfairShuffle_bufferSameSizeAsIterableSize(self):
        shuffled_items = list(range(100))
        unfair_shuffled_items = q(range(100)).shuffle(seed=SEED, buffer_size=100).to_list()
        assert set(unfair_shuffled_items) == set(shuffled_items)
        assert len(unfair_shuffled_items) == len(shuffled_items)

    def test_shuffle_hasMultipleItems_fairShuffle(self, rand):
        shuffled_items = list(range(100))
        rand.shuffle(shuffled_items)
        assert q(range(100)).shuffle(seed=SEED, fair=True) == shuffled_items
