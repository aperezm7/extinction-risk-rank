"""Domain transforms the model service calls. The math lives in src.features."""

from __future__ import annotations

import pandas as pd

from src.features import FEATURE_COLUMNS, build_features, log_body_mass

__all__ = ["FEATURE_COLUMNS", "build_features", "log_body_mass", "species_feature_matrix"]


def species_feature_matrix(frame: pd.DataFrame) -> pd.DataFrame:
    return build_features(frame)
