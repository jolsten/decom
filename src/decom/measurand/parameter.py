import abc
from dataclasses import dataclass, field
from typing import Any, Callable, Literal, Optional, Union, override

import numpy as np
from lark import Token, Transformer, v_args

from decom import utils
from decom.model import VarUIntArray


class UnknownSizeException(ValueError):
    pass


class Fragment(abc.ABC):
    complement: bool
    reverse: bool

    def build(self, data: VarUIntArray, /, offset: int = 0) -> VarUIntArray:
        """Build the specified Fragment.

        Notes
        -----
        For `FragmentWord`, extract the bits specified by `Fragment.bits`
        from the word (column) specified by `Fragment.word`.

        For `FragmentConstant`, build a constant scalar of the appropriate size.

        Parameters
        ----------
        data
            The input data array. This should be a 2-D array with a `word_size` attribute.

        Returns
        -------
        VarUIntArray
            The constructed fragment.
        """


class Parameter:
    pass


@dataclass
class FragmentWord(Fragment):
    word: int
    bits: Optional[list[int]] = None
    complement: bool = False
    reverse: bool = False
    word_size: Optional[int] = None

    one_based: bool = True

    _mask_shift: list[tuple[int, int]] = field(init=False, repr=False)

    def __post_init__(self) -> None:
        if self.bits is not None:
            self._bit_ranges = utils.bit_list_to_ranges(self.bits)
            self._mask_shift = []
            for bit_range in self._bit_ranges:
                self._mask_shift.append(utils.bits_to_mask_and_shift(bit_range))

    def __str__(self) -> str:
        if self.bits:
            bit_ranges = []
            for a, b in utils.bit_list_to_ranges(self.bits):
                if a == b:
                    bit_ranges.append(str(a))
                else:
                    bit_ranges.append(f"{a}-{b}")
            s = f"""{self.word}:{",".join(bit_ranges)}"""
        else:
            s = f"{self.word}"

        s = ("~" if self.complement else "") + s
        s = s + ("R" if self.reverse else "")

        return s

    def __eq__(self, other) -> bool:
        if isinstance(other, FragmentWord):
            bits_a = self.bits if self.bits is None else sorted(self.bits)
            bits_b = other.bits if other.bits is None else sorted(other.bits)
            return all(
                [
                    self.word - int(self.one_based) == other.word - int(self.one_based),
                    bits_a == bits_b,
                    self.complement == other.complement,
                    self.reverse == other.reverse,
                ]
            )
        return NotImplemented

    @override
    def build(self, data: VarUIntArray, /, offset: int = 0) -> VarUIntArray:
        result = data[:, self.word - int(self.one_based) + offset].flatten()

        if self.word_size is None:
            self.word_size = data.word_size

        if self.bits is not None:
            if self.word_size != data.word_size:
                msg = f"data.word_size={data.word_size} does not match fragment.word_size={self.word_size}"
                raise ValueError(msg)

            for mask, shift in self._mask_shift:
                result = np.bitwise_and(result, mask)
                result = np.bitwise_right_shift(result, shift)

            frag_size = len(self.bits)
        else:
            frag_size = data.word_size

        if self.complement:
            # TODO: Should this really come after the fragment assemby, or should it be before???
            result = np.bitwise_and(np.invert(result), 2**frag_size - 1)

        if self.reverse:
            result = utils.reverse_bits(result, frag_size)

        return VarUIntArray(result, word_size=frag_size)


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

    @override
    def build(self, data: VarUIntArray) -> VarUIntArray:
        return VarUIntArray(self.value, word_size=self.size)


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
        """Determine the size of the parameter by adding the fragment sizes."""
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
        """Generate a list of all the words in each Fragment"""
        return [f.word for f in self.fragments if isinstance(f, FragmentWord)]

    def max_word(self) -> int:
        """Find the maximum word in all fragments"""
        return max(self._all_words())

    def min_word(self) -> int:
        """Find the minimum word in all fragments"""
        return min(self._all_words())

    def build(self, data: VarUIntArray, /, offset: int = 0) -> VarUIntArray:
        """Construct the Parameter from the input data array.

        Args:
            data (VarUIntArray): The input data array.

            offset (int): An offset applied to the fragment words. This is useful
            for Parameters defined relative to another Parameter, e.g. for Supercom or Generator Parameters.

        Returns;
            VarUIntArray: The assembled Parameter vector.
        """
        # Determine the total number of bits in the complete Parameter
        # Set the uint dtype to the minimum sized container for the Parameter size
        size = self._calculate_parameter_size(data.word_size)
        dtype = utils.word_size_to_uint(size)

        # Initialize the result vector with the necessary dtype
        result = np.zeros(data.shape[0], dtype=dtype)

        for frag_idx, frag in enumerate(self.fragments):
            # Build the fragment
            tmp = frag.build(data, offset=offset)

            # Shift the previous result left by the fragment size
            if frag_idx != 0:
                result = np.left_shift(result, tmp.word_size)

            # Add the fragment value
            result += tmp

        if self.bit_op:
            result = self.bit_op._func(result, self.bit_op.value)

        return VarUIntArray(result, word_size=size)


@dataclass
class GeneratorParameter(Parameter):
    parameter: BasicParameter
    iterator: Iterator
    word_size: Optional[int] = None

    def __post_init__(self) -> None:
        # For decrementing generators, the "stop before" must be 0
        if self.iterator.stop is None and self.iterator.step < 0:
            self.iterator.stop = 0

    def build(self, data: VarUIntArray) -> list[VarUIntArray]:
        if self.word_size is None:
            self.word_size = data.word_size
        elif self.word_size != data.word_size:
            raise ValueError

        results = []

        # If the iterator is positive, compare the largest word against the "stop before" limit
        # If the iterator is negative, compare the smallest
        if self.iterator.step > 0:
            start = self.parameter.max_word()
        else:
            start = self.parameter.min_word()

        # Use the "stop before" limit if it is defined
        # If it is not defined, set the "stop before" limit based on the end of the row of data
        if self.iterator.stop is not None:
            stop = self.iterator.stop
        else:
            # If step is negative, the stop was implicitly 0 and set in __post_init__
            stop = data.shape[1]

        # Iterate through the generated parameters by using the offset
        for target in range(start, stop, self.iterator.step):
            offset = target - start
            result = self.parameter.build(data, offset=offset)
            results.append(result)

        return VarUIntArray(results, word_size=results[0].word_size).T


@dataclass
class SupercomParameter(GeneratorParameter):
    parameter: BasicParameter
    iterator: Iterator
    word_size: Optional[int] = None

    def build(self, data: VarUIntArray) -> VarUIntArray:
        results = super().build(data)
        return results


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
