import abc
from dataclasses import dataclass
from typing import Any, Callable, Optional, Union

import numpy as np
from lark import Token, Transformer
from numpy.typing import NDArray

from decom.calculator import Number
from decom.parameter import BaseParameter


class Interp:
    pass


class BaseEUC(abc.ABC):
    @abc.abstractmethod
    def apply(self, data: NDArray) -> NDArray:
        pass


@dataclass
class StaticEUC(BaseEUC):
    scale_factor: Number
    data_bias: Optional[Number] = None
    scaled_bias: Optional[Number] = None

    def apply(self, data: NDArray) -> NDArray:
        value = data.copy()
        if self.data_bias is not None:
            value = value + self.data_bias

        value = self.scale_factor * value

        if self.scaled_bias is not None:
            value = value + self.scaled_bias

        return value


@dataclass
class CallableEUC(BaseEUC):
    scale_factor: Union[Callable, Number]
    data_bias: Union[Callable, Number] = None
    scaled_bias: Union[Callable, Number] = None

    def __post_init__(self) -> None:
        self._ufunc = np.vectorize(self.func)

    def apply(self, data: NDArray) -> NDArray:
        value = data.copy()

        if self.data_bias is not None:
            value = value + self.data_bias(data)

        value = value * self.scale_factor(data)

        if self.scaled_bias is not None:
            value = value + self.scaled_bias(data)

        return value


class SamplingStrategy:
    pass


@dataclass
class Measurand:
    parameter: BaseParameter
    interp: Interp
    euc: BaseEUC
    ss: SamplingStrategy


class MeasurandTransformer(Transformer):
    def measurand(
        self,
        parameter: BaseParameter,
        interp: Optional[Any] = None,
        euc: Optional[Any] = None,
        ss: Optional[Any] = None,
    ) -> Measurand:
        return Measurand(parameter=parameter, interp=interp, euc=euc, ss=ss)

    def interp(self, token: Token) -> str:
        return str(token)

    def euc(self, *args: list[Union[Callable, Number]]) -> str:
        kwargs = {}
        if len(args) == 1:
            kwargs = {
                "scale_factor": args[0],
            }
        elif len(args) == 2:
            kwargs = {
                "scale_factor": args[0],
                "scaled_bias": args[1],
            }
        elif len(args) == 3:
            kwargs = {
                "data_bias": args[0],
                "scale_factor": args[1],
                "scaled_bias": args[2],
            }
        else:
            raise ValueError

        if any(isinstance(x, Callable) for x in args):
            return CallableEUC(**kwargs)
        return StaticEUC(**kwargs)
