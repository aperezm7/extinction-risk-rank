"""Hidden solutions match the functions the services run, and starters do not."""

from __future__ import annotations

import importlib

import pandas as pd
import pytest

from src import cover, features, labels, metrics, split


def test_starters_are_what_they_say():
    assert importlib.import_module("challenges.01_iucn_label.starter").map_iucn_label.__code__.co_code
    for call in (
        lambda: importlib.import_module("challenges.01_iucn_label.starter").map_iucn_label("CR"),
        lambda: importlib.import_module("challenges.02_log_body_mass.starter").log_body_mass([1.0]),
        lambda: importlib.import_module("challenges.03_family_split.starter").family_grouped_split(
            pd.DataFrame({"family": ["A", "B"]})
        ),
        lambda: importlib.import_module("challenges.04_top_decile_precision.starter").precision_at_top_fraction(
            [0, 1], [0.1, 0.2]
        ),
        lambda: importlib.import_module("challenges.05_greedy_family_cover.starter").greedy_family_cover([], 0),
    ):
        with pytest.raises(NotImplementedError):
            call()


def test_hidden_matches_src():
    hidden_labels = importlib.import_module("challenges.hidden.01_iucn_label")
    hidden_features = importlib.import_module("challenges.hidden.02_log_body_mass")
    hidden_split = importlib.import_module("challenges.hidden.03_family_split")
    hidden_metrics = importlib.import_module("challenges.hidden.04_top_decile_precision")
    hidden_cover = importlib.import_module("challenges.hidden.05_greedy_family_cover")

    for category in ["CR", "NT", "DD", "EX", "Least Concern", None]:
        assert hidden_labels.map_iucn_label(category) == labels.map_iucn_label(category)

    masses = pd.Series([10.0, None, 0.0], index=["a", "b", "c"])
    pd.testing.assert_series_equal(hidden_features.log_body_mass(masses), features.log_body_mass(masses))

    frame = pd.DataFrame(
        {"family": ["A", "A", "B", "C", "C", "D"], "scientific_name": list("abcdef")}
    )
    for side in (0, 1):
        left = hidden_split.family_grouped_split(frame, test_size=0.4, random_state=1)[side]
        right = split.family_grouped_split(frame, test_size=0.4, random_state=1)[side]
        assert left["scientific_name"].tolist() == right["scientific_name"].tolist()

    y_true = [0, 1, 0, 1, 0]
    y_score = [0.2, 0.9, 0.4, 0.8, 0.1]
    assert hidden_metrics.precision_at_top_fraction(y_true, y_score) == metrics.precision_at_top_fraction(
        y_true, y_score
    )

    records = [
        {"scientific_name": "a", "family": "A", "score": 0.4},
        {"scientific_name": "b", "family": "B", "score": 0.9},
    ]
    assert hidden_cover.greedy_family_cover(records, 1) == cover.greedy_family_cover(records, 1)


def test_reveal_prints_the_family_split(capsys):
    from challenges.__main__ import main

    main(["reveal", "03"])
    printed = capsys.readouterr().out
    assert "GroupShuffleSplit" in printed
    assert "family" in printed.lower()
