"""Trait transforms. Missing measurements stay missing.

Family.1.2 is the holdout group and the watchlist family. It is not a
covariate: a family-grouped split would otherwise let the booster memorize
which families are threatened, and a held-out family would be an unseen level.
"""

from __future__ import annotations

import numpy as np
import pandas as pd

# Published PHYLACINE 1.2.1 levels. Fixed here so train and test share columns.
ORDER_LEVELS = (
    "Afrosoricida",
    "Carnivora",
    "Cetartiodactyla",
    "Chiroptera",
    "Cingulata",
    "Dasyuromorphia",
    "Dermoptera",
    "Didelphimorphia",
    "Diprotodontia",
    "Eulipotyphla",
    "Hyracoidea",
    "Lagomorpha",
    "Litopterna",
    "Macroscelidea",
    "Microbiotheria",
    "Monotremata",
    "Notoryctemorphia",
    "Notoungulata",
    "Paucituberculata",
    "Peramelemorphia",
    "Perissodactyla",
    "Pholidota",
    "Pilosa",
    "Primates",
    "Proboscidea",
    "Rodentia",
    "Scandentia",
    "Sirenia",
    "Tubulidentata",
)

ISLAND_LEVELS = (
    "Exclusively marine",
    "Occurs on large land bridge islands",
    "Occurs on mainland",
    "Occurs on small land bridge islands",
    "Occurs only on isolated islands",
)

# Raw columns the model matrix reads. Mass is grams. Diet columns are percents.
TRAIT_COLUMNS = (
    "body_mass_g",
    "diet_plant",
    "diet_vertebrate",
    "diet_invertebrate",
    "terrestrial",
    "marine",
    "freshwater",
    "aerial",
    "island_endemicity",
    "taxonomic_order",
)

_NUMERIC_TRAITS = (
    "diet_plant",
    "diet_vertebrate",
    "diet_invertebrate",
    "terrestrial",
    "marine",
    "freshwater",
    "aerial",
)


def indicator_name(prefix: str, level: str) -> str:
    slug = "".join(char.lower() if char.isalnum() else "_" for char in level.strip())
    while "__" in slug:
        slug = slug.replace("__", "_")
    return f"{prefix}_{slug.strip('_')}"


def _indicator_columns(levels: tuple[str, ...], prefix: str) -> tuple[str, ...]:
    return tuple(indicator_name(prefix, level) for level in levels)


FEATURE_COLUMNS = (
    ("log_body_mass",)
    + _NUMERIC_TRAITS
    + _indicator_columns(ISLAND_LEVELS, "island")
    + _indicator_columns(ORDER_LEVELS, "order")
)


def log_body_mass(body_mass) -> pd.Series:
    """Natural log of body mass in grams.

    Missing values stay missing. Non-positive masses stay missing because
    the logarithm is undefined. Nothing is imputed.
    """
    values = pd.to_numeric(pd.Series(body_mass, copy=True), errors="coerce")
    logged = pd.Series(np.log(values.where(values > 0)), index=values.index, name="log_body_mass")
    return logged


def _indicators(series: pd.Series, levels: tuple[str, ...], prefix: str) -> pd.DataFrame:
    text = series.map(lambda value: "" if pd.isna(value) else str(value).strip())
    columns = {
        indicator_name(prefix, level): text.eq(level).astype(float)
        for level in levels
    }
    return pd.DataFrame(columns, index=series.index)


def build_features(frame: pd.DataFrame) -> pd.DataFrame:
    """Numeric model matrix. NaN marks a trait the table did not report.

    Order and island endemicity are one-hot columns from the fixed PHYLACINE
    vocabularies. An unknown level is all zeros. Family is not included.
    """
    missing = [column for column in TRAIT_COLUMNS if column not in frame.columns]
    if missing:
        raise KeyError(f"species table is missing {missing}")
    features = pd.DataFrame(index=frame.index)
    features["log_body_mass"] = log_body_mass(frame["body_mass_g"]).to_numpy()
    for column in _NUMERIC_TRAITS:
        features[column] = pd.to_numeric(frame[column], errors="coerce")
    features = pd.concat(
        [
            features,
            _indicators(frame["island_endemicity"], ISLAND_LEVELS, "island"),
            _indicators(frame["taxonomic_order"], ORDER_LEVELS, "order"),
        ],
        axis=1,
    )
    return features.loc[:, list(FEATURE_COLUMNS)]
