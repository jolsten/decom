from dataclasses import dataclass
from typing import Union

from .euc import EUC
from .interp import Interp
from .parameter import Parameter

Number = Union[int, float]


class SamplingStrategy:
    pass


@dataclass
class Measurand:
    parameter: Parameter
    interp: Interp
    euc: EUC
    ss: SamplingStrategy
