import numpy as np
import pytest

from decom.array import SizedArray

NUM_FRAMES = 10


@pytest.mark.parametrize(
    "word_size, input, output",
    [
        (8, 0b00000000, 0b11111111),
        (8, 0b00001111, 0b11110000),
        (8, 0b11110000, 0b00001111),
        (8, 0b11111111, 0b00000000),
        (4, 0b00001111, 0b00000000),
    ],
)
def test_array_invert(word_size: int, input: int, output: int):
    data = np.array([input] * NUM_FRAMES, dtype="uint8")
    array = SizedArray(data, word_size=word_size)
    out = np.invert(array)
    print(array, f"word_size={array.word_size}")
    assert out.tolist() == [output] * NUM_FRAMES
