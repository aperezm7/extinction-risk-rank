"""Public contract for the greedy family pick."""

from __future__ import annotations

import pytest

from challenges.loader import load

RECORDS = [
    {"scientific_name": "a1", "family": "A", "score": 0.95},
    {"scientific_name": "a2", "family": "A", "score": 0.90},
    {"scientific_name": "b1", "family": "B", "score": 0.80},
    {"scientific_name": "c1", "family": "C", "score": 0.70},
    {"scientific_name": "b2", "family": "B", "score": 0.60},
]


def _names(records) -> list[str]:
    return [row["scientific_name"] for row in records]


def test_prefers_a_new_family():
    cover = load("05")
    assert _names(cover.greedy_family_cover(RECORDS, 3)) == ["a1", "b1", "c1"]


def test_fills_after_every_family_is_represented():
    cover = load("05")
    assert _names(cover.greedy_family_cover(RECORDS, 4)) == ["a1", "b1", "c1", "a2"]


def test_edges():
    cover = load("05")
    assert cover.greedy_family_cover(RECORDS, 0) == []
    assert _names(cover.greedy_family_cover(RECORDS, 1)) == ["a1"]
    assert len(cover.greedy_family_cover(RECORDS, 20)) == len(RECORDS)
    with pytest.raises(ValueError):
        cover.greedy_family_cover(RECORDS, -1)
