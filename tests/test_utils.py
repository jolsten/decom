import pytest

from decom import utils


@pytest.mark.parametrize(
    "bits, mask, shift",
    [
        ((1, 8), 0b11111111, 0),
        ((1, 4), 0b00001111, 0),
        ((5, 8), 0b11110000, 4),
        ((8, 8), 0b10000000, 7),
        ((1, 1), 0b00000001, 0),
    ],
)
def test_bits_to_mask_and_shift(bits: tuple[int, int], mask: int, shift: int):
    m, s = utils.bits_to_mask_and_shift(bits)
    assert mask == m
    assert shift == s


@pytest.mark.parametrize(
    "bit_list, ranges",
    [
        ([1, 2, 3, 4], [(1, 4)]),
        ([5, 6, 7, 8], [(5, 8)]),
        ([1, 2, 3, 5, 7, 8], [(1, 3), (5, 5), (7, 8)]),
        ([1], [(1, 1)]),
        ([1, 2], [(1, 2)]),
        ([1, 2, 3], [(1, 3)]),
        ([1, 2, 3, 7, 8, 9], [(1, 3), (7, 9)]),
    ],
)
def test_bit_list_to_ranges(bit_list: list[int], ranges: list[tuple[int, int]]):
    out = utils.bit_list_to_ranges(bit_list)
    assert out == ranges
