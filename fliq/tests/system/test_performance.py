from typing import Generator
from unittest import TestCase

from parameterized import parameterized

from fliq import q
from fliq.tests.fliq_test_utils import MyTestClass, FliqTestUtils
from fliq.tests.timer import Timer


class TestPerformance(TestCase):
    def _query_baseline(self, data: Generator):
        item = next(map(lambda x: x.b, filter(lambda x: x.a == 50, data))) or -1
        return item

    def _query_fliq(self, data: Generator):
        item = (
            q(data)
            .where(lambda x: x.a == 50)
            .select(lambda x: x.b)
            .first_or_default(default=-1)
        )
        return item

    @staticmethod
    def _generate_data(num: int):
        return (MyTestClass(a=i, b=i * 2) for i in range(num))

    @parameterized.expand([
        ("small", 100),
        ("medium", 10_000),
        ("large", 10_000_000)
    ])
    def test_performance_smallDataset(self, name, data):
        self._test_performance(data)

    @FliqTestUtils.retry(attempts=10)
    def _test_performance(self, data, attempt: int):
        expected_item = 100

        with Timer() as baseline_t:
            baseline_item = self._query_baseline(self._generate_data(data))

        with Timer() as fliq_t:
            fliq_item = self._query_fliq(self._generate_data(data))

        self.assertEqual(
            expected_item,
            baseline_item,
            'Baseline query returned incorrect result'
        )
        self.assertEqual(
            expected_item,
            fliq_item,
            'Fliq query returned incorrect result'
        )
        if abs(fliq_t.elapsed - baseline_t.elapsed) < 0.001:
            # If the difference is less than 1ms, compare is not meaningful, due to noise
            return
        FliqTestUtils.assertSmallerOrCloseTo(
            fliq_t.elapsed,
            baseline_t.elapsed,
            0.01,
            f"Attempt {attempt}"
        )
