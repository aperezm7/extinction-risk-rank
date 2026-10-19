"""Checks that fail loud before a model sees the table."""

from __future__ import annotations

import pandas as pd

from services.data.columns import SPECIES_COLUMNS
from src.labels import normalize_iucn_category

KNOWN_CATEGORIES = frozenset(
    {"CR", "EN", "VU", "NT", "LC", "DD", "EX", "EW", "EP", "NE", "CR(PE)", "CR(PEW)"}
)


def validate_species_frame(frame: pd.DataFrame) -> None:
    missing = [column for column in SPECIES_COLUMNS if column not in frame.columns]
    if missing:
        raise ValueError(f"species table is missing {missing}")
    if frame.empty:
        raise ValueError("species table is empty")
    if frame["scientific_name"].duplicated().any():
        dupes = frame.loc[frame["scientific_name"].duplicated(), "scientific_name"].head(5)
        raise ValueError(f"duplicate scientific names: {list(dupes)}")
    if frame["scientific_name"].isna().any() or frame["taxonomic_order"].isna().any():
        raise ValueError("scientific name and order are required")
    if frame["family"].isna().any():
        raise ValueError("family is required")
    codes = frame["iucn_category"].map(normalize_iucn_category)
    unexpected = sorted(
        {
            str(code)
            for code in codes
            if not pd.isna(code) and code not in KNOWN_CATEGORIES
        }
    )
    if unexpected:
        raise ValueError(f"unexpected IUCN categories: {unexpected}")
    if frame["iucn_category"].map(normalize_iucn_category).notna().sum() == 0:
        raise ValueError("species table has no published IUCN categories to train on")
