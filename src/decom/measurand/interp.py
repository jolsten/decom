import abc
from typing import Callable

from numpy.typing import NDArray
from typeconvert import ufunc

from decom.array import UintXArray


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
    _func: InterpImplementation

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
