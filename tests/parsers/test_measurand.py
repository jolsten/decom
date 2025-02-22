import pytest
from hypothesis import given

from decom.measurand import Measurand
from decom.parsers import measurand_parser

from . import strategies as cst

PARAMETERS = [
    "[1]",
    "[1-2]",
    "[1+2+3]",
    "[1+2+3+4]",
    "[1-4]",
    "[1-5]",
    "[1-6]",
    "[1-8]",
]

INTERPS = [
    "u",
    "sm",
    "1c",
    "2c",
    "ieee32",
    "ieee64",
    "1750a32",
    "1750a48",
    "ti32",
    "ti40",
]

EUCS = [
    "EUC[1]",
    "[1.0]",
    "EUC[1,1]",
    "[1,1,1]",
]


@pytest.mark.parametrize(
    "text",
    [
        "[1];",
        "[1-2];1c",
        "[1+2+3];2c",
        "[1+2+3+4];ieee32",
        "[1-4];1750a32",
        "[1-5];sm",
        "[1-6];1750a48",
        "[1-8];ieee64",
    ],
)
def test_parser(text: str):
    print(f"Input: {text!r}")
    tree = measurand_parser.parse(text)
    assert tree


@pytest.mark.parametrize("parameter", PARAMETERS)
def test_parameters(parameter: str):
    m = measurand_parser.parse(parameter)
    assert isinstance(m, Measurand)


@pytest.mark.parametrize("interp", INTERPS)
def test_interps(interp: str):
    measurand = f"[1];{interp}"
    m = measurand_parser.parse(measurand)
    assert isinstance(m, Measurand)


@pytest.mark.parametrize("euc", EUCS)
def test_eucs(euc: str):
    measurand = f"[1];u;{euc}"
    m = measurand_parser.parse(measurand)
    assert isinstance(m, Measurand)


@given(cst.measurands())
def test_measurands(measurand: str):
    print(f"Input: {measurand!r}")
    tree = measurand_parser.parse(measurand)
    assert tree
