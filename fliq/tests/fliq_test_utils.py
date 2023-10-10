from dataclasses import dataclass
from functools import wraps
from typing import Optional


class FliqTestUtils:
    @staticmethod
    def assertSmallerOrCloseTo(a: float,
                               b: float,
                               tolerance: float = 0.0,
                               msg: Optional[str] = None) -> None:
        """
        Asserts that a is smaller than or bigger but close to b.

        Parameters:
        - a, b: The two numbers to be compared.
        - tolerance: The tolerance to be used. Must be a float between 0 and 1.
        """
        if a <= b:
            return

        if not (0.0 <= tolerance <= 1.0):
            raise ValueError("Tolerance must be a float between 0 and 1.")

        # Calculate the allowed difference based on the tolerance
        max_diff = a * tolerance

        actual_diff = abs(a - b)

        assert actual_diff <= max_diff, (
            f"{a:.10f} and {b:.10f} "
            f"differ by more than {max_diff:.10f} ({tolerance * 100}%),"
            f" actual difference: {actual_diff:.10f}"
            f" {msg if msg else ''}"
        )

    @classmethod
    def retry(cls, attempts: int):
        def decorator(fn):
            @wraps(fn)
            def wrapper(*args, **kwargs):
                for attempt in range(attempts):
                    try:
                        return fn(*args, attempt=attempt, **kwargs)
                    except AssertionError:
                        pass
                raise AssertionError(f"Test failed after {attempts} retries.")

            return wrapper

        return decorator


@dataclass
class MyTestClass:
    a: int
    b: int

    def __hash__(self):
        return hash(self.a)


class Params:
    sig_iterable = "iter_type,iterable,iterable_list"
    sig_iterable_obj = "iter_type,iterable"

    @staticmethod
    def iterable_obj_multi():
        return [
            ("list", [
                MyTestClass(0, 0 * 2),
                MyTestClass(1, 1 * 2),
                MyTestClass(2, 2 * 2),
                MyTestClass(3, 3 * 2),
                MyTestClass(4, 4 * 2)
            ]),
            ("generator", (MyTestClass(i, i * 2) for i in range(5))),
            ("tuple", (
                MyTestClass(0, 0 * 2),
                MyTestClass(1, 1 * 2),
                MyTestClass(2, 2 * 2),
                MyTestClass(3, 3 * 2),
                MyTestClass(4, 4 * 2))),
            ("set", {
                MyTestClass(0, 0 * 2),
                MyTestClass(1, 1 * 2),
                MyTestClass(2, 2 * 2),
                MyTestClass(3, 3 * 2),
                MyTestClass(4, 4 * 2)
            }),
        ]

    @staticmethod
    def iterable_obj_single():
        return [
            ("list", [MyTestClass(0, 0)]),
            ("generator", (MyTestClass(i, i) for i in range(1))),
            ("tuple", (MyTestClass(0, 0),)),
            ("set", {MyTestClass(0, 0)}),
        ]

    @staticmethod
    def iterable_multi():
        """
        type_name, iterable, iterable_list
        """
        return [
            ("list", [0, 1, 2, 3, 4], [0, 1, 2, 3, 4]),
            ("generator", (i for i in range(5)), [0, 1, 2, 3, 4]),
            ("range", (range(5)), [0, 1, 2, 3, 4]),
            ("tuple", (0, 1, 2, 3, 4), [0, 1, 2, 3, 4]),
            ("set", {0, 1, 2, 3, 4}, [0, 1, 2, 3, 4]),
            ("str", "01234", ['0', '1', '2', '3', '4']),
        ]

    @staticmethod
    def iterable_single():
        """
        type_name, iterable, iterable_list
        """
        return [
            ("list", [0], [0]),
            ("generator", (i for i in range(1)), [0]),
            ("range", (range(1)), [0]),
            ("tuple", (0,), [0]),
            ("set", {0}, [0]),
            ("str", "0", ['0']),
        ]

    @staticmethod
    def iterable_empty():
        """
        type_name, actual, iterable_list
        """
        return [
            ("list", [], []),
            ("generator", (i for i in range(0)), []),
            ("range", (range(0)), []),
            ("tuple", (), []),
            ("set", set(), []),
            ("str", "", []),
        ]
