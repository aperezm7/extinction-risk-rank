"""FastAPI gateway. The only public entrypoint."""

from __future__ import annotations

import os
from contextlib import asynccontextmanager
from pathlib import Path

import pandas as pd
from fastapi import FastAPI, HTTPException, Query

from services.features.transform import species_feature_matrix
from services.gateway.repository import json_float, normalize_name, threatened_flag
from src.cover import greedy_family_cover

DEFAULT_SPECIES_CSV = Path("tests/fixtures/mammals.csv")


def _text(value):
    if value is None:
        return None
    try:
        if pd.isna(value):
            return None
    except TypeError:
        pass
    text = str(value).strip()
    if text == "" or text.lower() == "nan":
        return None
    return text


_TRAIT_NUMBERS = (
    "body_mass_g",
    "diet_plant",
    "diet_vertebrate",
    "diet_invertebrate",
    "terrestrial",
    "marine",
    "freshwater",
    "aerial",
)


def _traits(row: dict) -> dict:
    features = species_feature_matrix(pd.DataFrame([row])).iloc[0]
    payload = {column: json_float(row.get(column)) for column in _TRAIT_NUMBERS}
    payload["log_body_mass"] = json_float(features["log_body_mass"])
    payload["island_endemicity"] = _text(row.get("island_endemicity"))
    return payload


def _species_payload(row: dict) -> dict:
    category = _text(row.get("iucn_category"))
    return {
        "scientific_name": row["scientific_name"],
        "order": row["taxonomic_order"],
        "family": row["family"],
        "genus": _text(row.get("genus")),
        "iucn_category": category,
        "threatened": threatened_flag(row.get("threatened_label")),
        "threat_score": json_float(row.get("threat_score")),
        "traits": _traits(row),
    }


def register_routes(app: FastAPI) -> None:
    @app.get("/health")
    def health():
        return {"status": "ok"}

    @app.get("/metrics")
    def metrics():
        report = app.state.repo.metrics()
        if not report:
            raise HTTPException(status_code=404, detail="No training report is stored.")
        return report

    @app.get("/species/{name}")
    def species(name: str):
        row = app.state.repo.get_species(normalize_name(name))
        if row is None:
            raise HTTPException(
                status_code=404,
                detail=f"No species named {name!r} in the trait table.",
            )
        return _species_payload(row)

    @app.get("/watchlist")
    def watchlist(
        order: str = Query(..., min_length=1, description="Taxonomic order, for example Carnivora"),
        n: int = Query(20, ge=1, le=200),
        k: int | None = Query(None, ge=1, le=200),
    ):
        """Highest stored scores in one order, plus a short family-covering pick.

        This does not fit a model. Scores were written when the service started.
        """
        if k is None:
            k = min(5, n)
        if k > n:
            raise HTTPException(status_code=422, detail="k cannot exceed n.")
        stored_order = app.state.repo.order_name(order)
        if stored_order is None:
            raise HTTPException(status_code=404, detail=f"No species in order {order!r}.")
        ranked = app.state.repo.highest_in_order(stored_order, n)
        picked = greedy_family_cover(ranked, k)
        return {
            "order": stored_order,
            "n": n,
            "k": k,
            "ranked": [_public_watch(row) for row in ranked],
            "greedy_pick": [_public_watch(row) for row in picked],
        }


def _public_watch(row: dict) -> dict:
    return {
        "scientific_name": row["scientific_name"],
        "family": row["family"],
        "iucn_category": row["iucn_category"],
        "threatened": row["threatened"],
        "threat_score": row["threat_score"],
    }


def create_app(repo=None) -> FastAPI:
    @asynccontextmanager
    async def lifespan(app: FastAPI):
        if repo is None:
            from services.gateway.bootstrap import bootstrap

            database_url = os.environ.get("DATABASE_URL")
            if not database_url:
                raise RuntimeError("DATABASE_URL is not set")
            csv_path = Path(os.environ.get("SPECIES_CSV", DEFAULT_SPECIES_CSV))
            if not csv_path.exists():
                raise RuntimeError(f"species CSV not found: {csv_path}")
            app.state.repo = bootstrap(database_url, csv_path)
            close = True
        else:
            app.state.repo = repo
            close = False
        yield
        if close:
            app.state.repo.close()

    app = FastAPI(
        title="Extinction risk rank",
        summary="Trait scores for mammals, compared with published IUCN categories.",
        lifespan=lifespan,
    )
    register_routes(app)
    return app


app = create_app()
