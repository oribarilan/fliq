from unittest import TestCase

from fliq import q


class TestQuery(TestCase):
    def test_query_withNone(self):
        iterable = None

        with self.assertRaises(TypeError):
            q(iterable)

    def test_query_withNonIterable(self):
        iterable = 5

        with self.assertRaises(TypeError):
            q(iterable)

    def test_query_iterable(self):
        expected = [1, 2, 3]
        actual = [i for i in q(expected)]
        assert expected == actual
