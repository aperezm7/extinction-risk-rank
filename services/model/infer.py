"""Score a frame with a booster that was already fit."""

from __future__ import annotations

import pandas as pd

from services.features.transform import species_feature_matrix
from src.model import threat_scores


def score_frame(model, frame: pd.DataFrame) -> pd.Series:
    features = species_feature_matrix(frame)
    return pd.Series(threat_scores(model, features), index=frame.index, name="threat_score")
