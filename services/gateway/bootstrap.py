"""Load the species CSV, fit the serving model, and store scores."""

from __future__ import annotations

import math
from pathlib import Path

import pandas as pd
import psycopg
from psycopg.rows import dict_row

from services.data.columns import SPECIES_COLUMNS
from services.data.parse import read_species_csv
from services.gateway.repository import PostgresSpeciesRepository
from services.model.train import train_species_table

SCHEMA_PATH = Path(__file__).resolve().parents[1] / "data" / "schema.sql"


def apply_schema(connection) -> None:
    script = SCHEMA_PATH.read_text()
    for statement in script.split(";"):
        sql = statement.strip()
        if sql:
            connection.execute(sql)


def _db_value(value):
    if isinstance(value, str):
        return value
    if value is None:
        return None
    if hasattr(value, "item") and not isinstance(value, (bytes, bytearray)):
        try:
            value = value.item()
        except Exception:
            pass
    try:
        if pd.isna(value):
            return None
    except TypeError:
        pass
    if isinstance(value, float) and math.isnan(value):
        return None
    return value


def load_species(connection, frame: pd.DataFrame) -> None:
    connection.execute("TRUNCATE species, training_report")
    columns = list(SPECIES_COLUMNS) + ["threatened_label", "threat_score"]
    placeholders = ", ".join(["%s"] * len(columns))
    sql = f"INSERT INTO species ({', '.join(columns)}) VALUES ({placeholders})"
    rows = []
    for record in frame.to_dict(orient="records"):
        rows.append(tuple(_db_value(record.get(column)) for column in columns))
    with connection.cursor() as cursor:
        cursor.executemany(sql, rows)


def save_report(connection, report: dict) -> None:
    connection.execute(
        """
        INSERT INTO training_report (
            id, roc_auc, precision_top_10, n_labeled, n_train, n_test,
            n_scored, random_state, positive_rate
        ) VALUES (1, %s, %s, %s, %s, %s, %s, %s, %s)
        ON CONFLICT (id) DO UPDATE SET
            roc_auc = EXCLUDED.roc_auc,
            precision_top_10 = EXCLUDED.precision_top_10,
            n_labeled = EXCLUDED.n_labeled,
            n_train = EXCLUDED.n_train,
            n_test = EXCLUDED.n_test,
            n_scored = EXCLUDED.n_scored,
            random_state = EXCLUDED.random_state,
            positive_rate = EXCLUDED.positive_rate
        """,
        (
            report["roc_auc"],
            report["precision_top_10"],
            report["n_labeled"],
            report["n_train"],
            report["n_test"],
            report["n_scored"],
            report["random_state"],
            report["positive_rate"],
        ),
    )


def connect_with_retry(database_url: str, attempts: int = 30, delay: float = 1.0):
    import time

    last_error = None
    for _ in range(attempts):
        try:
            return psycopg.connect(database_url, row_factory=dict_row)
        except psycopg.OperationalError as exc:
            last_error = exc
            time.sleep(delay)
    raise last_error


def bootstrap(database_url: str, species_csv: Path, random_state: int = 0) -> PostgresSpeciesRepository:
    """Replace the species table from a local CSV, train, and store scores."""
    frame = read_species_csv(species_csv)
    scored, report, _model = train_species_table(frame, random_state=random_state)
    connection = connect_with_retry(database_url)
    connection.execute("DROP TABLE IF EXISTS species")
    connection.execute("DROP TABLE IF EXISTS training_report")
    apply_schema(connection)
    load_species(connection, scored)
    save_report(connection, report)
    connection.commit()
    return PostgresSpeciesRepository(connection)
