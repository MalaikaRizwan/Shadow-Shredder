from __future__ import annotations

import os
from abc import ABC, abstractmethod


class WipeMethod(ABC):
    name = "base"

    @abstractmethod
    def transform(self, data: bytes, pass_index: int) -> bytes:
        raise NotImplementedError


class NullBytesMethod(WipeMethod):
    name = "NULL_0x00"

    def transform(self, data: bytes, pass_index: int) -> bytes:
        return b"\x00" * len(data)


class OnesBytesMethod(WipeMethod):
    name = "ONES_0xFF"

    def transform(self, data: bytes, pass_index: int) -> bytes:
        return b"\xFF" * len(data)


class RandomBytesMethod(WipeMethod):
    name = "RANDOM"

    def transform(self, data: bytes, pass_index: int) -> bytes:
        return os.urandom(len(data))


class AlternatingPatternMethod(WipeMethod):
    name = "ALT_AA_55"

    def transform(self, data: bytes, pass_index: int) -> bytes:
        byte_value = 0xAA if pass_index % 2 == 0 else 0x55
        return bytes([byte_value]) * len(data)


class CustomByteMethod(WipeMethod):
    name = "CUSTOM_BYTE"

    def __init__(self, value: int):
        if value < 0 or value > 255:
            raise ValueError("Custom byte must be in range 0..255")
        self._value = value

    def transform(self, data: bytes, pass_index: int) -> bytes:
        return bytes([self._value]) * len(data)


class XorMethod(WipeMethod):
    name = "XOR_FAST"

    def __init__(self, xor_key: int = 0xA5):
        self._xor_key = xor_key & 0xFF

    def transform(self, data: bytes, pass_index: int) -> bytes:
        key = (self._xor_key + pass_index) & 0xFF
        return bytes((b ^ key) for b in data)


class BitInversionMethod(WipeMethod):
    name = "BIT_INVERSION"

    def transform(self, data: bytes, pass_index: int) -> bytes:
        return bytes((~b) & 0xFF for b in data)


class BitRotationMethod(WipeMethod):
    name = "BIT_ROTATION"

    def __init__(self, shift: int = 1):
        self._shift = shift % 8

    def transform(self, data: bytes, pass_index: int) -> bytes:
        s = (self._shift + pass_index) % 8
        if s == 0:
            return data
        return bytes((((b << s) & 0xFF) | (b >> (8 - s))) for b in data)


def build_method(method_name: str, custom_byte_value: int | None = None) -> WipeMethod:
    method_map = {
        NullBytesMethod.name: NullBytesMethod,
        OnesBytesMethod.name: OnesBytesMethod,
        RandomBytesMethod.name: RandomBytesMethod,
        AlternatingPatternMethod.name: AlternatingPatternMethod,
        XorMethod.name: XorMethod,
        BitInversionMethod.name: BitInversionMethod,
        BitRotationMethod.name: BitRotationMethod,
    }
    if method_name == CustomByteMethod.name:
        return CustomByteMethod(custom_byte_value if custom_byte_value is not None else 0x11)
    cls = method_map.get(method_name)
    if not cls:
        raise ValueError(f"Unsupported wipe method: {method_name}")
    return cls()
