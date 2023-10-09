from dataclasses import dataclass


@dataclass
class TestClass:
    a: int

    def __hash__(self):
        return hash(self.a)


class Params:
    sig_iterable = "iter_type,iterable,iterable_list"
    sig_iterable_obj = "iter_type,iterable"

    @staticmethod
    def iterable_obj_multi():
        return [
            ("list", [
                TestClass(0),
                TestClass(1),
                TestClass(2),
                TestClass(3),
                TestClass(4)
            ]),
            ("generator", (TestClass(i) for i in range(5))),
            ("tuple", (
                TestClass(0),
                TestClass(1),
                TestClass(2),
                TestClass(3),
                TestClass(4))),
            ("set", {
                TestClass(0),
                TestClass(1),
                TestClass(2),
                TestClass(3),
                TestClass(4)
            }),
        ]

    @staticmethod
    def iterable_obj_single():
        return [
            ("list", [TestClass(0)]),
            ("generator", (TestClass(i) for i in range(1))),
            ("tuple", (TestClass(0),)),
            ("set", {TestClass(0)}),
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
