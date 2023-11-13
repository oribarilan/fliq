import pytest

from fliq import q
from fliq.exceptions import NotEnoughElementsException
from fliq.tests.fliq_test_utils import Params
from fliq.tests.utils.tracking_iterator import TrackingIterator


class TestSample:
    @pytest.mark.parametrize(Params.sig_iterable, Params.iterable_empty())
    def test_sample_sampleEmpty_errorRaised(self, iter_type, iterable, iterable_list):
        with pytest.raises(NotEnoughElementsException):
            q(iterable).sample()

    @pytest.mark.parametrize(Params.sig_iterable, Params.iterable_single())
    def test_sample_sampleSingle_doesNotConsume(self, iter_type, iterable, iterable_list):
        e0 = q(iterable).sample()
        assert e0 == iterable_list[0]

    @pytest.mark.parametrize(Params.sig_iterable, Params.iterable_single())
    def test_sample_sampleMoreThanSize_errorRaised(self, iter_type, iterable, iterable_list):
        with pytest.raises(NotEnoughElementsException):
            q(iterable).sample(n=2)

    def test_sample_zeroNumber(self):
        with pytest.raises(ValueError):
            q(range(5)).sample(n=0)

    def test_sample_negativeNumber(self):
        with pytest.raises(ValueError):
            q(range(5)).sample(n=-1)

    @pytest.mark.parametrize(Params.sig_iterable, Params.iterable_multi())
    def test_sample_sampledOne_singleItemReturned(self, iter_type, iterable, iterable_list):
        sampled_item = q(iterable).sample(seed=42)
        assert sampled_item == iterable_list[1]

    @pytest.mark.parametrize(Params.sig_iterable, Params.iterable_multi())
    def test_sample_sampledWithinSize_multipleItemsReturned(self,
                                                            iter_type,
                                                            iterable,
                                                            iterable_list):
        s0, s1 = q(iterable).sample(n=2, seed=42)
        assert s0 == iterable_list[0]
        assert s1 == iterable_list[4]

    @pytest.mark.parametrize(Params.sig_iterable, Params.iterable_multi())
    def test_sample_sampledOverSize_errorRaised(self, iter_type, iterable, iterable_list):
        with pytest.raises(NotEnoughElementsException):
            q(iterable).sample(n=6)

    def test_sample_sampledWithBudget_multipleItemsReturned(self):
        n = 10
        budget_factor = 1
        sequence = range(100)  # Known sequence
        tracking_iterable = TrackingIterator(sequence)
        q(tracking_iterable).sample(n=n, budget_factor=budget_factor)
        assert tracking_iterable.count <= n * budget_factor

    def test_sample_sampleWithStopFactor_stopFactorStopsSampling(self):
        sequence = range(10000)  # Longer sequence to allow for early stopping
        n = 5
        seed = 42
        stop_factor = 1  # Higher probability of stopping early
        budget_factor = 100
        tracking_iterable = TrackingIterator(sequence)

        q(tracking_iterable).sample(n=n,
                                    seed=seed,
                                    budget_factor=budget_factor,
                                    stop_factor=stop_factor)

        assert tracking_iterable.count <= budget_factor * n

    def test_sample_budgetFactorIsPositive(self):
        with pytest.raises(ValueError):
            q(range(5)).sample(budget_factor=-1)

    def test_sample_stopFactorIsPositive(self):
        with pytest.raises(ValueError):
            q(range(5)).sample(stop_factor=-1)
