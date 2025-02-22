import abc
from dataclasses import dataclass, field
from typing import Callable, Optional, Union

import numpy as np
from numpy.typing import NDArray
from typeconvert import ufunc

from decom.array import UintXArray
from decom.measurand.parameter import Parameter

Number = Union[int, float]


class InterpFactory:
    _registry: dict[str, Callable] = {}

    @classmethod
    def register(cls, name: str) -> Callable:
        def inner_wrapper(wrapped_class) -> Callable:
            cls._registry[name] = wrapped_class
            return wrapped_class

        return inner_wrapper

    @classmethod
    def create(self, name: str) -> None:
        object_class = self._registry.get(name)
        if not object_class:
            raise ValueError(f"Invalid object key: {name}")
        return object_class()

    def __contains__(self, a: str) -> bool:
        if not isinstance(a, str):
            raise TypeError
        return a in self._registry


class InterpImplementation(abc.ABC):
    @abc.abstractmethod
    def apply(self, data: UintXArray) -> NDArray: ...


class Interp:
    mode: str
    _func: InterpImplementation = field(init=False, repr=False)

    def __init__(self, mode: str) -> None:
        if mode not in InterpFactory._registry:
            msg = f"{self.mode!r} is not a valid interpretation type"
            raise ValueError(msg)
        self.mode = mode
        self._func = InterpFactory.create(self.mode)

    def apply(self, data: UintXArray) -> NDArray:
        return self._func.apply(data)


@InterpFactory.register("u")
class UnsignedInt(InterpImplementation):
    def apply(self, data: UintXArray) -> UintXArray:
        return data


@InterpFactory.register("1c")
class OnesComplement(InterpImplementation):
    def apply(self, data: UintXArray) -> NDArray:
        return ufunc.onescomp(data, data.word_size)


@InterpFactory.register("2c")
class TwosComplement(InterpImplementation):
    def apply(self, data: UintXArray) -> NDArray:
        return ufunc.twoscomp(data, data.word_size)


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

        if self.data_bias is not None:
            result = result - self.data_bias

        if isinstance(self.scale_factor, Callable):
            result = self.scale_factor(result)
        else:
            result = result * self.scale_factor

        if self.scaled_bias is not None:
            result = result + self.scaled_bias

        return result


class SamplingStrategy:
    pass


@dataclass
class Measurand:
    parameter: Parameter
    interp: Interp
    euc: EUC
    ss: SamplingStrategy
