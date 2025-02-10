from lark import Transformer, v_args
import math

@v_args(inline=True)
class CalculateTree(Transformer):
    from operator import add, sub, mul, truediv as div, neg, pow
    from math import sin, cos, tan

    number = float

    def rad2deg(self, value: float) -> float:
        return 180 / math.pi * value

    def deg2rad(self, value: float) -> float:
        return math.pi / 180 * value
