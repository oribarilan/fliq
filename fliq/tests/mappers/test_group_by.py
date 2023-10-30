import pytest

from fliq import q
from fliq.tests.fliq_test_utils import Params, MyTestClass


class TestGroupBy:
    @pytest.mark.parametrize(Params.sig_iterable, Params.iterable_empty())
    def test_groupBy_hasNoItems(self, iter_type, iterable, iterable_list):
        assert q(iterable).group_by('id') == iterable_list

    @pytest.mark.parametrize(Params.sig_iterable_obj, Params.iterable_obj_single())
    def test_groupBy_hasSingleItem_attributeDoesNotExist(self, iter_type, iterable):
        with pytest.raises(AttributeError):
            q(iterable).group_by('id')

    @pytest.mark.parametrize(Params.sig_iterable_obj, Params.iterable_obj_single())
    def test_groupBy_hasSingleItem_attributeExists_keyIsString(self, iter_type, iterable):
        assert q(iterable).group_by('a') == [[MyTestClass(0, 0)]]

    @pytest.mark.parametrize(Params.sig_iterable_obj, Params.iterable_obj_multi())
    def test_groupBy_hasMultipleItems_attributeExists_keyIsString(self, iter_type, iterable):
        assert q(iterable).group_by('a') == [
            [MyTestClass(0, 0)],
            [MyTestClass(1, 1 * 2)],
            [MyTestClass(2, 2 * 2)],
            [MyTestClass(3, 3 * 2)],
            [MyTestClass(4, 4 * 2)],
        ]

    @pytest.mark.parametrize(Params.sig_iterable_obj, Params.iterable_obj_multi())
    def test_groupBy_hasMultipleItems_attributeExists_keyIsLambda(self, iter_type, iterable):
        assert q(iterable).group_by(lambda x: x.a % 2 == 0) == [
            [MyTestClass(0, 0), MyTestClass(2, 2 * 2), MyTestClass(4, 4 * 2)],
            [MyTestClass(1, 1 * 2), MyTestClass(3, 3 * 2)],
        ]
