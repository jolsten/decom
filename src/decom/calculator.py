import math
from typing import Callable, Union

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
    return 180 / math.pi * val


def rad(val: Number) -> float:
    return math.pi / 180 * val


def tento(val: Number) -> Number:
    return 10**val


def hamdist(a: int, b: int) -> int:
    return f"{a ^ b:b}".count("1")


CN = Union[Number, Callable]


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

    def number(self, token: Token) -> Number:
        if token.type == "INT":
            return int(token)
        else:
            return float(token)

    def constant(self, token: Token) -> float:
        if token == "E":
            return math.e
        if token == "PI":
            return math.pi
        raise ValueError

    def neg(self, a: CN) -> CN:
        if isinstance(a, Callable):

            def wrapper(PV):
                return -a(PV)

            return wrapper
        return -a

    def float(self, a: CN) -> CN:
        if isinstance(a, Callable):

            def f(PV):
                return float(a(PV))

            return f
        return float(a)

    def integer(self, a: CN) -> CN:
        if isinstance(a, Callable):

            def f(PV):
                return int(a(PV))

            return f
        return int(a)

    fix = integer

    def add(self, a: CN, b: CN) -> CN:
        if isinstance(a, Callable) and isinstance(b, Callable):

            def f(PV):
                return a(PV) + b(PV)

            return f
        elif isinstance(a, Callable):

            def f(PV):
                return a(PV) + b

            return f
        elif isinstance(b, Callable):

            def f(PV):
                return a + b(PV)

            return f
        return a + b

    def sub(self, a: CN, b: CN) -> CN:
        if isinstance(a, Callable) and isinstance(b, Callable):

            def f(PV):
                return a(PV) - b(PV)

            return f
        elif isinstance(a, Callable):

            def f(PV):
                return a(PV) - b

            return f
        elif isinstance(b, Callable):

            def f(PV):
                return a - b(PV)

            return f
        return a - b

    def mul(self, a: CN, b: CN) -> CN:
        if isinstance(a, Callable) and isinstance(b, Callable):

            def f(PV):
                return a(PV) * b(PV)

            return f
        elif isinstance(a, Callable):

            def f(PV):
                return a(PV) * b

            return f
        elif isinstance(b, Callable):

            def f(PV):
                return a * b(PV)

            return f
        return a * b

    def div(self, a: CN, b: CN) -> CN:
        if isinstance(a, Callable) and isinstance(b, Callable):

            def f(PV):
                return a(PV) / b(PV)

            return f
        elif isinstance(a, Callable):

            def f(PV):
                return a(PV) / b

            return f
        elif isinstance(b, Callable):

            def f(PV):
                return a / b(PV)

            return f
        return a / b

    def pow(self, a: CN, b: CN) -> CN:
        if isinstance(a, Callable) and isinstance(b, Callable):

            def f(PV):
                return a(PV) ** b(PV)

            return f
        elif isinstance(a, Callable):

            def f(PV):
                return a(PV) ** b

            return f
        elif isinstance(b, Callable):

            def f(PV):
                return a ** b(PV)

            return f
        return a**b

    def exp(self, a: callable) -> callable:
        if isinstance(a, Callable):

            def f(PV):
                return math.e ** a(PV)

            return f
        return math.e**a

    def round(self, a: CN) -> CN:
        if isinstance(a, Callable):

            def f(PV):
                return round(a(PV))

            return f
        return round(a)

    def floor(self, a: CN) -> CN:
        if isinstance(a, Callable):

            def f(PV):
                return math.floor(a(PV))

            return f
        return math.floor(a)

    def ceil(self, a: CN) -> CN:
        if isinstance(a, Callable):

            def f(PV):
                return math.ceil(a(PV))

            return f
        return math.ceil(a)

    def nxtwo(self, a: callable) -> callable:
        if isinstance(a, Callable):

            def f(PV):
                return nxtwo(a(PV))

            return f
        return nxtwo(a)

    def sin(self, a: callable) -> callable:
        if isinstance(a, Callable):

            def f(PV):
                return math.sin(a(PV))

            return f
        return math.sin(a)

    def cos(self, a: callable) -> callable:
        if isinstance(a, Callable):

            def f(PV):
                return math.cos(a(PV))

            return f
        return math.cos(a)

    def tan(self, a: callable) -> callable:
        if isinstance(a, Callable):

            def f(PV):
                return math.tan(a(PV))

            return f
        return math.tan(a)

    def asin(self, a: callable) -> callable:
        if isinstance(a, Callable):

            def f(PV):
                return math.asin(a(PV))

            return f
        return math.asin(a)

    def acos(self, a: callable) -> callable:
        if isinstance(a, Callable):

            def f(PV):
                return math.acos(a(PV))

            return f
        return math.acos(a)

    def atan(self, a: callable) -> callable:
        if isinstance(a, Callable):

            def f(PV):
                return math.atan(a(PV))

            return f
        return math.atan(a)

    def atan2(self, a: callable, b: callable) -> CN:
        if isinstance(a, Callable) and isinstance(b, Callable):

            def f(PV):
                return math.atan2(a(PV), b(PV))

            return f
        elif isinstance(a, Callable):

            def f(PV):
                return math.atan2(a(PV), b)

            return f
        elif isinstance(b, Callable):

            def f(PV):
                return math.atan2(a, b(PV))

            return f
        return math.atan2(a, b)

    def deg(self, a: callable) -> callable:
        if isinstance(a, Callable):

            def f(PV):
                return deg(a(PV))

            return f
        return deg(a)

    def rad(self, a: callable) -> callable:
        if isinstance(a, Callable):

            def f(PV):
                return rad(a(PV))

            return f
        return rad(a)

    def abs(self, a: callable) -> callable:
        if isinstance(a, Callable):

            def f(PV):
                return abs(a(PV))

            return f
        return abs(a)

    def tento(self, a: callable) -> callable:
        if isinstance(a, Callable):

            def f(PV):
                return tento(a(PV))

            return f
        return tento(a)

    def log(self, a: callable) -> callable:
        if isinstance(a, Callable):

            def f(PV):
                return math.log(a(PV))

            return f
        return math.log(a)

    def log10(self, a: callable) -> callable:
        if isinstance(a, Callable):

            def f(PV):
                return math.log10(a(PV))

            return f
        return math.log10(a)

    def sqrt(self, a: callable) -> callable:
        if isinstance(a, Callable):

            def f(PV):
                return math.sqrt(a(PV))

            return f
        return math.sqrt(a)

    def hamdist(self, a: callable, b: callable) -> callable:
        if isinstance(a, Callable) and isinstance(b, Callable):

            def f(PV):
                return hamdist(a(PV), b(PV))

            return f
        elif isinstance(a, Callable):

            def f(PV):
                return hamdist(a(PV), b)

            return f
        elif isinstance(b, Callable):

            def f(PV):
                return hamdist(a, b(PV))

            return f
        return hamdist(a, b)

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
