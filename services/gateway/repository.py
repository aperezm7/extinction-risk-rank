"""Postgres and in-memory readers. Neither one fits a model."""

from __future__ import annotations

import math
from typing import Protocol

import pandas as pd

from services.gateway.queries import METRICS_SQL, ORDER_EXISTS_SQL, SPECIES_SQL, WATCHLIST_SQL


def normalize_name(name: str) -> str:
    return " ".join(name.replace("_", " ").split()).casefold()


def _missing(value) -> bool:
    if value is None:
        return True
    if isinstance(value, float) and math.isnan(value):
        return True
    try:
        return bool(pd.isna(value))
    except TypeError:
        return False


def json_float(value):
    if _missing(value):
        return None
    return float(value)


def threatened_flag(label):
    if _missing(label):
        return None
    return bool(int(label))


def watch_row(row) -> dict:
    return {
        "scientific_name": row["scientific_name"],
        "family": row["family"],
        "iucn_category": None if _missing(row["iucn_category"]) else str(row["iucn_category"]),
        "threatened": threatened_flag(row["threatened_label"]),
        "threat_score": json_float(row["threat_score"]),
        "score": json_float(row["threat_score"]),
    }


class SpeciesRepository(Protocol):
    def get_species(self, name: str) -> dict | None: ...

    def order_name(self, order: str) -> str | None: ...

    def highest_in_order(self, order: str, n: int) -> list[dict]: ...

    def metrics(self) -> dict: ...

    def close(self) -> None: ...


class MemorySpeciesRepository:
    def __init__(self, scored: pd.DataFrame, report: dict):
        self._frame = scored.reset_index(drop=True)
        self._report = report

    def get_species(self, name: str) -> dict | None:
        key = normalize_name(name)
        names = self._frame["scientific_name"].map(normalize_name)
        hit = self._frame.loc[names.eq(key)]
        if hit.empty:
            return None
        return hit.iloc[0].to_dict()

    def order_name(self, order: str) -> str | None:
        match = self._frame.loc[
            self._frame["taxonomic_order"].str.upper().eq(order.strip().upper()),
            "taxonomic_order",
        ]
        if match.empty:
            return None
        return str(match.iloc[0])

    def highest_in_order(self, order: str, n: int) -> list[dict]:
        subset = self._frame.loc[
            self._frame["taxonomic_order"].str.upper().eq(order.strip().upper())
            & self._frame["threat_score"].notna()
        ]
        subset = subset.sort_values(["threat_score", "scientific_name"], ascending=[False, True])
        return [watch_row(row) for _, row in subset.head(n).iterrows()]

    def metrics(self) -> dict:
        return dict(self._report)

    def close(self) -> None:
        return None


class PostgresSpeciesRepository:
    def __init__(self, connection):
        self._connection = connection

    def get_species(self, name: str) -> dict | None:
        row = self._connection.execute(SPECIES_SQL, {"name": normalize_name(name)}).fetchone()
        return dict(row) if row else None

    def order_name(self, order: str) -> str | None:
        row = self._connection.execute(
            ORDER_EXISTS_SQL, {"taxonomic_order": order.strip()}
        ).fetchone()
        if row is None:
            return None
        return str(row["taxonomic_order"])

    def highest_in_order(self, order: str, n: int) -> list[dict]:
        rows = self._connection.execute(
            WATCHLIST_SQL, {"taxonomic_order": order.strip(), "n": int(n)}
        ).fetchall()
        return [watch_row(row) for row in rows]

    def metrics(self) -> dict:
        row = self._connection.execute(METRICS_SQL).fetchone()
        if row is None:
            return {}
        report = dict(row)
        report["model"] = "HistGradientBoostingClassifier"
        report["split"] = "family"
        return report

    def close(self) -> None:
        self._connection.close()
