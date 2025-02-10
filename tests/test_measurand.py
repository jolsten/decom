import pytest
from decom.parsers import measurand_parser as parser
from hypothesis import given
from . import strategies as cst

@pytest.mark.parametrize("text", [
    "[1];",
    "[1-2];1c",
    "[1+2+3];2c",
    "[1+2+3+4];ieee32",
    "[1-4];1750a32",
    "[1-5];sm",
    "[1-6];1750a48",
    "[1-8];ieee64",
])
def test_parser(text: str):
    print(f"Input: {text!r}")
    tree = parser.parse(text)
    print("Output:", tree.pretty())
    assert tree

@given(cst.measurands())
def test_measurands(measurand: str):
    print(f"Input: {measurand!r}")
    tree = parser.parse(measurand)
    assert tree
