from typing import Any, Optional

from lark import Token, Transformer, v_args

from decom import utils
from decom.measurand import (
    BasicParameter,
    BitOperator,
    Fragment,
    FragmentConstant,
    FragmentWord,
    GeneratorParameter,
    Iterator,
    Parameter,
    SupercomParameter,
)


@v_args(inline=True)
class ParameterTransformer(Transformer):
    integer = int

    def hex2dec(self, val: str) -> int:
        return utils.hex2dec(val)

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

    def bit_mask(self, val: int) -> list[int]:
        return utils.bit_mask(val)

    def word_spec(self, start: int, stop: Optional[int] = None) -> tuple[int, int]:
        if stop is None:
            return start, start
        return min(start, stop), max(start, stop)

    def range(self, start: int, stop: Optional[int] = None) -> list[int]:
        if stop is not None:
            return utils.irange(start, stop)
        return [start]

    def cr_fragments(self, *args) -> list[Fragment]:
        complement, reverse = False, False

        if args[0] == "~":
            complement = True
            args = args[1:]

        if args[-1] == "R":
            reverse = True
            args = args[:-1]

        for frag in args[0]:
            if not isinstance(frag, Fragment):
                raise TypeError
            frag.complement = complement
            frag.reverse = reverse
        return args[0]

    def fragments_single(self, word: int) -> list[Fragment]:
        return [FragmentWord(word=word)]

    def fragments_range(self, start: int, stop: int) -> list[Fragment]:
        return [FragmentWord(word=word) for word in utils.irange(start, stop)]

    def fragments_bits_first(self, *args) -> list[Fragment]:
        if len(args) == 2:
            start, bits = args
            stop = start
        elif len(args) == 3:
            start, bits, stop = args
        return [
            FragmentWord(word=word, bits=bits) for word in utils.irange(start, stop)
        ]

    def fragments_bits_last(self, *args) -> list[Fragment]:
        if len(args) == 2:
            start, bits = args
            stop = start
        elif len(args) == 3:
            start, stop, bits = args
        return [
            FragmentWord(word=word, bits=bits) for word in utils.irange(start, stop)
        ]

    def constant(self, token: Token) -> list[FragmentConstant]:
        # When merging transformers, the token.type will contain a prefix (e.g. "parameter__")
        if "HEX" in token.type:
            size = 4 * len(token)
            value = utils.hex2dec(token)
        elif "OCT" in token.type:
            size = 3 * len(token)
            value = utils.oct2dec(token)
        elif "BIN" in token.type:
            size = len(token)
            value = utils.bin2dec(token)
        else:
            raise ValueError
        return [FragmentConstant(value, size)]

    def concatenate(self, *args: list[list[Any]]) -> list[Any]:
        out = []
        for arg in args:
            out.extend(arg)
        return out

    def bit_op(self, mode: str, value: int) -> BitOperator:
        return BitOperator(mode=str(mode), value=value)

    def parameter(self, fragments: list[Fragment]) -> Parameter:
        return BasicParameter(fragments=fragments)

    def parameter_with_bitop(
        self, fragments: list[Fragment], bit_op: BitOperator
    ) -> Parameter:
        return BasicParameter(fragments, bit_op=bit_op)

    def supercom_parameter(
        self, fragments: list[Fragment], iterator: Iterator
    ) -> SupercomParameter:
        parameter = BasicParameter(fragments=fragments)
        return SupercomParameter(parameter, iterator=iterator)

    def supercom_parameter_with_bitop(
        self, fragments: list[Fragment], bit_op: BitOperator, iterator: Iterator
    ) -> SupercomParameter:
        parameter = BasicParameter(fragments=fragments, bit_op=bit_op)
        return SupercomParameter(parameter, iterator=iterator)

    def generator_parameter(
        self, fragments: list[Fragment], iterator: Iterator
    ) -> GeneratorParameter:
        parameter = BasicParameter(fragments=fragments)
        return GeneratorParameter(parameter=parameter, iterator=iterator)

    def generator_parameter_with_bitop(
        self, fragments: list[Fragment], iterator: Iterator, bit_op: BitOperator
    ) -> GeneratorParameter:
        parameter = BasicParameter(fragments=fragments, bit_op=bit_op)
        return GeneratorParameter(parameter=parameter, iterator=iterator)
