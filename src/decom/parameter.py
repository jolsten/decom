from dataclasses import dataclass, field
from typing import Any, Literal, Optional, Union

import numpy as np
from lark import Token, Transformer, v_args

from decom import utils
from decom.array import UintXArray


class Fragment:
    pass


class Parameter:
    pass


@dataclass
class FragmentWord(Fragment):
    word: int
    bits: Optional[tuple[int, int]] = None
    complement: bool = False
    reverse: bool = False
    word_size: Optional[int] = None
    one_based: bool = True

    _idx: int = field(init=False, repr=False)
    _mask: int = field(init=False, repr=False)
    _shift: int = field(init=False, repr=False)

    def __post_init__(self) -> None:
        self._idx = self.word
        if self.one_based:
            self._idx += -1

        if self.bits is not None:
            self._mask, self._shift = utils.bits_to_mask_and_shift(self.bits)

    def __eq__(self, other) -> bool:
        if isinstance(other, FragmentWord):
            bits_a = self.bits if self.bits is None else sorted(self.bits)
            bits_b = other.bits if other.bits is None else sorted(other.bits)
            return all(
                [
                    self.word == other.word,
                    bits_a == bits_b,
                    self.complement == other.complement,
                    self.reverse == other.reverse,
                ]
            )
        return NotImplemented

    def build(self, data: UintXArray) -> UintXArray:
        result = data[:, self._idx].flatten()

        if self.bits is not None:
            if self.word_size is not None and self.word_size != data.word_size:
                msg = f"data.word_size={data.word_size} does not match fragment.word_size={self.word_size}"
                raise ValueError(msg)

            result = np.bitwise_and(result, self._mask)
            result = np.bitwise_right_shift(result, self._shift)

            frag_size = abs(self.bits[1] - self.bits[0]) + 1
        else:
            frag_size = data.word_size

        if self.complement:
            # TODO: Should this really come after the bit slicing above, or should it be before???
            result = np.bitwise_and(np.invert(result), 2**frag_size - 1)

        if self.reverse:
            result = utils.reverse_bits(result, frag_size)

        return result


@dataclass
class FragmentConstant(Fragment):
    value: Union[int, np.unsignedinteger]
    size: int
    complement: bool = False
    reverse: bool = False

    def __post_init__(self) -> None:
        if self.value < 0:
            msg = f"FragmentConstant(value={self.value}) value must be positive"
            raise ValueError(msg)
        elif self.value < 2**8:
            self.value = np.uint8(self.value)
        elif self.value < 2**16:
            self.value = np.uint16(self.value)
        elif self.value < 2**32:
            self.value = np.uint32(self.value)
        elif self.value < 2**64:
            self.value = np.uint64(self.value)
        else:
            msg = f"FragmentConstant(value={self.value}) value exceeds 2**64-1"
            raise ValueError(msg)

        if self.complement:
            self.value = np.bitwise_and(np.invert(self.value), 2**self.size - 1)

        if self.reverse:
            self.value = utils.reverse_bits(self.value, self.size)

    def build(self, data: UintXArray) -> np.unsignedinteger:
        return self.value


@dataclass
class Iterator:
    step: int
    stop: Optional[int] = None


@dataclass
class BitOperator:
    mode: Literal["AND", "OR", "XOR"]
    value: int


@dataclass
class BasicParameter(Parameter):
    fragments: list[Fragment]
    bit_op: Optional[BitOperator] = None

    def build(self, data: UintXArray) -> UintXArray:
        size = 0
        for frag in self.fragments:
            if isinstance(frag, FragmentConstant):
                size += frag.size
            elif isinstance(frag, FragmentWord):
                if frag.bits is None:
                    size += data.word_size
                else:
                    size += (frag.bits[1] - frag.bits[0]) + 1
            else:
                raise TypeError
        dtype = utils.word_size_to_uint(size)

        result = np.zeros(data.shape[0], dtype=dtype)
        for frag in self.fragments:
            if isinstance(frag, FragmentConstant):
                frag_size = frag.size
            elif isinstance(frag, FragmentWord):
                if frag.bits is None:
                    frag_size = data.word_size
                else:
                    frag_size = (frag.bits[1] - frag.bits[0]) + 1

            result = np.left_shift(result, frag_size)
            result += frag.build(data)

        return result


@dataclass
class SupercomParameter(Parameter):
    parameter: Parameter
    iterator: Iterator
    bit_op: Optional[BitOperator] = None


@dataclass
class GeneratorParameter(Parameter):
    parameter: Parameter
    iterator: Iterator
    bit_op: Optional[BitOperator] = None


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
            frag: Fragment
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
        return BasicParameter(fragments=fragments)

    def parameter_with_bitop(
        self, fragments: list[Fragment], bit_op: BitOperator
    ) -> Parameter:
        return BasicParameter(fragments, bit_op=bit_op)

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
