import math

import pytest

from decom.parsers import calculator_parser

PI = math.pi


@pytest.mark.parametrize(
    "text, expect",
    [
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
        ("float(123456)", 123456.0),
        ("fix(1.2345)", 1),
        ("round(1.5)", 2),
        ("floor(1.5)", 1),
        ("ceil(1.2345)", 2),
        ("nxtwo(15)", 16),
        ("sin(PI/2)", 1),
        ("cos(PI/2)", 0),
        ("tan(PI/4)", 1),
        ("asin(1)", PI / 2),
        ("acos(0)", PI / 2),
        ("atan(1)", PI / 4),
        ("atan2(0,0)", 0),
        ("atan2(1/2,sqrt(3)/2)", 30 * PI / 180),
        ("deg(PI)", 180),
        ("rad(180)", PI),
        ("abs(1)", 1),
        ("abs(-1)", 1),
        ("exp(2)", math.e**2),
        ("tento(4)", 10_000),
        ("ln(E)", 1),
        ("log(100)", 2),
        ("sqrt(4)", 2),
    ],
)
def test_parser(text: str, expect: float):
    value = calculator_parser.parse(text)
    assert value == pytest.approx(expect)


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
        ("nxtwo(PV+1.5)", lambda pv: 2 ** math.ceil(math.log(pv + 1.5) / math.log(2))),
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
def test_callable_parser(text: str, func: callable):
    out = calculator_parser.parse(text)
    for pv in range(10):
        assert func(pv) == pytest.approx(out(pv))
