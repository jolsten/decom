import pytest

from decom.array import UintXArray
from decom.measurand import Interp

from ..conftest import NUM_FRAMES


@pytest.mark.parametrize(
    "word_size, input_, expected",
    [
        (8, 0, 0),
    ],
)
def test_u(word_size: int, input_: int, expected: int):
    interp = Interp("u")
    data = UintXArray([input_] * NUM_FRAMES, word_size=word_size)
    out = interp.apply(data)
    assert out.tolist() == [expected] * NUM_FRAMES


@pytest.mark.parametrize(
    "word_size, input_, expected",
    [
        (3, 0, 0),
        (3, 1, 1),
        (3, 2, 2),
        (3, 3, 3),
        (3, 4, -4),
        (3, 5, -3),
        (3, 6, -2),
        (3, 7, -1),
        (8, 0, 0),
        (8, 1, 1),
        (8, 2, 2),
        (8, 126, 126),
        (8, 127, 127),
        (8, 128, -128),
        (8, 129, -127),
        (8, 130, -126),
        (8, 253, -3),
        (8, 254, -2),
        (8, 255, -1),
    ],
)
def test_2c(word_size: int, input_: int, expected: int):
    interp = Interp("2c")
    data = UintXArray([input_] * NUM_FRAMES, word_size=word_size)
    out = interp.apply(data)
    assert out.tolist() == [expected] * NUM_FRAMES
