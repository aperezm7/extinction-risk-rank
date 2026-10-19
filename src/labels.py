"""Map published IUCN categories onto the binary contrast used for training."""

from __future__ import annotations

import math

import pandas as pd

THREATENED = frozenset({"CR", "EN", "VU"})
NOT_THREATENED = frozenset({"NT", "LC"})

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
    """Return a short IUCN code, or None when the cell is empty."""
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
    """Threatened (CR, EN, VU) -> 1, not threatened (NT, LC) -> 0.

    Data deficient and every other category, including EX and EW, return None.
    The caller decides whether None drops the row.
    """
    code = normalize_iucn_category(category)
    if code in THREATENED:
        return 1
    if code in NOT_THREATENED:
        return 0
    return None


def drop_data_deficient(frame: pd.DataFrame, category_col: str = "iucn_category") -> pd.DataFrame:
    """Remove data-deficient rows. EX, EW, and blank categories stay."""
    codes = frame[category_col].map(normalize_iucn_category)
    kept = frame.loc[codes.ne("DD")].copy()
    return kept.reset_index(drop=True)


def rows_for_service(frame: pd.DataFrame, category_col: str = "iucn_category") -> pd.DataFrame:
    """Rows the API is allowed to score.

    Drops DD, EP, EX, EW, and any other non-empty category that is not
    CR, EN, VU, NT, or LC. Those codes are not in the training contrast.
    A blank category would stay. PHYLACINE 1.2.1 has a status on every row,
    so the scored table is the binary labeled set.
    """
    codes = frame[category_col].map(normalize_iucn_category)
    labels = frame[category_col].map(map_iucn_label)
    keep = codes.isna() | labels.notna()
    out = frame.loc[keep].copy()
    out["threatened_label"] = labels.loc[keep].astype("Int64")
    return out.reset_index(drop=True)
