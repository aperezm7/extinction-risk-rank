"""Public contract for the family split."""

from __future__ import annotations

import pandas as pd
import pytest

from challenges.loader import load


def _frame() -> pd.DataFrame:
    return pd.DataFrame(
        {
            "family": ["MURIDAE", "MURIDAE", "FELIDAE", "FELIDAE", "BOVIDAE", "BOVIDAE"],
            "scientific_name": ["m1", "m2", "f1", "f2", "b1", "b2"],
        }
    )


def test_families_do_not_cross_the_split():
    split = load("03")
    frame = _frame()
    train, test = split.family_grouped_split(frame, test_size=0.34, random_state=0)
    assert not train.empty and not test.empty
    assert set(train["family"]).isdisjoint(set(test["family"]))
    together = pd.concat([train, test], ignore_index=True)
    assert sorted(together["scientific_name"]) == sorted(frame["scientific_name"])
    for family in frame["family"].unique():
        in_train = family in set(train["family"])
        in_test = family in set(test["family"])
        assert in_train ^ in_test


def test_split_is_reproducible():
    split = load("03")
    frame = _frame()
    first = split.family_grouped_split(frame, random_state=0)
    second = split.family_grouped_split(frame, random_state=0)
    assert first[0]["scientific_name"].tolist() == second[0]["scientific_name"].tolist()


def test_one_family_is_rejected():
    split = load("03")
    frame = pd.DataFrame({"family": ["MURIDAE", "MURIDAE"], "scientific_name": ["a", "b"]})
    with pytest.raises(ValueError):
        split.family_grouped_split(frame)
