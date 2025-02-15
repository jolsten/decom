import math

import pytest

from decom.parsers import symcalc_parser


@pytest.mark.parametrize(
    "text, func",
    [
        ("sin(PV)", lambda pv: math.sin(pv)),
    ],
)
def test_symcalc(text: str, func: callable):
    expression = symcalc_parser.parse(text)
    for pv in range(10):
        assert expression.evalf(subs={"PV": pv}) == pytest.approx(func(pv))
