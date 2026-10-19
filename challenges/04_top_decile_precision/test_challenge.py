"""Public contract for top-decile precision."""

from __future__ import annotations

import math

import numpy as np
import pytest

from challenges.loader import load


def test_top_decile_of_ten_is_one_row():
    metrics = load("04")
    labels = np.array([0, 1, 0, 0, 1, 0, 0, 0, 0, 0])
    scores = np.array([0.1, 0.9, 0.2, 0.05, 0.8, 0.3, 0.0, 0.4, 0.15, 0.12])
    assert metrics.precision_at_top_fraction(labels, scores, 0.1) == 1.0


def test_tie_keeps_the_earlier_row():
    metrics = load("04")
    # k = ceil(2 * 0.1) = 1. Equal scores: the earlier positive is selected.
    assert metrics.precision_at_top_fraction([1, 0], [0.5, 0.5], 0.1) == 1.0
    assert metrics.precision_at_top_fraction([0, 1], [0.5, 0.5], 0.1) == 0.0


def test_half_of_five_uses_ceil():
    metrics = load("04")
    labels = [1, 1, 0, 0, 0]
    scores = [0.9, 0.8, 0.7, 0.2, 0.1]
    # n * 0.5 = 2.5, k = 3, precision = 2/3.
    assert metrics.precision_at_top_fraction(labels, scores, 0.5) == pytest.approx(2 / 3)


def test_rejects_empty_and_nan():
    metrics = load("04")
    with pytest.raises(ValueError):
        metrics.precision_at_top_fraction([], [], 0.1)
    with pytest.raises(ValueError):
        metrics.precision_at_top_fraction([1], [math.nan], 0.1)
