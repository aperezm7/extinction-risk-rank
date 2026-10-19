"""Public contract for the body-mass log."""

from __future__ import annotations

import math

import numpy as np
import pandas as pd

from challenges.loader import load


def test_log_and_missing():
    features = load("02")
    masses = pd.Series([math.e, np.nan, None, 1.0], index=["a", "b", "c", "d"])
    logged = features.log_body_mass(masses)
    assert logged.name == "log_body_mass"
    assert list(logged.index) == ["a", "b", "c", "d"]
    assert logged.loc["a"] == pytest_approx(1.0)
    assert logged.loc["d"] == pytest_approx(0.0)
    assert pd.isna(logged.loc["b"])
    assert pd.isna(logged.loc["c"])


def test_non_positive_stays_missing():
    features = load("02")
    logged = features.log_body_mass(pd.Series([0.0, -5.0, 10.0]))
    assert pd.isna(logged.iloc[0])
    assert pd.isna(logged.iloc[1])
    assert logged.iloc[2] == pytest_approx(math.log(10.0))


def pytest_approx(value: float):
    import pytest

    return pytest.approx(value)
