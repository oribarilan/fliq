import pytest

from fliq import q
from fliq.tests.fliq_test_utils import Params


class TestReverse:
    def _is_reversible(self, iter_type):
        return iter_type != "set"

    @pytest.mark.parametrize(Params.sig_iterable, Params.iterable_empty())
    def test_reverse_reversible_empty(self,
                                      iter_type,
                                      iterable,
                                      iterable_list):
        if not self._is_reversible(iter_type):
            return

        assert list(q(iterable).reverse()) == list(reversed(iterable_list))

    @pytest.mark.parametrize(Params.sig_iterable, Params.iterable_single())
    def test_reverse_reversible_single(self,
                                       iter_type,
                                       iterable,
                                       iterable_list):
        if not self._is_reversible(iter_type):
            return

        assert list(q(iterable).reverse()) == list(reversed(iterable_list))

    @pytest.mark.parametrize(Params.sig_iterable, Params.iterable_multi())
    def test_reverse_reversible_multi(self,
                                      iter_type,
                                      iterable,
                                      iterable_list):
        if not self._is_reversible(iter_type):
            return

        assert list(q(iterable).reverse()) == list(reversed(iterable_list))

    @pytest.mark.parametrize(Params.sig_iterable, Params.iterable_empty())
    def test_reverse_irreversible_empty(self,
                                        iter_type,
                                        iterable,
                                        iterable_list):
        if self._is_reversible(iter_type):
            return

        with pytest.raises(TypeError):
            q(iterable).reverse()

    @pytest.mark.parametrize(Params.sig_iterable, Params.iterable_single())
    def test_reverse_irreversible_single(self,
                                         iter_type,
                                         iterable,
                                         iterable_list):
        if self._is_reversible(iter_type):
            return

        with pytest.raises(TypeError):
            q(iterable).reverse()

    @pytest.mark.parametrize(Params.sig_iterable, Params.iterable_multi())
    def test_reverse_irreversible_multi(self,
                                        iter_type,
                                        iterable,
                                        iterable_list):
        if self._is_reversible(iter_type):
            return

        with pytest.raises(TypeError):
            q(iterable).reverse()
