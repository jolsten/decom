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

    def bit_ops(self, *args):
        print("")
        print(args)
        return args

    def bit_mask(self, val: int) -> list[int]:
        return utils.bit_mask(val)

    def range(self, start: int, stop: Optional[int] = None) -> list[int]:
        if stop is not None:
            return utils.irange(start, stop)
        return [start]

    def cr_fragments(self, *args) -> list[Fragment]:
        print("cr_fragments", args)
        complement, reverse = False, False

        if args[0] == "~":
            complement = True
            args = args[1:]

        if args[-1] == "R":
            reverse = True
            args = args[:-1]

        for frag in args[0]:
            frag: Fragment
            frag.complement = complement
            frag.reverse = reverse
        return args[0]

    def fragments_single(self, word: int) -> list[Fragment]:
        return [Fragment(word=word)]

    def fragments_range(self, start: int, stop: int) -> list[Fragment]:
        return [Fragment(word=word) for word in utils.irange(start, stop)]

    def fragments_bits_first(self, *args) -> list[Fragment]:
        if len(args) == 2:
            start, bits = args
            stop = start
        elif len(args) == 3:
            start, bits, stop = args
        return [Fragment(word=word, bits=bits) for word in utils.irange(start, stop)]

    def fragments_bits_last(self, *args) -> list[Fragment]:
        if len(args) == 2:
            start, bits = args
            stop = start
        elif len(args) == 3:
            start, stop, bits = args
        return [Fragment(word=word, bits=bits) for word in utils.irange(start, stop)]

    def constant(self, token: Token) -> list[FragmentConstant]:
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

    def concatenate(self, *args: list[list[Any]]) -> list[Any]:
        out = []
        for arg in args:
            out.extend(arg)
        return out

    def bit_op(self, mode: str, value: int) -> BitOperator:
        return BitOperator(mode=str(mode), value=value)

    def parameter(self, fragments: list[Fragment]) -> Parameter:
        return Parameter(fragments=fragments)

    def parameter_with_bitop(
        self, fragments: list[Fragment], bit_op: BitOperator
    ) -> Parameter:
        return Parameter(fragments, bit_op=bit_op)

    def supercom_parameter(
        self, parameter: Parameter, iterator: Iterator
    ) -> SupercomParameter:
        return SupercomParameter(parameter, iterator=iterator)

    def supercom_parameter_with_bitop(
        self, parameter: Parameter, bit_op: BitOperator, iterator: Iterator
    ) -> SupercomParameter:
        return SupercomParameter(parameter, iterator=iterator, bit_op=bit_op)

    def generator_parameter(
        self, parameter: Parameter, iterator: Iterator
    ) -> GeneratorParameter:
        return GeneratorParameter(parameter=parameter, iterator=iterator)

    def generator_parameter_with_bitop(
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

    def euc(self, token: Token) -> str:
        print(token)
        return token
