from dataclasses import dataclass
from typing import Callable, Optional, Union

import numpy as np
from numpy.typing import NDArray

Number = Union[int, float]


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
