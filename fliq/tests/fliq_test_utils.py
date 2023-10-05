from dataclasses import dataclass


@dataclass
class TestClass:
    a: int

    def __hash__(self):
        return hash(self.a)


class Params:
    sig = "iter_type,iterable"

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
        return [
            ("list", [0, 1, 2, 3, 4]),
            ("generator", (i for i in range(5))),
            ("range", (range(5))),
            ("tuple", (0, 1, 2, 3, 4)),
            ("set", {0, 1, 2, 3, 4}),
            ("str", "01234"),
            ("bytes", b'\x00\x01\x02\x03\x04'),
            ("bytearray", bytearray(b'\x00\x01\x02\x03\x04')),
        ]

    @staticmethod
    def iterable_single():
        return [
            ("list", [0]),
            ("generator", (i for i in range(1))),
            ("range", (range(1))),
            ("tuple", (0,)),
            ("set", {0}),
            ("str", "0"),
            ("bytes", b'\x00'),
            ("bytearray", bytearray(b'\x00')),
        ]

    @staticmethod
    def iterable_empty():
        return [
            ("list", []),
            ("generator", (i for i in range(0))),
            ("range", (range(0))),
            ("tuple", ()),
            ("set", set()),
            ("str", ""),
            ("bytes", b""),
            ("bytearray", bytearray(b"")),
        ]
