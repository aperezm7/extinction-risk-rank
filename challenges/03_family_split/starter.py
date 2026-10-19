# Complete the functions below. Do not change the signatures.
"""Starter for challenge 03. Replace the body; do not import the hidden solution."""

from __future__ import annotations

import pandas as pd


def family_grouped_split(
    frame: pd.DataFrame,
    group_col: str = "family",
    test_size: float = 0.2,
    random_state: int = 0,
) -> tuple[pd.DataFrame, pd.DataFrame]:
    # Related species share a family, and the paper's models gave each family
    # its own intercept. A row-wise split leaks that dependence into the test score.
    #
    # Steps:
    # - Use sklearn.model_selection.GroupShuffleSplit so the seed is reproducible.
    # - Hold out whole families. No family appears on both sides.
    # - Every input row appears on exactly one side.
    # - Both sides are non-empty.
    #
    # Edge cases:
    # - Raise ValueError if the frame has fewer than two families.
    #
    # Return (train, test) as copies.
    raise NotImplementedError("Split by family so no family is in both train and test.")
