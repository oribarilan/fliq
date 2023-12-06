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
        def name_selector(person: Person) -> str:
            return person.name

        men = [Person(name=f'Mr {i}', age=i, gender="M") for i in range(30)]
        women = [Person(name=f'Ms {i+10}', age=i, gender="W") for i in range(30)]
        non_binary = [Person(name=f'{i+30}', age=i, gender="N") for i in range(30)]
        adults = (q(men)
                  .append_many(women)
                  .where(lambda p: p.age >= 25)
                  .prepend_many(non_binary)
                  .select(name_selector))

        assert adults.count() == 5 + 5 + 30

    def test_sanity_3(self):
        data = [1, 2, 3, 4, 5]
        gen = (i * 2 if i % 2 == 0 else -1 for i in [1, 2, 3, 4, 5])
        fliq = q(data).select(lambda x: x * 2 if x % 2 == 0 else -1)
        assert list(fliq) == list(gen)