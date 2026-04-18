from app.core.wipe_methods import (
    AlternatingPatternMethod,
    BitInversionMethod,
    BitRotationMethod,
    CustomByteMethod,
    NullBytesMethod,
    OnesBytesMethod,
    RandomBytesMethod,
    XorMethod,
)


def test_methods_keep_length():
    data = b"abcdef123456"
    methods = [
        NullBytesMethod(),
        OnesBytesMethod(),
        RandomBytesMethod(),
        AlternatingPatternMethod(),
        CustomByteMethod(0x7E),
        XorMethod(),
        BitInversionMethod(),
        BitRotationMethod(),
    ]
    for method in methods:
        out = method.transform(data, 0)
        assert len(out) == len(data)


def test_custom_method_value_applies():
    data = b"xxxx"
    out = CustomByteMethod(0x33).transform(data, 0)
    assert out == b"\x33" * 4
