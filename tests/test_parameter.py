import pytest
from decom.parsers import parameter_parser as parser

@pytest.mark.parametrize("text", [
    "[1]",
    "[1+2]",
    "[1+2:5-8]",
    "1-4",
    "4-1",
    "[1R]",
    "[1:1-4R]",
    "(1-4)R",
    "1++1",
    "1++2<16",
])
def test_parser(text: str):
    print(f"Input: {text!r}")
    tree = parser.parse(text)
    print("Output:", tree.pretty())
    assert tree
