import pytest
import math
from decom.parsers import calculate_parser as parser

PI = math.pi

@pytest.mark.parametrize("text, expect", [
    ("1.0", 1.0),
    ("1e3", 1e3),
    ("2**16", 2**16),
    ("1/2", 0.5),
    ("1/2**16", 2**-16),
    ("1/2^16", 1/2**16),
    (f"sin({PI}/2)", 1),
    (f"cos({PI}/2)", 0),
    (f"tan({PI}/4)", 1),
    (f"rad2deg({PI})", 180),
    (f"deg2rad(180)", PI),
])
def test_parser(text: str, expect: float):
    value = parser.parse(text)
    assert value == pytest.approx(expect)
