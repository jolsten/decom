from dataclasses import dataclass
from lark import Transformer, v_args
from typing import Optional
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


@dataclass
class Fragment:
    word: int
    bits: Optional[int] = None
    complement: bool = False
    reverse: bool = False

    def __eq__(self, other: "Fragment") -> bool:
        bits_a = self.bits if self.bits is None else sorted(self.bits)
        bits_b = other.bits if other.bits is None else sorted(other.bits)
        return all([
            self.word == other.word,
            bits_a == bits_b,
            self.complement == other.complement,
            self.reverse == other.reverse,
        ])

@dataclass
class Iterator:
    step: int
    stop: Optional[int] = None

@dataclass
class Parameter:
    fragments: list[Fragment]
    iterator: Optional[Iterator] = None

@dataclass
class BitwiseOperator:
    operation: str
    operand: int

def expand_range(start: int, stop: int) -> list[int]:
    if start <= stop:
        return list(range(start, stop + 1))
    return list(range(start, stop - 1, -1))


@v_args(inline=True)
class ParameterTransformer(Transformer):
    integer = int

    def bit_range(self, *args) -> list[int]:
        if len(args) == 1:
            return list(args)
        elif len(args) == 2:
            return expand_range(*args)
        raise ValueError
    
    def word_range(self, *args) -> list[int]:
        if len(args) == 1:
            return list(args)
        elif len(args) == 2:
            return expand_range(*args)
        raise ValueError

    def concatenate(self, *args) -> list[int]:
        out = []
        for arg in args:
            out.extend(arg)
        return out
    
    def c_fragments(self, *args) -> list[Fragment]:
        return self.fragments(*args, complement=True)
    
    def r_fragments(self, *args) -> list[Fragment]:
        return self.fragments(*args, reverse=True)
    
    def cr_fragments(self, *args) -> list[Fragment]:
        return self.fragments(*args, complement=True, reverse=True)

    def fragments(self, *args, reverse: bool = False, complement: bool = False) -> list[Fragment]:
        word_list = args[0]
        bit_list = args[1] if len(args) == 2 else None
        fragments = [Fragment(word, bits=bit_list, complement=complement, reverse=reverse) for word in word_list]
        return fragments

    def parameter(self, *args) -> Parameter:
        fragments = args[0]
        return Parameter(fragments=fragments)
