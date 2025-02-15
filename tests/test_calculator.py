import math

import pytest

from decom.parsers import calculate_parser as parser

PI = math.pi


@pytest.mark.parametrize(
    "text, expect",
    [
        # | "-" atom -> neg
        # | "(" sum ")"
        ("1.0", 1.0),
        ("-1.0", -1.0),
        ("1e3", 1e3),
        ("1e-3", 1e-3),
        ("-1e3", -1e3),
        ("2**16", 2**16),
        ("1/2", 0.5),
        ("1/2**16", 2**-16),
        ("(1+2)*3", 9),
        ("E", math.e),
        ("PI", math.pi),
        # | "float"i "(" sum ")" -> float
        # | "fix"i "(" sum ")" -> fix
        # | "round"i "(" sum ")" -> round
        # | "floor"i "(" sum ")" -> floor
        # | "ceil"i "(" sum ")" -> ceil
        # | "nxtwo"i "(" sum ")" -> nxtwo
        ("float(123456)", 123456.0),
        ("fix(1.2345)", 1),
        ("round(1.5)", 2),
        ("floor(1.5)", 1),
        ("ceil(1.2345)", 2),
        ("nxtwo(15)", 16),
        # | "sin"i "(" sum ")" -> sin
        # | "cos"i "(" sum ")" -> cos
        # | "tan"i "(" sum ")" -> tan
        # | "asin"i "(" sum ")" -> asin
        # | "acos"i "(" sum ")" -> acos
        # | "atan"i "(" sum ")" -> atan
        # | "atan2"i "(" sum "," sum ")" -> atan2
        ("sin(PI/2)", 1),
        ("cos(PI/2)", 0),
        ("tan(PI/4)", 1),
        ("asin(1)", PI / 2),
        ("acos(0)", PI / 2),
        ("atan(1)", PI / 4),
        ("atan2(0,0)", 0),
        ("atan2(1/2,sqrt(3)/2)", 30 * PI / 180),
        # | "deg"i "(" sum ")" -> deg
        # | "rad"i "(" sum ")" -> rad
        ("deg(PI)", 180),
        ("rad(180)", PI),
        # | "abs"i "(" sum ")" -> abs
        # | "exp"i "(" sum ")" -> exp
        # | "tento"i "(" sum ")" -> tento
        # | "ln"i "(" sum ")" -> log
        # | "log"i "(" sum ")" -> log10
        # | "sqrt"i "(" sum ")" -> sqrt
        ("abs(1)", 1),
        ("abs(-1)", 1),
        ("exp(2)", math.e**2),
        ("tento(4)", 10_000),
        ("ln(E)", 1),
        ("log(100)", 2),
        ("sqrt(4)", 2),
        # | "max"i "(" _csv{sum} ")" -> max
        # | "min"i "(" _csv{sum} ")" -> min
        # | "hamdist"i "(" sum "," sum ")" -> hamdist
    ],
)
def test_parser(text: str, expect: float):
    value = parser.parse(text)
    assert value == pytest.approx(expect)
