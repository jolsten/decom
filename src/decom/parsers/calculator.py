import math
from typing import Callable, Union

from lark import Token, Transformer, v_args

Number = Union[int, float]

CN = Union[Number, Callable]


def nxtwo(val: Number) -> int:
    return 2 ** math.ceil(math.log(val, 2))


def deg(val: Number) -> float:
    return 180 / math.pi * val


def rad(val: Number) -> float:
    return math.pi / 180 * val


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
class CalculatorTransformer(Transformer):
    def pv(self, _: Token) -> CN:
        def f(PV):
            return PV

        return f

    def number(self, token: Token) -> Number:
        try:
            return int(token)
        except ValueError:
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

    def exp(self, a: CN) -> CN:
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

    def nxtwo(self, a: CN) -> CN:
        if isinstance(a, Callable):

            def f(PV):
                return nxtwo(a(PV))

            return f
        return nxtwo(a)

    def sin(self, a: CN) -> CN:
        if isinstance(a, Callable):

            def f(PV):
                return math.sin(a(PV))

            return f
        return math.sin(a)

    def cos(self, a: CN) -> CN:
        if isinstance(a, Callable):

            def f(PV):
                return math.cos(a(PV))

            return f
        return math.cos(a)

    def tan(self, a: CN) -> CN:
        if isinstance(a, Callable):

            def f(PV):
                return math.tan(a(PV))

            return f
        return math.tan(a)

    def asin(self, a: CN) -> CN:
        if isinstance(a, Callable):

            def f(PV):
                return math.asin(a(PV))

            return f
        return math.asin(a)

    def acos(self, a: CN) -> CN:
        if isinstance(a, Callable):

            def f(PV):
                return math.acos(a(PV))

            return f
        return math.acos(a)

    def atan(self, a: CN) -> CN:
        if isinstance(a, Callable):

            def f(PV):
                return math.atan(a(PV))

            return f
        return math.atan(a)

    def atan2(self, a: CN, b: CN) -> CN:
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

    def deg(self, a: CN) -> CN:
        if isinstance(a, Callable):

            def f(PV):
                return deg(a(PV))

            return f
        return deg(a)

    def rad(self, a: CN) -> CN:
        if isinstance(a, Callable):

            def f(PV):
                return rad(a(PV))

            return f
        return rad(a)

    def abs(self, a: CN) -> CN:
        if isinstance(a, Callable):

            def f(PV):
                return abs(a(PV))

            return f
        return abs(a)

    def tento(self, a: CN) -> CN:
        if isinstance(a, Callable):

            def f(PV):
                return tento(a(PV))

            return f
        return tento(a)

    def log(self, a: CN) -> CN:
        if isinstance(a, Callable):

            def f(PV):
                return math.log(a(PV))

            return f
        return math.log(a)

    def log10(self, a: CN) -> CN:
        if isinstance(a, Callable):

            def f(PV):
                return math.log10(a(PV))

            return f
        return math.log10(a)

    def sqrt(self, a: CN) -> CN:
        if isinstance(a, Callable):

            def f(PV):
                return math.sqrt(a(PV))

            return f
        return math.sqrt(a)

    def hamdist(self, a: CN, b: CN) -> CN:
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

    def max(self, *args: list[CN]) -> CN:
        if any([isinstance(a, Callable) for a in args]):

            def f(PV):
                a = [f(PV) for f in args if isinstance(f, Callable)]
                b = [x for x in args if not isinstance(x, Callable)]
                return max(a + b)

            return f

        return max(args)

    def min(self, *args: list[CN]) -> CN:
        if any([isinstance(a, Callable) for a in args]):

            def f(PV):
                a = [f(PV) for f in args if isinstance(f, Callable)]
                b = [x for x in args if not isinstance(x, Callable)]
                return min(a + b)

            return f

        return min(args)

    def if_(self, a: CN, b: CN, c: CN) -> CN:
        args = [a, b, c]
        if any(isinstance(x, Callable) for x in args):

            def f(PV):
                vals = []
                for x in args:
                    if isinstance(x, Callable):
                        vals.append(x(PV))
                    else:
                        vals.append(x)
                a, b, c = vals
                return b if a > 0 else c

            return f

        return b if a > 0 else c
