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
