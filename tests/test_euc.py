import numpy as np
import pytest

from decom.measurand import BaseEUC, StaticEUC


@pytest.mark.parametrize(
    "euc, pv, expected",
    [
        (StaticEUC(scale_factor=0), 100, 0),
        (StaticEUC(scale_factor=1), 100, 100),
        (StaticEUC(data_bias=1, scale_factor=2), 5, (5 + 1) * 2),
        (StaticEUC(scale_factor=2, scaled_bias=3), 5, (5) * 2 + 3),
        (StaticEUC(data_bias=1, scale_factor=2, scaled_bias=3), 5, (5 + 1) * 2 + 3),
    ],
)
def test_euc(euc: BaseEUC, pv: float, expected: float):
    num_rows = 10
    a = np.array([pv] * num_rows, dtype="uint8")
    out = euc.apply(a)
    assert len(out) == num_rows
    assert out.tolist() == pytest.approx([expected] * num_rows)
