import math

import pytest
from sympy import lambdify

from decom.parsers import symcalc_parser


@pytest.mark.parametrize(
    "text, func",
    [
        ("sin(PV)", lambda pv: math.sin(pv)),
        ("PV*1.0", lambda pv: pv * 1.0),
        ("-PV", lambda pv: -pv),
        ("PV * 1e3", lambda pv: pv * 1e3),
        ("PV*1e-3", lambda pv: pv * 1e-3),
        ("PV-1e3", lambda pv: pv - 1e3),
        ("PV*2**16", lambda pv: pv * 2**16),
        ("1/2*PV", lambda pv: pv / 2),
        ("PV/2**16", lambda pv: pv / 2**16),
        ("(1+2)*3*PV", lambda pv: pv * 9),
        ("E*PV", lambda pv: pv * math.e),
        ("PI*PV", lambda pv: pv * math.pi),
        ("float(PV)", lambda pv: pv),
        ("fix(PV/3)", lambda pv: math.floor(pv / 3)),
        ("round(PV/3)", lambda pv: round(pv / 3)),
        ("floor(PV/2)", lambda pv: math.floor(pv / 2)),
        ("ceil(PV/2)", lambda pv: math.ceil(pv / 2)),
        ("nxtwo(PV+1.5)", lambda pv: math.ceil(math.log(pv + 1.5) / math.log(2))),
        ("PV*sin(PI/2)", lambda pv: pv),
        ("PV*cos(PI/2)", lambda pv: pv * 0),
        ("PV*tan(PI/4)", lambda pv: pv * 1),
        ("asin(1)/(PV+100)", lambda pv: math.pi / 2 / (pv + 100)),
        ("PV*acos(0)", lambda pv: pv * math.pi / 2),
        ("PV*atan(1)", lambda pv: pv * math.pi / 4),
        ("PV*atan2(1e-9,0)", lambda pv: pv * math.pi / 2),
        ("atan2(PV,sqrt(3)/2)", lambda pv: math.atan2(pv, math.sqrt(3) / 2)),
        ("deg(PV)", lambda pv: 180 / math.pi * pv),
        ("rad(PV)", lambda pv: pv * math.pi / 180),
        ("abs(PV)", lambda pv: abs(pv)),
        ("abs(-PV)", lambda pv: abs(-pv)),
        ("exp(PV)", lambda pv: math.e**pv),
        ("tento(PV)", lambda pv: 10**pv),
        ("ln(PV+1)", lambda pv: math.log(pv + 1)),
        ("log(PV+1)", lambda pv: math.log10(pv + 1)),
        ("PV*sqrt(4)", lambda pv: pv * 2),
    ],
)
def test_symcalc(text: str, func: callable):
    expression = symcalc_parser.parse(text)
    f = lambdify(["PV"], expression)
    for pv in range(10):
        expected = func(pv)
        print("pv =", pv)
        print(f"expected = {expected}")
        print(expression)
        print("f(pv) =", f(pv))
        print(expression.evalf(subs={"PV": pv}))
        assert expression.evalf(subs={"PV": pv}) == pytest.approx(expected)
