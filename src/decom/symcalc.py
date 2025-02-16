import sympy
from lark import Token, v_args

from decom.calculator import Calculator

PV = sympy.symbols("PV")


@v_args(inline=True)
class PVCalculator(Calculator):
    from operator import abs, add, mul, neg, pow, sub
    from operator import truediv as div

    from sympy import (
        acos,
        asin,
        atan,
        atan2,
        cos,
        exp,
        floor,
        log,
        sin,
        tan,
    )
    from sympy import (
        ceiling as ceil,
    )

    def pv(self, _: Token) -> sympy.Symbol:
        return PV

    def float(self, v):
        return sympy.Float(v)
        # raise NotImplementedError

    fix = floor

    def round(self, v):
        raise NotImplementedError

    def nxtwo(self, v):
        return sympy.ceiling(sympy.log(v, 2))

    def sqrt(self, v):
        return v ** (1 / 2)

    def log10(self, v):
        return sympy.log(v, 10)

    def rad(self, v):
        return sympy.pi / 180 * v

    def deg(self, v):
        return 180 / sympy.pi * v

    def tento(self, v):
        return 10**v

    def min(self, *args):
        return sympy.Min(args)

    def max(self, *args):
        return sympy.Max(args)

    # | "float"i "(" sum ")" -> float
    # | "fix"i   "(" sum ")" -> fix
    # | "round"i "(" sum ")" -> round
    # | "floor"i "(" sum ")" -> floor
    # | "ceil"i  "(" sum ")" -> ceil
    # | "nxtwo"i "(" sum ")" -> nxtwo
    # | "sin"i   "(" sum ")" -> sin
    # | "cos"i   "(" sum ")" -> cos
    # | "tan"i   "(" sum ")" -> tan
    # | "asin"i  "(" sum ")" -> asin
    # | "acos"i  "(" sum ")" -> acos
    # | "atan"i  "(" sum ")" -> atan
    # | "atan2"i "(" sum "," sum ")" -> atan2
    # | "deg"i   "(" sum ")" -> deg
    # | "rad"i   "(" sum ")" -> rad
    # | "abs"i   "(" sum ")" -> abs
    # | "exp"i   "(" sum ")" -> exp
    # | "tento"i "(" sum ")" -> tento
    # | "ln"i    "(" sum ")" -> log
    # | "log"i   "(" sum ")" -> log10
    # | "sqrt"i  "(" sum ")" -> sqrt
    # | "max"i   "(" _csv{sum} ")" -> max
    # | "min"i   "(" _csv{sum} ")" -> min

    # | "hamdist"i "(" sum "," sum ")" -> hamdist
