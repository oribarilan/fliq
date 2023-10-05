from unittest import TestCase
from fliq import q


class TestQuery(TestCase):
    def test_query_withList(self):
        iterable = [1, 2, 3, 4, 5]
        q(iterable)

    def test_query_withTuple(self):
        iterable = (1, 2, 3, 4, 5)
        q(iterable)

    def test_query_withSet(self):
        iterable = {1, 2, 3, 4, 5}
        q(iterable)

    def test_query_withDict(self):
        iterable = {1: 'a', 2: 'b', 3: 'c', 4: 'd', 5: 'e'}
        q(iterable)

    def test_query_withString(self):
        iterable = 'abcde'
        q(iterable)

    def test_query_withRange(self):
        iterable = range(5)
        q(iterable)

    def test_query_withGenerator(self):
        iterable = (i for i in range(5))
        q_iterable = q(iterable)
        assert isinstance(q_iterable._items, list)

    def test_query_withNone(self):
        iterable = None

        with self.assertRaises(TypeError):
            q(iterable)
