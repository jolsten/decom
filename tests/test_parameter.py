import itertools

import pytest

from decom.measurand import FragmentConstant, GeneratorParameter, SupercomParameter
from decom.parsers import parameter_parser
from decom.transformers import Fragment, Parameter


@pytest.mark.parametrize(
    "text",
    [
        "[5]",
        "[~5]",
        "[~5R]",
        "[5+6]",
        # "[(5+6)R]",
        "[5:1-4+6:5-8R]",
        "[5:x0FR+6:xF0R]",
        "[~5]++10",
        "[95]--10",
        "[~5]++10<55",
        "[4+6]++20",
        "[1+2+3+x00]",
        "[1+2] XOR x55",
    ],
)
def test_parser(text: str):
    p = parameter_parser.parse(text)
    assert isinstance(p, (Parameter, SupercomParameter, GeneratorParameter))


@pytest.mark.parametrize(
    "text, expect",
    [
        ("[1]", Parameter([Fragment(1)])),
        ("[1+2]", Parameter([Fragment(1), Fragment(2)])),
        ("[1-2]", Parameter([Fragment(1), Fragment(2)])),
        ("[2-1]", Parameter([Fragment(2), Fragment(1)])),
        (
            "[1:1-4+2:5-8]",
            Parameter([Fragment(1, [1, 2, 3, 4]), Fragment(2, [5, 6, 7, 8])]),
        ),
        ("[~1]", Parameter([Fragment(word=1, complement=True)])),
        (
            "[~1-2]",
            Parameter(
                [Fragment(word=1, complement=True), Fragment(word=2, complement=True)]
            ),
        ),
        ("[1R]", Parameter([Fragment(1, reverse=True)])),
        ("[xF]", Parameter([FragmentConstant(15, 4)])),
        (
            "[xF+1+xF]",
            Parameter([FragmentConstant(15, 4), Fragment(1), FragmentConstant(15, 4)]),
        ),
    ],
)
def test_transformer(text: str, expect: Parameter):
    result = parameter_parser.parse(text)
    assert result == expect


@pytest.mark.parametrize(
    "text",
    [
        "[1:5-8] == [1:8-5] == [1:5,6,7,8] == [1:8,7,6,5]",
        "[1:1,3,5,7] == [1:7,5,3,1]",
        "[1:4-1-4] == [1-4:1-4] == [1:1-4+2:1-4+3:1-4+4:1-4]",
        "[~1+~2+~3] == [~1-3]",
        "[1R+2R+3R] == [1-3R]",
        "[1:1-8] == [1:8-1] == [1:1,2,3,4,5,6,7,8] == [1:8,7,6,5,4,3,2,1] == [1:o377] == [1:xff] == [1:xFF]",
        "[1-4:8,5-3,1] == [1:b10011101-4] == [1-4:b10011101]",
        "[xFF] == [b11111111]",
        "[o377] == [b011111111]",
        "[1-4:xf0] == [1:xf0-4]",
        "[xf0] == ['xf0']",
    ],
)
def test_parameters_eq(text: str):
    parameters = text.split("==")
    for a, b in itertools.pairwise(parameters):
        print(a.strip())
        a = parameter_parser.parse(a.strip())
        print(b.strip())
        b = parameter_parser.parse(b.strip())
        assert a == b


@pytest.mark.parametrize(
    "text",
    [
        "[1:7+1:5+1:3+1:1] != [1:1+1:3+1:5+1:7]",
    ],
)
def test_parameters_ne(text: str):
    parameters = text.split("!=")
    for a, b in itertools.pairwise(parameters):
        print(a.strip())
        a = parameter_parser.parse(a.strip())
        print(b.strip())
        b = parameter_parser.parse(b.strip())
        assert a != b
