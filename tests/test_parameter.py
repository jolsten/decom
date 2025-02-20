import pytest

from decom.array import UintXArray
from decom.parameter import FragmentConstant, FragmentWord, Parameter
from decom.parsers import parameter_parser

NUM_FRAMES = 10
SAMPLE_DATA = {}
for word_size in [8, 10, 12]:
    SAMPLE_DATA[word_size] = UintXArray(
        [[x % 2**word_size for x in range(1, 2**word_size + 1)]] * NUM_FRAMES,
        word_size=word_size,
    )


@pytest.mark.parametrize(
    "word_size, frag, expected",
    [
        (8, FragmentWord(word=1, bits=None), 1),
        (8, FragmentWord(word=64, bits=None), 64),
        (8, FragmentWord(word=128, bits=None), 128),
        (8, FragmentWord(word=0x00, bits=(1, 1)), 0),
        (8, FragmentWord(word=0xFF, bits=(1, 1)), 1),
        (8, FragmentWord(word=0x0F, bits=(1, 4)), 0xF),
        (8, FragmentWord(word=0x0F, bits=(5, 8)), 0x0),
        (8, FragmentWord(word=0xF0, bits=(1, 4)), 0x0),
        (8, FragmentWord(word=0xF0, bits=(5, 8)), 0xF),
        (8, FragmentWord(word=256, bits=None), 0),
        (8, FragmentWord(word=255, bits=(1, 2)), 3),
        (8, FragmentWord(word=255, bits=(1, 4)), 15),
        (8, FragmentWord(word=255, bits=(1, 6)), 63),
        (8, FragmentWord(word=255, bits=(1, 8)), 255),
        (10, FragmentWord(word=1, bits=None), 1),
        (10, FragmentWord(word=256, bits=None), 256),
        (10, FragmentWord(word=1024, bits=None), 0),
        (10, FragmentWord(word=0b0111111110, bits=(2, 9)), 0b11111111),
    ],
)
def test_fragment_word_build(word_size: int, frag: FragmentWord, expected: int):
    data = SAMPLE_DATA[word_size]
    out = frag.build(data)
    print("frag =", frag)
    try:
        print("frag._mask  =", frag._mask)
        print("frag._shift =", frag._shift)
    except AttributeError:
        pass
    print("out =", out)
    print("expected =", expected)
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
    ],
)
def test_parameter_build(word_size: int, param: Parameter, expected: int):
    p = parameter_parser.parse(param)
    out = p.build(SAMPLE_DATA[word_size])
    assert out.tolist() == [expected] * NUM_FRAMES
