import copy
from dataclasses import dataclass, field
from typing import Any, Callable, Literal, Optional, Union

import numpy as np
from lark import Token, Transformer, v_args

from decom import utils
from decom.array import UintXArray


class UnknownSizeException(ValueError):
    pass


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
    _size: int = field(init=False, repr=False)

    def __post_init__(self) -> None:
        self._idx = self.word
        if self.one_based:
            self._idx += -1

        # self._calculate_size()

        if self.bits is not None:
            self._mask, self._shift = utils.bits_to_mask_and_shift(self.bits)

    def __str__(self) -> str:
        if self.bits:
            s = f"{self.word}:{self.bits[0]}-{self.bits[1]}"
        else:
            s = f"{self.word}"

        if self.complement:
            s = "~" + s

        if self.reverse:
            s = s + "R"

        return s

    # def size(self) -> int:
    #     try:
    #         return self._size
    #     except AttributeError as err:
    #         msg = "Fragment size is not known, probably because word_size was not specified"
    #         raise UnknownSizeException(msg) from err

    # def _calculate_size(self, word_size: Optional[int] = None) -> None:
    #     if self.bits is not None:
    #         self._size = max(self.bits) - min(self.bits) + 1
    #     elif word_size is not None:
    #         self._size = word_size

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

        if self.word_size is None:
            self.word_size = data.word_size

        if self.bits is not None:
            if self.word_size != data.word_size:
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

    def __str__(self) -> str:
        if self.size % 4 == 0:
            s = f"{self.value:x}"
        elif self.size % 3 == 0:
            s = f"{self.value:o}"
        else:
            s = f"{self.value:b}"

        if self.complement:
            s = "~" + s

        if self.reverse:
            s = s + "R"

        return s

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
    _func: Callable = field(init=False, repr=False)

    def __str__(self) -> str:
        return self.mode + " " + value_to_constant(self.value)

    def __post_init__(self) -> None:
        self.mode = self.mode.upper()
        if self.mode == "AND":
            self._func = np.bitwise_and
        elif self.mode == "OR":
            self._func = np.bitwise_or
        elif self.mode == "XOR":
            self._func = np.bitwise_xor
        else:
            raise ValueError


def value_to_constant(value: int, size: Optional[int] = None) -> str:
    if size is None:
        size = len(f"{value:b}")

    if size % 4 == 0:
        return f"x{value:0{size // 4}X}"
    elif size % 3 == 0:
        return f"o{value:0{size // 3}o}"
    return f"b{value:0{size}b}"


@dataclass
class BasicParameter(Parameter):
    fragments: list[Fragment]
    bit_op: Optional[BitOperator] = None

    def __str__(self) -> str:
        s = "[" + "+".join(str(f) for f in self.fragments) + "]"

        if self.bit_op:
            s = s + " " + str(self.bit_op)

        return s

    def _calculate_parameter_size(self, word_size: int) -> int:
        size = 0
        for frag in self.fragments:
            if isinstance(frag, FragmentConstant):
                size += frag.size
            elif isinstance(frag, FragmentWord):
                if frag.bits is None:
                    size += word_size
                else:
                    size += (frag.bits[1] - frag.bits[0]) + 1
            else:
                msg = f"expected Fragment subclass, but got {type(frag)}"
                raise TypeError(msg)
        return size

    def _all_words(self) -> list[int]:
        return [f.word for f in self.fragments if isinstance(f, FragmentWord)]

    def max_word(self) -> int:
        return max(self._all_words())

    def min_word(self) -> int:
        return min(self._all_words())

    def build(self, data: UintXArray) -> UintXArray:
        # Determine the total number of bits in the complete Parameter
        # Set the uint dtype to the minimum sized container for the Parameter size
        size = self._calculate_parameter_size(data.word_size)
        dtype = utils.word_size_to_uint(size)

        # Initialize the result vector with the necessary dtype
        result = np.zeros(data.shape[0], dtype=dtype)

        for frag_idx, frag in enumerate(self.fragments):
            # Determine the fragment size
            if isinstance(frag, FragmentConstant):
                frag_size = frag.size
            elif isinstance(frag, FragmentWord):
                if frag.bits is None:
                    frag_size = data.word_size
                else:
                    frag_size = (frag.bits[1] - frag.bits[0]) + 1

            # Shift the previous result left by the current fragment size
            if frag_idx != 0:
                result = np.left_shift(result, frag_size)

            # Add the fragment value
            result += frag.build(data)

        # TODO: Bit operations
        if self.bit_op:
            result = self.bit_op._func(result, self.bit_op.value)

        return result


@dataclass
class SupercomParameter(Parameter):
    parameter: BasicParameter
    iterator: Iterator
    word_size: Optional[int] = None


@dataclass
class GeneratorParameter(Parameter):
    parameter: BasicParameter
    iterator: Iterator
    word_size: Optional[int] = None

    _parameters: list[BasicParameter] = field(default_factory=list, repr=False)

    def __post_init__(self) -> None:
        print(self)
        if self.iterator.stop:
            self._generate_parameters()

    def _generate_parameters(self):
        self._parameters = [copy.deepcopy(self.parameter)]
        max_word = self._parameters[-1].max_word()
        while True:
            parameter = copy.deepcopy(self._parameters[-1])

            max_word += self.iterator.step

            if self.iterator.step > 0:
                if max_word >= self.iterator.stop:
                    break
            elif self.iterator.step < 0:
                if max_word <= self.iterator.stop:
                    break

            for frag in parameter.fragments:
                frag.word += self.iterator.step
                frag._idx += self.iterator.step

            self._parameters.append(parameter)

    # def _generate_parameters_up(self):
    #     self._parameters = [copy.deepcopy(self.parameter)]
    #     max_word = self._parameters[-1].max_word()
    #     while max_word < self.iterator.stop:
    #         parameter = self._parameters[-1]

    #         for frag in parameter.fragments:
    #             frag.word += self.iterator.step
    #             frag._idx += self.iterator.step

    #         max_word += self.iterator.step

    # def _generate_parameters_dn(self):
    #     self._parameters = [copy.deepcopy(self.parameter)]
    #     max_word = self._parameters[-1].max_word()
    #     while max_word > self.iterator.stop:
    #         parameter = self._parameters[-1]

    #         for frag in parameter.fragments:
    #             frag.word += self.iterator.step
    #             frag._idx += self.iterator.step

    #         max_word += self.iterator.step

    def build(self, data: UintXArray) -> list[UintXArray]:
        if self.word_size is None:
            self.word_size = data.word_size
        elif self.word_size != data.word_size:
            raise ValueError


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
