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

    def rad(self, value: float) -> float:
        return math.pi / 180 * value

    def deg(self, value: float) -> float:
        return 180 / math.pi * value

    def nxtwo(self, value: Number) -> int:
        return 2 ** math.ceil(math.log2(value))

    def tento(self, value: float) -> float:
        return 10**value


def nxtwo(val: Number) -> int:
    return math.ceil(math.log(val, 2))


def deg(val: Number) -> float:
    return math.pi / 180 * val


def rad(val: Number) -> float:
    return 180 / math.pi * val


def tento(val: Number) -> Number:
    return 10**val


def hamdist(a: int, b: int) -> int:
    return f"{a ^ b:b}".count("1")


# There should be a way to eliminate most of the boilerplate code in the class below.
#
# Tried using a decorator assign outer functions that return the inner f(PV) function
# but it didn't work. Possibly related to how the Transformer class is interacting
# with dynamically created attributes.
#
# Tried moving the decorator until after procedurally adding the attributes after
# defining the class. Same problem. So probably not related to the v_args decorator.
@v_args(inline=True)
class PVCalculator(Transformer):
    def pv(self, _: Token) -> callable:
        def f(PV):
            return PV

        return f

    def number(self, token: Token) -> callable:
        if token.type == "INT":
            return lambda PV: int(token)
        else:
            return lambda PV: float(token)

    def constant(self, token: Token) -> float:
        if token == "E":
            return lambda PV: math.e
        if token == "PI":
            return lambda PV: math.pi
        raise ValueError

    def neg(self, a: callable) -> callable:
        def wrapper(PV):
            return -a(PV)

        return wrapper

    def float(self, a) -> callable:
        def f(PV):
            return float(a(PV))

        return f

    def integer(self, a) -> callable:
        def f(PV):
            return int(a(PV))

        return f

    fix = integer

    def add(self, a: callable, b: callable) -> callable:
        def f(PV):
            return a(PV) + b(PV)

        return f

    def sub(self, a: callable, b: callable) -> callable:
        def f(PV):
            return a(PV) - b(PV)

        return f

    def mul(self, a: callable, b: callable) -> callable:
        def f(PV):
            return a(PV) * b(PV)

        return f

    def div(self, a: callable, b: callable) -> callable:
        def f(PV):
            return a(PV) / b(PV)

        return f

    def pow(self, a: callable, b: callable) -> callable:
        def f(PV):
            return a(PV) ** b(PV)

        return f

    def exp(self, a: callable) -> callable:
        def f(PV):
            return math.e ** a(PV)

        return f

    def round(self, a: callable) -> callable:
        def f(PV):
            return round(a(PV))

        return f

    def floor(self, a: callable) -> callable:
        def f(PV):
            return math.floor(a(PV))

        return f

    def ceil(self, a: callable) -> callable:
        def f(PV):
            return math.ceil(a(PV))

        return f

    def nxtwo(self, a: callable) -> callable:
        def f(PV):
            return nxtwo(a(PV))

        return f

    def sin(self, a: callable) -> callable:
        def f(PV):
            return math.sin(a(PV))

        return f

    def cos(self, a: callable) -> callable:
        def f(PV):
            return math.cos(a(PV))

        return f

    def tan(self, a: callable) -> callable:
        def f(PV):
            return math.tan(a(PV))

        return f

    def asin(self, a: callable) -> callable:
        def f(PV):
            return math.asin(a(PV))

        return f

    def acos(self, a: callable) -> callable:
        def f(PV):
            return math.acos(a(PV))

        return f

    def atan(self, a: callable) -> callable:
        def f(PV):
            return math.atan(a(PV))

        return f

    def atan2(self, a: callable, b: callable) -> callable:
        def f(PV):
            return math.atan2(a(PV), b(PV))

        return f

    def deg(self, a: callable) -> callable:
        def f(PV):
            return a(PV) * 180 / math.pi

        return f

    def rad(self, a: callable) -> callable:
        def f(PV):
            return a(PV) * math.pi / 180

        return f

    def abs(self, a: callable) -> callable:
        def f(PV):
            return abs(a(PV))

        return f

    def tento(self, a: callable) -> callable:
        def f(PV):
            return tento(a(PV))

        return f

    def log(self, a: callable) -> callable:
        def f(PV):
            return math.log(a(PV))

        return f

    def log10(self, a: callable) -> callable:
        def f(PV):
            return math.log10(a(PV))

        return f

    def sqrt(self, a: callable) -> callable:
        def f(PV):
            return math.sqrt(a(PV))

        return f

    def hamdist(self, a: callable, b: callable) -> callable:
        def f(PV):
            return hamdist(a(PV), b(PV))

        return f

    def max(self, *args: list[callable]) -> callable:
        def f(PV):
            return max([f(PV) for f in args])

        return f

    def min(self, *args: list[callable]) -> callable:
        def f(PV):
            return min([f(PV) for f in args])

        return f

    def if_(self, a: callable, b: callable, c: callable) -> callable:
        def wrapper(PV):
            return b(PV) if a(PV) else c(PV)

        return wrapper
