class FliqTestUtils:

    iterable_parameters_multi = [
        ("list", [0, 1, 2, 3, 4]),
        ("generator", (i for i in range(5))),
        ("range", (range(5))),
        ("tuple", (0, 1, 2, 3, 4)),
        ("set", {0, 1, 2, 3, 4}),
        ("str", "01234"),
        ("bytes", b'\x00\x01\x02\x03\x04'),
        ("bytearray", bytearray(b'\x00\x01\x02\x03\x04')),
    ]

    iterable_parameters_single = [
        ("list", [0]),
        ("generator", (i for i in range(1))),
        ("range", (range(1))),
        ("tuple", (0,)),
        ("set", {0}),
        ("str", "0"),
        ("bytes", b'\x00'),
        ("bytearray", bytearray(b'\x00')),
    ]

    iterable_parameters_empty = [
        ("list", []),
        ("generator", (i for i in range(0))),
        ("range", (range(0))),
        ("tuple", ()),
        ("set", set()),
        ("str", ""),
        ("bytes", b""),
        ("bytearray", bytearray(b"")),
    ]
