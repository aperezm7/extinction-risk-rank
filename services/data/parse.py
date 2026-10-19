"""Read PHYLACINE 1.2.1 traits into the species table."""

from __future__ import annotations

from pathlib import Path

import pandas as pd

from services.data.columns import SPECIES_COLUMNS

_REQUIRED = {
    "Binomial.1.2",
    "Order.1.2",
    "Family.1.2",
    "Genus.1.2",
    "Mass.g",
    "Diet.Plant",
    "Diet.Vertebrate",
    "Diet.Invertebrate",
    "Terrestrial",
    "Marine",
    "Freshwater",
    "Aerial",
    "Island.Endemicity",
    "IUCN.Status.1.2",
}

_TEXT = {
    "scientific_name",
    "taxonomic_order",
    "family",
    "genus",
    "iucn_category",
    "island_endemicity",
}


def _numeric(series: pd.Series) -> pd.Series:
    return pd.to_numeric(series, errors="coerce")


def _clean_text(value) -> str | None:
    if pd.isna(value):
        return None
    text = str(value).strip()
    if text == "" or text.lower() in {"nan", "none", "na", "<na>", "null"}:
        return None
    return text


def read_phylacine_traits(path: Path) -> pd.DataFrame:
    """Traits and IUCN.Status.1.2 from PHYLACINE Trait_data.csv.

    Binomial.1.2 uses underscores. Stored names use a space so
    `GET /species/Varecia rubra` matches the published binomial.
    Order.1.2 and Family.1.2 keep the published capitalization.
    Life habit is the four binary columns, not Life.Habit.Method.
    Diet is the three percent columns, not Diet.Method.
    """
    raw = pd.read_csv(path, na_values=["NA", "NaN", ""])
    missing = sorted(_REQUIRED - set(raw.columns))
    if missing:
        raise ValueError(f"PHYLACINE trait table is missing {missing}")
    frame = pd.DataFrame(
        {
            "scientific_name": raw["Binomial.1.2"].map(_clean_text).str.replace("_", " ", n=1, regex=False),
            "taxonomic_order": raw["Order.1.2"].map(_clean_text),
            "family": raw["Family.1.2"].map(_clean_text),
            "genus": raw["Genus.1.2"].map(_clean_text),
            "iucn_category": raw["IUCN.Status.1.2"].map(
                lambda value: None if _clean_text(value) is None else _clean_text(value).upper()
            ),
            "body_mass_g": _numeric(raw["Mass.g"]),
            "diet_plant": _numeric(raw["Diet.Plant"]),
            "diet_vertebrate": _numeric(raw["Diet.Vertebrate"]),
            "diet_invertebrate": _numeric(raw["Diet.Invertebrate"]),
            "terrestrial": _numeric(raw["Terrestrial"]),
            "marine": _numeric(raw["Marine"]),
            "freshwater": _numeric(raw["Freshwater"]),
            "aerial": _numeric(raw["Aerial"]),
            "island_endemicity": raw["Island.Endemicity"].map(_clean_text),
        }
    )
    return frame.loc[:, list(SPECIES_COLUMNS)].reset_index(drop=True)


def read_species_csv(path: Path) -> pd.DataFrame:
    """Fixture or prepared table that already uses the species-table columns."""
    frame = pd.read_csv(path, na_values=["NA", "NaN", ""])
    missing = [column for column in SPECIES_COLUMNS if column not in frame.columns]
    if missing:
        raise ValueError(f"{path} is missing {missing}")
    frame = frame.loc[:, list(SPECIES_COLUMNS)].copy()
    for column in SPECIES_COLUMNS:
        if column in _TEXT:
            frame[column] = frame[column].map(_clean_text)
        else:
            frame[column] = pd.to_numeric(frame[column], errors="coerce")
    frame["iucn_category"] = frame["iucn_category"].map(
        lambda value: None if value is None else value.upper()
    )
    return frame.reset_index(drop=True)
