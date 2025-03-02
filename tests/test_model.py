import numpy as np
import pytest

from decom import utils
from decom.model import FrameBatch, VarUIntArray

from .conftest import NUM_FRAMES, SAMPLE_DATA


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

    data = np.array([[input_]] * NUM_FRAMES, dtype=utils.word_size_to_uint(word_size))
    array = VarUIntArray(data, word_size=word_size)
    out = np.invert(array)
    print(array, f"word_size={array.word_size}")
    assert out.word_size == word_size
    assert out.tolist() == [[expected]] * NUM_FRAMES


def test_frame_batch_slice():
    t0 = np.datetime64("2020-01-01", "ns")
    time = t0 + np.arange(NUM_FRAMES, dtype="timedelta64[s]")
    data = SAMPLE_DATA[8]
    fb = FrameBatch(time=time, ctime=time, data=data)
    assert fb[:] == fb
    assert fb[0] == FrameBatch(
        time=np.atleast_1d(time[0]),
        ctime=np.atleast_1d(time[0]),
        data=np.atleast_2d(data[0]),
    )
