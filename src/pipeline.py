"""Family holdout, then a refit used only to score species."""

from __future__ import annotations

import pandas as pd
from sklearn.metrics import roc_auc_score

from src.features import build_features
from src.metrics import precision_at_top_fraction
from src.model import threat_scores, train_gradient_booster
from src.split import family_grouped_split


class HoldoutError(RuntimeError):
    """The family split cannot estimate both metrics."""


def evaluate_holdout(
    frame: pd.DataFrame,
    random_state: int = 0,
    test_size: float = 0.25,
) -> dict:
    """ROC AUC and top-decile precision on one predeclared family split.

    `frame` must already carry `threatened_label` and `family`. Rows with a
    null label are ignored. The seed is an argument so the reported split is
    not chosen after looking at the score.
    """
    labeled = frame.loc[frame["threatened_label"].notna()].copy()
    if labeled.empty or labeled["threatened_label"].nunique() < 2:
        raise HoldoutError("need both threatened and not-threatened species")
    train, test = family_grouped_split(
        labeled,
        group_col="family",
        test_size=test_size,
        random_state=random_state,
    )
    if train["threatened_label"].nunique() < 2 or test["threatened_label"].nunique() < 2:
        raise HoldoutError(
            f"random_state={random_state} put only one class on a side of the family split"
        )
    model = train_gradient_booster(
        build_features(train),
        train["threatened_label"].astype(int),
        random_state=random_state,
    )
    scores = threat_scores(model, build_features(test))
    y_true = test["threatened_label"].astype(int).to_numpy()
    return {
        "roc_auc": float(roc_auc_score(y_true, scores)),
        "precision_top_10": precision_at_top_fraction(y_true, scores, fraction=0.1),
        "n_labeled": int(len(labeled)),
        "n_train": int(len(train)),
        "n_test": int(len(test)),
        "random_state": int(random_state),
        "test_size": float(test_size),
        "positive_rate": float(labeled["threatened_label"].astype(int).mean()),
        "model": "HistGradientBoostingClassifier",
        "split": "family",
    }


def fit_and_score(
    frame: pd.DataFrame,
    random_state: int = 0,
    test_size: float = 0.25,
) -> tuple[pd.DataFrame, dict, object]:
    """Holdout metrics, then refit on every labeled row and score the whole frame.

    The second fit is the serving model. It is not a different algorithm.
    """
    report = evaluate_holdout(frame, random_state=random_state, test_size=test_size)
    labeled = frame.loc[frame["threatened_label"].notna()]
    model = train_gradient_booster(
        build_features(labeled),
        labeled["threatened_label"].astype(int),
        random_state=random_state,
    )
    scored = frame.copy()
    scored["threat_score"] = threat_scores(model, build_features(scored))
    report["n_scored"] = int(len(scored))
    return scored, report, model
