import numpy as np
import pytest

from decom import utils
from decom.array import UintXArray

from .conftest import NUM_FRAMES


@pytest.mark.parametrize(
    "text",
    [
        "0000",
        "0101",
        "1010",
        "1111",
        "00000000",
        "00001111",
        "11110000",
        "11111111",
        "0000000000000000",
        "0101010101010101",
        "1010101010101010",
        "1111111111111111",
    ],
)
def test_array_invert(text: str):
    input_ = int(text, base=2)
    word_size = len(text)

    # Substitute 0 -> 1, 1 -> 0 (with an intermediate placeholder "a")
    expected = text.replace("0", "a").replace("1", "0").replace("a", "1")
    expected = int(expected, base=2)

    data = np.array([input_] * NUM_FRAMES, dtype=utils.word_size_to_uint(word_size))
    array = UintXArray(data, word_size=word_size)
    out = np.invert(array)
    print(array, f"word_size={array.word_size}")
    assert out.word_size == word_size
    assert out.tolist() == [expected] * NUM_FRAMES
