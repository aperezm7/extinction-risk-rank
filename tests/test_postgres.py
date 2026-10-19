"""Postgres holds the species table. Skipped unless DATABASE_URL is reachable."""

from __future__ import annotations

import os

import psycopg
import pytest
from fastapi.testclient import TestClient

from services.gateway.app import create_app
from services.gateway.queries import WATCHLIST_SQL


@pytest.fixture(scope="module")
def database_url():
    url = os.environ.get("DATABASE_URL")
    if not url:
        pytest.skip("DATABASE_URL is not set")
    try:
        with psycopg.connect(url) as connection:
            connection.execute("SELECT 1")
    except Exception as exc:
        pytest.skip(f"Postgres is not reachable: {exc}")
    return url


def test_gateway_against_postgres(database_url):
    os.environ["DATABASE_URL"] = database_url
    os.environ["SPECIES_CSV"] = "tests/fixtures/mammals.csv"
    with TestClient(create_app()) as client:
        health = client.get("/health")
        assert health.status_code == 200
        species = client.get("/species/Varecia rubra")
        assert species.status_code == 200
        body = species.json()
        assert body["iucn_category"] == "CR"
        assert body["threatened"] is True
        assert 0.0 <= body["threat_score"] <= 1.0
        watch = client.get("/watchlist", params={"order": "Carnivora", "n": 20})
        assert watch.status_code == 200
        ranked = watch.json()["ranked"]
        assert len(ranked) == 20
        scores = [row["threat_score"] for row in ranked]
        assert scores == sorted(scores, reverse=True)

        connection = client.app.state.repo._connection
        rows = connection.execute(WATCHLIST_SQL, {"taxonomic_order": "Carnivora", "n": 20}).fetchall()
        assert [row["scientific_name"] for row in rows] == [item["scientific_name"] for item in ranked]
