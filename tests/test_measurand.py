from typing import Optional, Literal, Union
import pytest
from hypothesis import strategies as st, given
from decom.parsers import measurand_parser as parser

VALID_INTERPS = [
    "u",
    "sm",
    "1c",
    "2c",
    "ieee32",
    "ieee64",
    "1750a32",
    "1750a48",
]

@st.composite
def parameters(draw, max_components: int = 8, max_value: int = 256, style: Optional[Literal["+", "-"]] = None):
    size = draw(st.integers(min_value=1, max_value=max_components))
    first = draw(st.integers(min_value=1, max_value=max_value-size))
    
    if style is None:
        style = draw(st.sampled_from(["+", "-"]))
    
    if style == "+":
        values = list(range(first, first+size))
        return "+".join([str(v) for v in values])
    elif style == "-":
        return f"{first}-{first+size-1}"
    raise ValueError


@st.composite
def interps(draw) -> Union[None, str]:
    return draw(st.sampled_from([None] + VALID_INTERPS))


@st.composite
def measurands(draw):
    p = draw(parameters())
    i = draw(interps())

    m = f"[{p}]"
    if i is not None:
        m += f";{i}"
    
    return m

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
