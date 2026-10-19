# Complete the functions below. Do not change the signatures.
"""Starter for challenge 04. Replace the body; do not import the hidden solution."""

from __future__ import annotations


def precision_at_top_fraction(y_true, y_score, fraction: float = 0.1) -> float:
    # The watchlist is the top of the score list, not a threshold of 0.5.
    # Precision there is the fraction of those species whose published label
    # is threatened.
    #
    # Steps:
    # - Let n be the number of rows and k = max(1, ceil(n * fraction)).
    # - Take the k highest scores. Ties keep the earlier row (stable sort).
    # - Return the mean of y_true on those rows.
    #
    # Edge cases:
    # - Raise ValueError on an empty input, a bad fraction, unequal lengths,
    #   or a NaN score.
    #
    # Return that precision as a float.
    raise NotImplementedError("Compute precision in the top fraction of scores.")
