"""Public contract for the IUCN label."""

from __future__ import annotations

import pandas as pd

from challenges.loader import load


def test_threatened_and_not():
    labels = load("01")
    for category in ("CR", "EN", "VU", "cr", "Critically Endangered", "CR(PE)", "CR (PEW)"):
        assert labels.map_iucn_label(category) == 1
    for category in ("NT", "LC", "near threatened", "Least Concern"):
        assert labels.map_iucn_label(category) == 0


def test_data_deficient_and_extinct_have_no_binary_label():
    labels = load("01")
    for category in ("DD", "Data Deficient", "EX", "EW", "NE", None, ""):
        assert labels.map_iucn_label(category) is None


def test_drop_data_deficient_keeps_other_categories():
    labels = load("01")
    frame = pd.DataFrame(
        {
            "scientific_name": ["a", "b", "c", "d"],
            "iucn_category": ["DD", "LC", "EX", "Data Deficient"],
        }
    )
    kept = labels.drop_data_deficient(frame)
    assert kept["scientific_name"].tolist() == ["b", "c"]
