from unittest import TestCase

from fliq import q


class TestQuery(TestCase):
    def test_query_iterable(self):
        expected = [1, 2, 3]
        actual = [i for i in q(expected)]
        assert expected == actual
