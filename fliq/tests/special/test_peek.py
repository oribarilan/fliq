import pytest

from fliq import q
from fliq.tests.fliq_test_utils import Params


class TestPeek:
    @pytest.mark.parametrize(Params.sig_iterable, Params.iterable_empty())
    def test_peek_peekEmpty_noneReturned(self, iter_type, iterable, iterable_list):
        items = q(iterable)
        e0 = items.peek()
        assert e0 is None
        assert items == iterable_list

    @pytest.mark.parametrize(Params.sig_iterable, Params.iterable_single())
    def test_peek_peekSingle_doesNotConsume(self, iter_type, iterable, iterable_list):
        items = q(iterable)
        e0 = items.peek()
        assert e0 == iterable_list[0]
        assert items == iterable_list

    @pytest.mark.parametrize(Params.sig_iterable, Params.iterable_single())
    def test_peek_peekMoreThanSize_nonAvailableAreNone(self, iter_type, iterable, iterable_list):
        items = q(iterable)
        e0, e1 = items.peek(n=2)
        assert e0 == iterable_list[0]
        assert e1 is None
        assert items.to_list() == iterable_list

    @pytest.mark.parametrize(Params.sig_iterable, Params.iterable_single())
    def test_peek_peekMultipleMoreThanSize_nonAvailableAreNone(self,
                                                               iter_type,
                                                               iterable,
                                                               iterable_list):
        items = q(iterable)
        e0, e1, e2, e3, e4 = items.peek(n=5)
        assert e0 == iterable_list[0]
        assert e1 is None
        assert e2 is None
        assert e3 is None
        assert e4 is None
        assert items.to_list() == iterable_list

    @pytest.mark.parametrize(Params.sig_iterable, Params.iterable_multi())
    def test_peek_peekedAtPopulatedQuery_doesNotConsume(self, iter_type, iterable, iterable_list):
        query = q(iterable)
        first_item = query.peek()
        assert first_item == iterable_list[0]
        assert query.to_list() == iterable_list

    @pytest.mark.parametrize(Params.sig_iterable, Params.iterable_multi())
    def test_peek_peekMultipleItems_doesNotConsume(self, iter_type, iterable, iterable_list):
        items = q(iterable)
        e0, e1, e2 = items.peek(n=3)
        assert e0 == iterable_list[0]
        assert e1 == iterable_list[1]
        assert e2 == iterable_list[2]
        assert items.to_list() == iterable_list

    @pytest.mark.parametrize(Params.sig_iterable, Params.iterable_multi())
    def test_peek_multiplePeekBeforeConsumption_doesNotConsume(self,
                                                               iter_type,
                                                               iterable,
                                                               iterable_list):
        items = q(iterable)
        e00, e01, e02 = items.peek(n=3)
        e10, e11, e12 = items.peek(n=3)
        assert e00 == iterable_list[0]
        assert e01 == iterable_list[1]
        assert e02 == iterable_list[2]
        assert e10 == iterable_list[0]
        assert e11 == iterable_list[1]
        assert e12 == iterable_list[2]
        assert items == iterable_list

    @pytest.mark.parametrize(Params.sig_iterable, Params.iterable_multi())
    def test_peek_peekAfterPartialConsumption_doesNotConsume(self,
                                                             iter_type,
                                                             iterable,
                                                             iterable_list):
        items = q(iterable)
        e0 = next(items)
        e1, e2 = items.peek(n=2)
        assert e0 == iterable_list[0]
        assert e1 == iterable_list[1]
        assert e2 == iterable_list[2]
        assert items == iterable_list[1:]

    @pytest.mark.parametrize(Params.sig_iterable, Params.iterable_multi())
    def test_peek_peekDuringIteration_doesNotConsume(self,
                                                     iter_type,
                                                     iterable,
                                                     iterable_list):
        items = q(iterable)
        iterated = []
        peeked = None
        for i, element in enumerate(items):
            if i == 1:
                # peaked is item at index 2
                peeked = items.peek()
            iterated.append(element)
        assert iterated == iterable_list
        assert peeked == iterable_list[2]

    @pytest.mark.parametrize(Params.sig_iterable, Params.iterable_multi())
    def test_peek_peekAfterIteration_doesNotConsume(self,
                                                     iter_type,
                                                     iterable,
                                                     iterable_list):
        items = q(iterable)
        iterated = []
        for i, element in enumerate(items):
            iterated.append(element)
        peeked = items.peek()
        assert iterated == iterable_list
        assert peeked is None

    def test_peek_peekNonPositive_valueErrorRaised(self):
        with pytest.raises(ValueError):
            q(range(5)).peek(n=0)
