"""Service tests on the committed fixture. They do not download the deposit."""

from __future__ import annotations

import math
import urllib.request
from pathlib import Path

import pandas as pd
import pytest
from fastapi.testclient import TestClient

from services.data.parse import read_species_csv
from services.gateway.app import create_app
from services.gateway.queries import WATCHLIST_SQL
from services.gateway.repository import MemorySpeciesRepository
from services.model.train import train_species_table
from src.labels import map_iucn_label, rows_for_service

FIXTURE = Path("tests/fixtures/mammals.csv")
ROOT = Path(__file__).resolve().parents[1]


@pytest.fixture(scope="module")
def scored_bundle():
    frame = read_species_csv(FIXTURE)
    scored, report, _model = train_species_table(frame)
    return scored, report


@pytest.fixture(scope="module")
def client(scored_bundle):
    scored, report = scored_bundle
    with TestClient(create_app(MemorySpeciesRepository(scored, report))) as test_client:
        yield test_client


def test_fixture_train_does_not_download(monkeypatch):
    def blocked(*_args, **_kwargs):
        raise AssertionError("fixture train tried to use the network")

    monkeypatch.setattr(urllib.request, "urlopen", blocked)
    frame = read_species_csv(FIXTURE)
    scored, report, _model = train_species_table(frame)
    assert report["n_labeled"] == 4701
    assert report["n_test"] > 10
    assert report["n_scored"] == 4701
    assert report["split"] == "family"
    assert 0.0 <= report["roc_auc"] <= 1.0
    assert 0.0 <= report["precision_top_10"] <= 1.0
    assert len(scored) == 4701
    names = set(scored["scientific_name"])
    assert "Varecia rubra" in names
    assert "Bettongia anhydra" not in names
    assert "Oryx dammah" not in names
    assert "Acratocnus odontrigonus" not in names
    assert "Abditomys latidens" not in names
    assert set(scored["iucn_category"]) <= {"CR", "EN", "VU", "NT", "LC"}


def test_near_threatened_is_not_the_positive_class(client):
    body = client.get("/species/Genetta johnstoni").json()
    assert body["iucn_category"] == "NT"
    assert body["threatened"] is False
    assert body["order"] == "Carnivora"
    assert body["family"] == "Viverridae"
    assert 0.0 <= body["threat_score"] <= 1.0


def test_species_prediction(client):
    response = client.get("/species/Varecia%20rubra")
    assert response.status_code == 200
    body = response.json()
    assert body["scientific_name"] == "Varecia rubra"
    assert body["iucn_category"] == "CR"
    assert body["threatened"] is True
    assert body["family"] == "Lemuridae"
    assert body["order"] == "Primates"
    assert body["traits"]["log_body_mass"] == pytest.approx(math.log(3450.0))
    assert body["traits"]["diet_plant"] == pytest.approx(100.0)
    assert body["traits"]["terrestrial"] == pytest.approx(1.0)
    assert body["traits"]["aerial"] == pytest.approx(0.0)
    assert body["traits"]["island_endemicity"] == "Occurs only on isolated islands"

    underscored = client.get("/species/varecia_rubra")
    assert underscored.status_code == 200
    assert underscored.json()["scientific_name"] == "Varecia rubra"


def test_missing_body_mass_stays_missing():
    from src.features import build_features

    frame = pd.DataFrame(
        {
            "body_mass_g": [None, 0, 3450.0],
            "diet_plant": [100, 0, 100],
            "diet_vertebrate": [0, 100, 0],
            "diet_invertebrate": [0, 0, 0],
            "terrestrial": [1, 1, 1],
            "marine": [0, 0, 0],
            "freshwater": [0, 0, 0],
            "aerial": [0, 0, 0],
            "island_endemicity": ["Occurs on mainland"] * 3,
            "taxonomic_order": ["Primates", "Carnivora", "Primates"],
        }
    )
    features = build_features(frame)
    assert features.loc[0, "log_body_mass"] != features.loc[0, "log_body_mass"]
    assert features.loc[1, "log_body_mass"] != features.loc[1, "log_body_mass"]
    assert features.loc[2, "log_body_mass"] == pytest.approx(math.log(3450.0))
    assert "family" not in features.columns
    assert features.loc[2, "order_primates"] == 1.0
    assert features.loc[1, "order_carnivora"] == 1.0
    assert features.loc[2, "island_occurs_on_mainland"] == 1.0


def test_extinct_prehistoric_and_deficient_are_not_served(client):
    for name in (
        "Bettongia anhydra",
        "Oryx dammah",
        "Acratocnus odontrigonus",
        "Abditomys latidens",
    ):
        assert client.get(f"/species/{name}").status_code == 404


def test_unknown_species_and_order(client):
        assert client.get("/species/Not a mammal").status_code == 404
    missing = client.get("/watchlist", params={"order": "NotAnOrder", "n": 5})
    assert missing.status_code == 404


def test_carnivora_watchlist_ranks_and_spreads_families(client):
    response = client.get("/watchlist", params={"order": "Carnivora", "n": 20})
    assert response.status_code == 200
    body = response.json()
    assert body["order"] == "Carnivora"
    assert body["n"] == 20
    assert body["k"] == 5
    assert len(body["ranked"]) == 20
    scores = [row["threat_score"] for row in body["ranked"]]
    assert scores == sorted(scores, reverse=True)
    assert all(0.0 <= score <= 1.0 for score in scores)
    families = [row["family"] for row in body["greedy_pick"]]
    assert len(body["greedy_pick"]) == 5
    assert len(set(families)) == 5
    ranked_names = {row["scientific_name"] for row in body["ranked"]}
    assert {row["scientific_name"] for row in body["greedy_pick"]} <= ranked_names


def test_watchlist_does_not_fit_a_model(client, monkeypatch):
    def explode(*_args, **_kwargs):
        raise AssertionError("watchlist fitted a model")

    monkeypatch.setattr("src.model.train_gradient_booster", explode)
    response = client.get("/watchlist", params={"order": "Primates", "n": 20, "k": 3})
    assert response.status_code == 200
    body = response.json()
    assert body["k"] == 3
    assert len({row["family"] for row in body["greedy_pick"]}) == len(body["greedy_pick"])


def test_k_cannot_exceed_n(client):
    response = client.get("/watchlist", params={"order": "Carnivora", "n": 5, "k": 6})
    assert response.status_code == 422


def test_metrics(client):
    body = client.get("/metrics").json()
    assert body["model"] == "HistGradientBoostingClassifier"
    assert body["n_labeled"] == 4701
    assert body["n_scored"] == 4701
    assert 0.0 <= body["roc_auc"] <= 1.0


def test_service_rows_drop_extinct_and_deficient():
    frame = pd.DataFrame(
        {
            "scientific_name": ["a", "b", "c", "d", "e", "f"],
            "iucn_category": ["DD", "EX", "NT", None, "EP", "EW"],
        }
    )
    served = rows_for_service(frame)
    assert served["scientific_name"].tolist() == ["c", "d"]
    assert int(served.loc[served["scientific_name"].eq("c"), "threatened_label"].iloc[0]) == 0
    assert pd.isna(served.loc[served["scientific_name"].eq("d"), "threatened_label"].iloc[0])
    assert map_iucn_label("EN") == 1


def test_watchlist_sql_is_annotated():
    sql_doc = (ROOT / "learn" / "sql.md").read_text()
    assert WATCHLIST_SQL in sql_doc
    assert "does not fit" in sql_doc.lower() or "does not train" in sql_doc.lower()
