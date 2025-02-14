from dataclasses import dataclass
from typing import Literal, Optional


@dataclass
class Fragment:
    word: int
    bits: Optional[int] = None
    complement: bool = False
    reverse: bool = False

    def __eq__(self, other: "Fragment") -> bool:
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


@dataclass
class FragmentConstant:
    value: int
    size: int


@dataclass
class Iterator:
    step: int
    stop: Optional[int] = None


@dataclass
class BitOperator:
    mode: Literal["AND", "OR", "XOR"]
    value: int


@dataclass
class Parameter:
    fragments: list[Fragment]
    bit_op: Optional[BitOperator] = None


@dataclass
class SupercomParameter:
    parameter: Parameter
    iterator: Iterator
    bit_op: Optional[BitOperator] = None


@dataclass
class GeneratorParameter:
    parameter: Parameter
    iterator: Iterator
    bit_op: Optional[BitOperator] = None


class Interp:
    pass


class EUC:
    pass


class SamplingStrategy:
    pass


@dataclass
class Measurand:
    parameter: Parameter
    interp: Interp
    euc: EUC
    ss: SamplingStrategy
