from typing import Optional, Literal, Union
from hypothesis import strategies as st

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
def eucs(draw) -> Union[None, list[str]]:
    floats = st.floats(allow_nan=False, allow_infinity=False)
    args = draw(st.lists(floats, min_size=0, max_size=3))

    s = ""
    if draw(st.booleans()):
        s = "EUC"

    if len(args):
        return f"""{s}[{",".join([str(x) for x in args])}]"""
    return None

@st.composite
def measurands(draw, with_interp: bool = True, with_euc: bool = True):
    p = draw(parameters())
    i = draw(interps()) if with_interp else None
    e = draw(eucs()) if with_euc else None

    m = f"[{p}]"
    if i:
        m += f";{i}"

        if e:
            m += f";{e}"

    return m
