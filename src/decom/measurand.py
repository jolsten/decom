from dataclasses import dataclass
from typing import Optional


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
class Parameter:
    fragments: list[Fragment]


class SupercomParameter:
    fragments: list[Fragment]
    iterator: Iterator


class GeneratorParameter:
    fragments: list[Fragment]
    iterator: Iterator


@dataclass
class BitwiseOperator:
    operation: str
    operand: int
