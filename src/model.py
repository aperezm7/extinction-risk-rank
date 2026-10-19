"""Gradient boosting that leaves missing traits missing."""

from __future__ import annotations

import numpy as np
import pandas as pd
from sklearn.ensemble import HistGradientBoostingClassifier


def train_gradient_booster(
    features: pd.DataFrame,
    labels,
    random_state: int = 0,
) -> HistGradientBoostingClassifier:
    """Fit a histogram gradient booster.

    HistGradientBoostingClassifier is the scikit-learn booster that accepts
    NaN. GradientBoostingClassifier would require an imputation step, which
    would invent body masses the table does not have.
    """
    model = HistGradientBoostingClassifier(
        learning_rate=0.08,
        max_iter=200,
        max_depth=3,
        min_samples_leaf=5,
        early_stopping=False,
        random_state=random_state,
    )
    model.fit(features, np.asarray(labels, dtype=int))
    return model


def threat_scores(model, features: pd.DataFrame) -> np.ndarray:
    """Probability of the threatened class. Does not refit the model."""
    probabilities = model.predict_proba(features)
    classes = [int(value) for value in model.classes_]
    if 1 not in classes:
        raise RuntimeError("booster has no threatened class")
    return np.asarray(probabilities[:, classes.index(1)], dtype=float)
