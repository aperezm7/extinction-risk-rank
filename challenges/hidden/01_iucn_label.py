"""Hidden solution for challenge 01. Mirrors src.labels."""

from __future__ import annotations

import math

import pandas as pd

_FULL_NAMES = {
    "CRITICALLY ENDANGERED": "CR",
    "ENDANGERED": "EN",
    "VULNERABLE": "VU",
    "NEAR THREATENED": "NT",
    "LEAST CONCERN": "LC",
    "DATA DEFICIENT": "DD",
    "EXTINCT": "EX",
    "EXTINCT IN THE WILD": "EW",
    "NOT EVALUATED": "NE",
}


def normalize_iucn_category(category) -> str | None:
    if category is None:
        return None
    if isinstance(category, float) and math.isnan(category):
        return None
    try:
        if pd.isna(category):
            return None
    except TypeError:
        pass
    text = str(category).strip().upper()
    if text in {"", "NAN", "NONE", "NA", "<NA>", "NULL"}:
        return None
    text = _FULL_NAMES.get(text, text)
    compact = text.replace(" ", "")
    if compact in {"CR(PE)", "CR(PEW)"}:
        return "CR"
    return text


def map_iucn_label(category) -> int | None:
    code = normalize_iucn_category(category)
    if code in {"CR", "EN", "VU"}:
        return 1
    if code in {"NT", "LC"}:
        return 0
    return None


def drop_data_deficient(frame: pd.DataFrame, category_col: str = "iucn_category") -> pd.DataFrame:
    codes = frame[category_col].map(normalize_iucn_category)
    return frame.loc[codes.ne("DD")].copy().reset_index(drop=True)
