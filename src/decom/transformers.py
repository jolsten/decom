import math
from typing import Any, Optional

from lark import Token, Transformer, v_args

from decom import utils
from decom.measurand import (
    BitOperator,
    Fragment,
    FragmentConstant,
    GeneratorParameter,
    Iterator,
    Measurand,
    Parameter,
    SupercomParameter,
)


@v_args(inline=True)
class CalculateTree(Transformer):
    from math import cos, sin, tan
    from operator import add, mul, neg, pow, sub
    from operator import truediv as div

    number = float

    def rad2deg(self, value: float) -> float:
        return 180 / math.pi * value

    def deg2rad(self, value: float) -> float:
        return math.pi / 180 * value


@v_args(inline=True)
class ParameterTransformer(Transformer):
    integer = int

    def hex2dec(self, val: str) -> int:
        return utils.hex2dec(str(val))

    def oct2dec(self, val: str) -> int:
        return utils.oct2dec(val)

    def bin2dec(self, val: str) -> int:
        return utils.bin2dec(val)

    def bit_range(self, *args) -> list[int]:
        if len(args) == 1:
            return list(args)
        elif len(args) == 2:
            return utils.irange(*args)
        raise ValueError

    def up_iterator(self, *args) -> Iterator:
        step = args[0]
        if len(args) == 2:
            return Iterator(step, args[1])
        return Iterator(step)

    def dn_iterator(self, *args) -> Iterator:
        step = -args[0]
        if len(args) == 2:
            return Iterator(step, args[1])
        return Iterator(step)

    def bit_mask(self, val: int) -> list[int]:
        return utils.bit_mask(val)

    def frag_range_bits_last(
        self, start: int, stop: int, bits: list[int]
    ) -> list[Fragment]:
        return [Fragment(word=word, bits=bits) for word in utils.irange(start, stop)]

    def frag_range_bits_first(
        self, start: int, bits: list[int], stop: int
    ) -> list[Fragment]:
        return [Fragment(word=word, bits=bits) for word in utils.irange(start, stop)]

    def frag_word_with_bits(self, word: int, bits: list[int]) -> list[Fragment]:
        return [Fragment(word=word, bits=bits)]

    def frag_range_no_bits(self, start: int, stop: int) -> list[Fragment]:
        return [Fragment(word=word) for word in utils.irange(start, stop)]

    def frag_word_no_bits(self, word: int) -> list[Fragment]:
        return [Fragment(word=word)]

    def frag_constant(self, token):
        if token.type == "HEX":
            size = 4 * len(token)
            value = utils.hex2dec(token)
        elif token.type == "OCT":
            size = 3 * len(token)
            value = utils.oct2dec(token)
        elif token.type == "BIN":
            size = len(token)
            value = utils.bin2dec(token)
        return [FragmentConstant(value, size)]

    def concatenate(self, *args) -> list[int]:
        out = []
        for arg in args:
            out.extend(arg)
        return out

    def complement(self, fragments: list[Fragment]) -> list[Fragment]:
        for f in fragments:
            f.complement = True
        return fragments

    def reverse(self, fragments: list[Fragment]) -> list[Fragment]:
        for f in fragments:
            f.reverse = True
        return fragments

    def complement_reverse(self, fragments: list[Fragment]) -> list[Fragment]:
        return self.complement(self.reverse(fragments))

    def bitwise_operator(self, arg: str) -> BitOperator:
        return BitOperator(mode=arg.type, value=int(arg))

    def mod_fragments(self, fragments: list[Fragment]) -> list[Fragment]:
        return fragments

    def parameter(self, fragments: list[Fragment]) -> Parameter:
        return Parameter(fragments=fragments)

    def parameter_with_mask(
        self, fragments: list[Fragment], bit_op: BitOperator
    ) -> Parameter:
        return Parameter(fragments, bit_op=bit_op)

    def supercom_parameter(
        self, parameter: Parameter, iterator: Iterator
    ) -> SupercomParameter:
        return SupercomParameter(parameter, iterator=iterator)

    def supercom_parameter_with_mask(
        self, parameter: Parameter, bit_op: BitOperator, iterator: Iterator
    ) -> SupercomParameter:
        return SupercomParameter(parameter, iterator=iterator, bit_op=bit_op)

    def generator_parameter(
        self, parameter: Parameter, iterator: Iterator
    ) -> GeneratorParameter:
        return GeneratorParameter(parameter=parameter, iterator=iterator)

    def generator_parameter_with_mask(
        self, parameter: Parameter, iterator: Iterator, bit_op: BitOperator
    ) -> GeneratorParameter:
        return GeneratorParameter(parameter=parameter, iterator=iterator, bit_op=bit_op)


class MeasurandTransformer(Transformer):
    def measurand(
        self,
        parameter: Parameter,
        interp: Optional[Any] = None,
        euc: Optional[Any] = None,
        ss: Optional[Any] = None,
    ) -> Measurand:
        return Measurand(parameter=parameter, interp=interp, euc=euc, ss=ss)

    def interp(self, token: Token) -> str:
        return str(token)
