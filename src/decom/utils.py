from typing import Literal

import numpy as np
from numpy.typing import NDArray


def irange(start: int, stop: int) -> list[int]:
    if start <= stop:
        return list(range(start, stop + 1))
    return list(range(start, stop - 1, -1))


def hex2dec(val: str) -> int:
    return int(val, base=16)


def oct2dec(val: str) -> int:
    return int(val, base=8)


def bin2dec(val: str) -> int:
    return int(val, base=2)


def bit_mask(val: int) -> list[int]:
    bits = []
    i = 1
    while val > 0:
        if val % 2 == 1:
            bits.append(i)
        val = val >> 1
        i += 1
    return bits


def word_size_to_uint(word_size: int) -> Literal["uint8", "uint16", "uint32", "uint64"]:
    if word_size < 0:
        msg = f"word_size={word_size!r} cannot be negative"
        raise ValueError(msg)
    elif word_size <= 8:
        return "uint8"
    elif word_size <= 16:
        return "uint16"
    elif word_size <= 32:
        return "uint32"
    elif word_size <= 64:
        return "uint64"
    msg = f"word_size={word_size} is not valid"
    raise ValueError(msg)


def bits_to_mask_and_shift(bits: tuple[int, int]) -> tuple[int, int]:
    lo, hi = min(bits), max(bits)

    mask = 0
    for bit in range(lo - 1, hi):
        mask += 2**bit

    shift = lo - 1
    return mask, shift


def reverse_bits(x: NDArray, bits: int) -> NDArray:
    """Reverses the bits of an integer.

    Args:
        x (int or numpy.ndarray): The integer(s) to reverse.
        bits (int): The number of bits to consider (default is 32).

    Returns:
        int or numpy.ndarray: The bit-reversed integer(s).
    """
    result = np.zeros_like(x)
    for i in range(bits):
        result |= ((x >> i) & 1) << (bits - 1 - i)
    return result
