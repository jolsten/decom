from dataclasses import dataclass
from typing import Any, Iterable, Union

import numpy as np
from numpy.typing import NDArray

from decom import utils


class VarUIntArray(np.ndarray):
    def __new__(cls, input_array, word_size: int):
        # Input array is an already formed ndarray instance
        # We first cast to be our class type
        dtype = utils.word_size_to_uint(word_size)
        obj = np.asarray(input_array, dtype=dtype).view(cls)

        # add the new attribute to the created instance
        obj.word_size = word_size

        # Finally, we must return the newly created object:
        return obj

    def __array_finalize__(self, obj):
        # see InfoArray.__array_finalize__ for comments
        if obj is None:
            return
        self.word_size = getattr(obj, "word_size", None)

    def __array_wrap__(self, obj, context=None, return_scalar=False):
        if obj is self:  # for in-place operations
            result = obj
        else:
            result = obj.view(type(self))

        result = super().__array_wrap__(obj, context, return_scalar)

        if context is not None:
            func, args, out_i = context
            # input_args = args[: func.nin]

            if func is np.invert:
                # Ensure the inverted result doesn't contain bits which should be unused
                result = np.bitwise_and(result.view(np.ndarray), 2**self.word_size - 1)
                result = self.__class__(result, word_size=self.word_size)

        return result


@dataclass
class FrameBatch:
    ctime: NDArray[np.datetime64]
    time: NDArray[np.datetime64]
    data: VarUIntArray

    def __post_init__(self):
        if self.ctime.ndim != 1:
            raise ValueError
        if self.time.ndim != 1:
            raise ValueError
        if self.data.ndim != 2:
            raise ValueError

        if not all(
            [len(self.ctime) == len(self.time), len(self.time) == len(self.data)]
        ):
            raise ValueError

    def __eq__(self, other) -> bool:
        if isinstance(other, FrameBatch):
            return all(
                [
                    self.time.tolist() == other.time.tolist(),
                    self.ctime.tolist() == other.ctime.tolist(),
                    self.data.tolist() == other.data.tolist(),
                ]
            )
        raise TypeError

    def __getitem__(self, key) -> "FrameBatch":
        ctime = np.atleast_1d(self.ctime[key])
        time = np.atleast_1d(self.time[key])
        data = np.atleast_2d(self.data[key])
        return FrameBatch(ctime=ctime, time=time, data=data)


def ensure_n_by_2(
    values: list[Union[int, tuple[int, int]]], fill: int = 0
) -> list[tuple[int, int]]:
    result = []
    for row in values:
        if isinstance(row, int):
            result.append((row, fill))
        elif isinstance(row, (tuple, list)):
            if len(row) == 1:
                result.append((row[0], fill))
            elif len(row) == 2:
                result.append((row[0], row[2]))
            else:
                raise ValueError
        else:
            raise ValueError
    return result


@dataclass
class IndexedFrameBatch:
    index: VarUIntArray
    frames: FrameBatch

    def __getitem__(self, idx) -> "IndexedFrameBatch":
        index = self.index[idx]
        frames = self.frames[idx]
        return IndexedFrameBatch(index=index, frames=frames)

    def _select_one(self, value: int, mod: int = 0) -> FrameBatch:
        if not isinstance(value, int):
            raise ValueError

        if not isinstance(mod, int):
            raise ValueError

        if mod:
            return self.frames[self.index % mod == value]
        return self.frames[self.index == value]

    def _select_many(self, values: list[tuple[int, int]]) -> FrameBatch:
        idx = np.zeros(self.index.shape, dtype=np.bool)
        for value, mod in values:
            if mod:
                tmp = self.index % mod == value
            else:
                tmp = self.index == value
            idx = np.logical_or(idx, tmp)
        return self.frames[idx]

    def select(
        self, values: Union[int, tuple[int, int], Iterable[tuple[int, int]]]
    ) -> FrameBatch:
        values = np.asarray(values)

        if values.ndim == 0:
            return self._select_one(values)
        elif values.ndim == 1:
            return self._select_one(value=values[0], mod=values[1])
        elif values.ndim == 2:
            return self._select_many(ensure_n_by_2(values))

        raise ValueError


@dataclass
class PacketBatch:
    packets: dict[Any, FrameBatch]

    def select(self, pid: Any) -> FrameBatch:
        if pid in self.packets:
            return self.packets[pid]
        return None

    def __getitem__(self, idx) -> "PacketBatch":
        return self.select(idx)
