import pytest

from fliq.tests.fliq_test_utils import Params
from fliq import q


class TestPartition:
    @pytest.mark.parametrize(Params.sig_iterable, Params.iterable_empty())
    def test_partition_hasNoItems(self,
                                  iter_type,
                                  iterable,
                                  iterable_list):
        q1, q2 = q(iterable).partition(lambda x: int(x), n=2)
        assert q1 == iterable_list
        assert q2 == iterable_list

    @pytest.mark.parametrize(Params.sig_iterable, Params.iterable_single())
    def test_partition_hasSingleItem(self,
                                     iter_type,
                                     iterable,
                                     iterable_list):
        q1, q2 = q(iterable).partition(lambda x: int(x), n=2)
        assert q1 == iterable_list
        assert q2 == []

    @pytest.mark.parametrize(Params.sig_iterable, Params.iterable_multi())
    def test_partition_hasMultipleItems(self,
                                        iter_type,
                                        iterable,
                                        iterable_list):
        q0, q1, q2, q3, q4 = q(iterable).partition(lambda x: int(x), n=5)
        assert q0 == [iterable_list[0]]
        assert q1 == [iterable_list[1]]
        assert q2 == [iterable_list[2]]
        assert q3 == [iterable_list[3]]
        assert q4 == [iterable_list[4]]

    @pytest.mark.parametrize(Params.sig_iterable, Params.iterable_multi())
    def test_partition_hasMultipleItems_binary(self,
                                               iter_type,
                                               iterable,
                                               iterable_list):
        q0, q1 = q(iterable).partition(lambda x: int(x) % 2, n=2)
        assert q0 == [iterable_list[0], iterable_list[2], iterable_list[4]]
        assert q1 == [iterable_list[1], iterable_list[3]]

    @pytest.mark.parametrize(Params.sig_iterable, Params.iterable_multi())
    def test_partition_hasMultipleItems_predicate(self,
                                                  iter_type,
                                                  iterable,
                                                  iterable_list):
        q0, q1 = q(iterable).partition(lambda x: int(x) == 2)
        assert q0 == [iterable_list[0], iterable_list[1], iterable_list[3], iterable_list[4]]
        assert q1 == [iterable_list[2]]

    def test_partition_iteratingPastExhaustion_stopIterationRaised(self):
        q0, _ = q(range(3)).partition(lambda x: x % 2, n=2)
        next(q0)
        next(q0)
        with pytest.raises(StopIteration):
            next(q0)

    def test_partition_wrongPartitionIndexType_typeErrorRaised(self):
        q0, _, _ = q(range(3)).partition(lambda x: x == 1, n=3)
        with pytest.raises(TypeError):
            for _ in q0:
                pass

    def test_partition_iteratingOverItemWithoutPartition_valueErrorRaised(self):
        q0, _ = q(range(3)).partition(lambda x: x, n=2)
        next(q0)
        with pytest.raises(ValueError):
            next(q0)

    def test_partition_nonPositiveN_valueErrorRaised(self):
        with pytest.raises(ValueError):
            q(range(3)).partition(lambda x: x, n=0)
