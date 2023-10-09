from dataclasses import dataclass
from unittest import TestCase

from fliq import q

@dataclass
class Item:
    price: int
    rating: float


class TestSanity(TestCase):

    def setUp(self):
        self.items = (Item(i, i % 5) for i in range(100))

    def test_sanity(self):
        price = (
            q(self.items)
            .where(lambda x: x.price > 50)
            .select(lambda x: x.price)
            .first_or_default(default=0)
        )
        assert price == 51
