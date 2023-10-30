import pytest

from fliq import q
from fliq.tests.fliq_test_utils import Params, MyTestClass


class TestToDict:
    @pytest.mark.parametrize(Params.sig_iterable, Params.iterable_empty())
    def test_toDict_hasNoItems(self, iter_type, iterable, iterable_list):
        assert q(iterable).to_dict('id') == dict()

    @pytest.mark.parametrize(Params.sig_iterable_obj, Params.iterable_obj_single())
    def test_toDict_hasSingleItem_attributeDoesNotExist(self, iter_type, iterable):
        with pytest.raises(AttributeError):
            q(iterable).to_dict('id')

    @pytest.mark.parametrize(Params.sig_iterable_obj, Params.iterable_obj_single())
    def test_toDict_hasSingleItem_attributeExists_keyIsString(self, iter_type, iterable):
        assert q(iterable).to_dict('a') == {0: [MyTestClass(0, 0)]}

    @pytest.mark.parametrize(Params.sig_iterable_obj, Params.iterable_obj_multi())
    def test_toDict_hasMultipleItems_attributeExists_keyIsString(self, iter_type, iterable):
        assert q(iterable).to_dict('a') == {
            0: [MyTestClass(0, 0)],
            1: [MyTestClass(1, 1 * 2)],
            2: [MyTestClass(2, 2 * 2)],
            3: [MyTestClass(3, 3 * 2)],
            4: [MyTestClass(4, 4 * 2)],
        }

    @pytest.mark.parametrize(Params.sig_iterable_obj, Params.iterable_obj_multi())
    def test_toDict_hasMultipleItems_attributeExists_keyIsLambda(self, iter_type, iterable):
        assert q(iterable).to_dict(lambda x: x.a % 2 == 0) == {
            True: [MyTestClass(0, 0), MyTestClass(2, 2 * 2), MyTestClass(4, 4 * 2)],
            False: [MyTestClass(1, 1 * 2), MyTestClass(3, 3 * 2)],
        }
