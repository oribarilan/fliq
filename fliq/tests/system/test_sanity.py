from dataclasses import dataclass
from unittest import TestCase

from fliq import q
from fliq.tests.fliq_test_utils import Person


@dataclass
class Item:
    price: int
    rating: float


class TestSanity(TestCase):

    def setUp(self):
        self.items = (Item(i, i % 5) for i in range(100))

    def test_sanity_1(self):
        price = (
            q(self.items)
            .where(lambda x: x.price > 50)
            .select(lambda x: x.price)
            .first_or_default(default=0)
        )
        assert price == 51

    def test_sanity_2(self):
        men = [Person(name=f'Mr {i}', age=i, gender="M") for i in range(10)]
        women = [Person(name=f'Ms {i+10}', age=i+10, gender="W") for i in range(10)]
        non_binary = [Person(name=f'{i+30}', age=i+30, gender="N") for i in range(10)]
        (q(men)
         .append_many(women)
         .where(lambda p: p.age < 5)
         .prepend_many(non_binary)
         .select(lambda p: p.name).to_list())
