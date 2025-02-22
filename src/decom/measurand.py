from dataclasses import dataclass
from typing import Any, Callable, Optional, Union

import numpy as np
from lark import Token, Transformer, v_args
from numpy.typing import NDArray

from decom.calculator import Number
from decom.parameter import Parameter


class Interp:
    pass


NumberOrCallable = Union[Number, Callable]


@dataclass
class EUC:
    scale_factor: Union[Number, Callable]
    data_bias: Optional[Number] = None
    scaled_bias: Optional[Number] = None

    def __post_init__(self) -> None:
        if isinstance(self.scale_factor, Callable):
            self.scale_factor = np.vectorize(self.scale_factor)

    def apply(self, data: NDArray) -> NDArray:
        result = data
        print("a", result)
        if self.data_bias is not None:
            result = result - self.data_bias

        print("b", result)
        if isinstance(self.scale_factor, Callable):
            result = self.scale_factor(result)
        else:
            result = result * self.scale_factor

        print("c", result)
        if self.scaled_bias is not None:
            result = result + self.scaled_bias

        print("d", result)
        return result


# @dataclass
# class StaticEUC(BaseEUC):
#     scale_factor: Number
#     data_bias: Optional[Number] = None
#     scaled_bias: Optional[Number] = None

#     def apply(self, data: NDArray) -> NDArray:
#         value = data.copy()
#         if self.data_bias is not None:
#             value = value + self.data_bias

#         value = self.scale_factor * value

#         if self.scaled_bias is not None:
#             value = value + self.scaled_bias

#         return value


# @dataclass
# class CallableEUC(BaseEUC):
#     scale_factor: Union[Callable, Number]
#     data_bias: Union[Callable, Number] = None
#     scaled_bias: Union[Callable, Number] = None

#     def __post_init__(self) -> None:
#         self._ufunc = np.vectorize(self.func)

#     def apply(self, data: NDArray) -> NDArray:
#         value = data.copy()

#         if self.data_bias is not None:
#             value = value + self.data_bias(data)

#         value = value * self.scale_factor(data)

#         if self.scaled_bias is not None:
#             value = value + self.scaled_bias(data)

#         return value


class SamplingStrategy:
    pass


@dataclass
class Measurand:
    parameter: Parameter
    interp: Interp
    euc: EUC
    ss: SamplingStrategy


@v_args(inline=True)
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

    def euc(self, *args: list[Union[Callable, Number]]) -> str:
        if len(args) == 1:
            return EUC(scale_factor=args[0])
        elif len(args) == 2:
            return EUC(scale_factor=args[0], scaled_bias=args[1])
        elif len(args) == 3:
            return EUC(data_bias=args[0], scale_factor=args[1], scaled_bias=args[2])
        raise ValueError
