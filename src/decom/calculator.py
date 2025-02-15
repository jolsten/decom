import math
from typing import Union

from lark import Token, Transformer, v_args

Number = Union[int, float]


@v_args(inline=True)
class Calculator(Transformer):
    from math import (
        acos,
        asin,
        atan,
        atan2,
        ceil,
        cos,
        exp,
        floor,
        log,
        log10,
        sin,
        sqrt,
        tan,
    )
    from operator import abs, add, mul, neg, pow, sub
    from operator import truediv as div

    number = float
    max = max
    min = min
    fix = floor

    def float(self, val: Number) -> float:
        return float(val)

    def round(self, val: Number) -> int:
        return round(val)

    def constant(self, token: Token) -> float:
        if token == "E":
            return math.e
        if token == "PI":
            return math.pi

    def pi(self) -> float:
        return math.pi

    def e(self) -> float:
        return math.e

    def rad(self, value: float) -> float:
        return math.pi / 180 * value

    def deg(self, value: float) -> float:
        return 180 / math.pi * value

    def nxtwo(self, value: Number) -> int:
        return 2 ** math.ceil(math.log2(value))

    def tento(self, value: float) -> float:
        return 10**value
