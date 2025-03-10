import numpy as np
import pytest

from decom.measurand import (
    FragmentConstant,
    FragmentWord,
    GeneratorParameter,
    SupercomParameter,
)
from decom.parsers import parameter_parser

from ..conftest import NUM_FRAMES, SAMPLE_DATA


@pytest.mark.parametrize(
    "word_size, frag, expected",
    [
        (8, FragmentWord(word=1, bits=None), 1),
        (8, FragmentWord(word=64, bits=None), 64),
        (8, FragmentWord(word=128, bits=None), 128),
        (8, FragmentWord(word=0x00, bits=[1, 1]), 0),
        (8, FragmentWord(word=0xFF, bits=[1, 1]), 1),
        (8, FragmentWord(word=0x0F, bits=[1, 2, 3, 4]), 0xF),
        (8, FragmentWord(word=0x0F, bits=[5, 6, 7, 8]), 0x0),
        (8, FragmentWord(word=0xF0, bits=[1, 2, 3, 4]), 0x0),
        (8, FragmentWord(word=0xF0, bits=[5, 6, 7, 8]), 0xF),
        (8, FragmentWord(word=256, bits=None), 0),
        (8, FragmentWord(word=255, bits=[1, 2]), 3),
        (8, FragmentWord(word=255, bits=[1, 2, 3, 4]), 15),
        (8, FragmentWord(word=255, bits=[1, 2, 3, 4, 5, 6]), 63),
        (8, FragmentWord(word=255, bits=[1, 2, 3, 4, 5, 6, 7, 8]), 255),
        (10, FragmentWord(word=1, bits=None), 1),
        (10, FragmentWord(word=256, bits=None), 256),
        (10, FragmentWord(word=1024, bits=None), 0),
        (
            10,
            FragmentWord(word=0b0111111110, bits=[2, 3, 4, 5, 6, 7, 8, 9]),
            0b11111111,
        ),
    ],
)
def test_fragment_word_build(word_size: int, frag: FragmentWord, expected: int):
    data = SAMPLE_DATA[word_size]
    print("data =", data)
    print("frag =", frag)
    print("expected =", expected)
    out = frag.build(data)
    print("out =", out)
    assert out.tolist() == [expected] * NUM_FRAMES


@pytest.mark.parametrize(
    "value, size, expected",
    [
        (0xF, 4, 0xF),
        (0xAA, 8, 0xAA),
        (0b1010, 4, 0b1010),
    ],
)
def test_fragment_constant_build(value: int, size: int, expected: int):
    frag = FragmentConstant(value, size)
    assert frag.build(None) == expected


@pytest.mark.parametrize(
    "word_size, param, expected",
    [
        (8, "[255+255]", 0xFFFF),
        (8, "[255:1-4+255]", 0xFFF),
        (8, "[170+85]", 0xAA55),
        (8, "[170R+85]", 0x5555),
        (8, "[170+85R]", 0xAAAA),
        (8, "[170R+85R]", 0x55AA),
        (8, "[255] XOR xFF", 0x00),
        (8, "[256] XOR xFF", 0xFF),
        (8, "[255] AND xF0", 0xF0),
        (8, "[255] AND x0F", 0x0F),
        (8, "[63] OR xF0", 0xFF),
        (8, "[15] OR b10000000", 0b10001111),
    ],
)
def test_parameter_build(word_size: int, param: str, expected: int):
    p = parameter_parser.parse(param)
    out = p.build(SAMPLE_DATA[word_size])
    assert out.tolist() == [expected] * NUM_FRAMES


@pytest.mark.parametrize(
    "word_size, text, p",
    [
        (8, "[1++1<17]", [f"[{i + 1}]" for i in range(16)]),
        (10, "[1:2-9++1<513]", [f"[{i + 1}:2-9]" for i in range(512)]),
        (8, "[1++32]", [f"[{i + 1}]" for i in range(0, 256, 32)]),
        (8, "[1++64]", [f"[{i + 1}]" for i in range(0, 256, 64)]),
        (10, "[1:2-9++64]", [f"[{i + 1}:2-9]" for i in range(0, 1024, 64)]),
    ],
)
def test_generator_parameter(word_size: int, text: str, p: list[str]):
    gp = parameter_parser.parse(text)
    assert isinstance(gp, GeneratorParameter)

    results = gp.build(SAMPLE_DATA[word_size])

    ep = [parameter_parser.parse(a) for a in p]
    expected = np.array([a.build(SAMPLE_DATA[word_size]) for a in ep]).T

    for a, b in zip(results, expected):
        assert a.tolist() == b.tolist()


@pytest.mark.parametrize(
    "word_size, text, num_cols, range_",
    [
        (8, "[1]++32", 8, range(1, 257, 32)),
    ],
)
def test_supercom_parameter(word_size: int, text: str, num_cols: int, range_: range):
    sp = parameter_parser.parse(text)
    assert isinstance(sp, SupercomParameter)

    result = sp.build(SAMPLE_DATA[word_size])

    assert result.shape[0] == NUM_FRAMES
    assert result.shape[1] == num_cols

    expected = np.array([[x for x in range_]] * NUM_FRAMES)
    assert result.tolist() == expected.tolist()
