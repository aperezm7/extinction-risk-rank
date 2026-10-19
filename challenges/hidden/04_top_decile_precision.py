"""Hidden solution for challenge 04. Mirrors src.metrics."""

from __future__ import annotations

import math

import numpy as np


def precision_at_top_fraction(y_true, y_score, fraction: float = 0.1) -> float:
    labels = np.asarray(y_true)
    scores = np.asarray(y_score, dtype=float)
    if labels.shape[0] != scores.shape[0]:
        raise ValueError("y_true and y_score must have the same length")
    if labels.shape[0] == 0:
        raise ValueError("need at least one row")
    if not 0 < fraction <= 1:
        raise ValueError("fraction must be in (0, 1]")
    if np.isnan(scores).any():
        raise ValueError("scores contain NaN")
    k = max(1, math.ceil(labels.shape[0] * fraction))
    order = np.argsort(-scores, kind="mergesort")
    top = labels[order[:k]].astype(float)
    return float(np.mean(top))
