import math

import numpy as np
import pytest

from decom.measurand import EUC


@pytest.mark.parametrize(
    "euc, pv, expected",
    [
        (EUC(scale_factor=0), 100, 0),
        (EUC(scale_factor=1), 100, 100),
        (EUC(data_bias=1, scale_factor=2), 5, (5 - 1) * 2),
        (EUC(scale_factor=2, scaled_bias=3), 5, (5) * 2 + 3),
        (EUC(data_bias=1, scale_factor=2, scaled_bias=3), 5, (5 - 1) * 2 + 3),
    ],
)
def test_euc_static(euc: EUC, pv: float, expected: float):
    num_rows = 10
    a = np.array([pv] * num_rows, dtype="float32")
    out = euc.apply(a)
    assert len(out) == num_rows
    assert out.tolist() == pytest.approx([expected] * num_rows)


@pytest.mark.parametrize(
    "euc, pv, expected",
    [
        (EUC(scale_factor=lambda pv: math.sin(pv)), math.pi / 2, 1),
        (EUC(scale_factor=lambda pv: math.cos(pv)), 0, 1),
        (EUC(scale_factor=lambda pv: math.cos(pv), scaled_bias=1), 0, 1 + 1),
    ],
)
def test_euc_callable(euc: EUC, pv: float, expected: float):
    num_rows = 10
    a = np.array([pv] * num_rows, dtype="float32")
    out = euc.apply(a)
    assert len(out) == num_rows
    assert out.tolist() == pytest.approx([expected] * num_rows)
