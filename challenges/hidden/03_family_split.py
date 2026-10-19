"""Hidden solution for challenge 03. Mirrors src.split."""

from __future__ import annotations

import pandas as pd
from sklearn.model_selection import GroupShuffleSplit


def family_grouped_split(
    frame: pd.DataFrame,
    group_col: str = "family",
    test_size: float = 0.2,
    random_state: int = 0,
) -> tuple[pd.DataFrame, pd.DataFrame]:
    if group_col not in frame.columns:
        raise KeyError(group_col)
    if not 0 < test_size < 1:
        raise ValueError("test_size must be between 0 and 1")
    if frame[group_col].nunique(dropna=True) < 2:
        raise ValueError("family split needs at least two families")
    splitter = GroupShuffleSplit(n_splits=1, test_size=test_size, random_state=random_state)
    train_pos, test_pos = next(splitter.split(frame, groups=frame[group_col]))
    train = frame.iloc[train_pos].copy()
    test = frame.iloc[test_pos].copy()
    if train.empty or test.empty:
        raise RuntimeError("family split produced an empty side")
    overlap = set(train[group_col]) & set(test[group_col])
    if overlap:
        raise RuntimeError(f"family leaked across the split: {sorted(overlap)[:5]}")
    return train, test
