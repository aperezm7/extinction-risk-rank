"""Parser for the PHYLACINE trait table, exercised on a tiny stand-in."""

from __future__ import annotations

from pathlib import Path

import pandas as pd

from services.data.parse import read_phylacine_traits, read_species_csv
from services.data.validate import validate_species_frame

FIXTURE = Path("tests/fixtures/mammals.csv")


def _raw_row(**overrides) -> dict:
    row = {
        "Binomial.1.2": "Panthera_leo",
        "Order.1.2": "Carnivora",
        "Family.1.2": "Felidae",
        "Genus.1.2": "Panthera",
        "Species.1.2": "leo",
        "Terrestrial": 1,
        "Marine": 0,
        "Freshwater": 0,
        "Aerial": 0,
        "Life.Habit.Method": "observed",
        "Mass.g": 161499.1,
        "Island.Endemicity": "Occurs on mainland",
        "IUCN.Status.1.2": "VU",
        "Diet.Plant": 0,
        "Diet.Vertebrate": 100,
        "Diet.Invertebrate": 0,
        "Diet.Method": "observed",
    }
    row.update(overrides)
    return row


def test_phylacine_names_habits_and_status(tmp_path: Path):
    path = tmp_path / "Trait_data.csv"
    pd.DataFrame(
        [
            _raw_row(),
            _raw_row(
                **{
                    "Binomial.1.2": "Genetta_johnstoni",
                    "Family.1.2": "Viverridae",
                    "Genus.1.2": "Genetta",
                    "IUCN.Status.1.2": "NT",
                    "Mass.g": 2225,
                    "Diet.Plant": 0,
                    "Diet.Vertebrate": 90,
                    "Diet.Invertebrate": 10,
                },
            ),
        ]
    ).to_csv(path, index=False)
    frame = read_phylacine_traits(path)
    validate_species_frame(frame)
    assert frame.loc[0, "scientific_name"] == "Panthera leo"
    assert frame.loc[0, "taxonomic_order"] == "Carnivora"
    assert frame.loc[0, "family"] == "Felidae"
    assert frame.loc[0, "iucn_category"] == "VU"
    assert frame.loc[0, "body_mass_g"] == 161499.1
    assert frame.loc[0, "diet_vertebrate"] == 100
    assert frame.loc[0, "terrestrial"] == 1
    assert frame.loc[0, "island_endemicity"] == "Occurs on mainland"
    assert "Diet.Method" not in frame.columns
    assert frame.loc[1, "scientific_name"] == "Genetta johnstoni"
    assert frame.loc[1, "iucn_category"] == "NT"


def test_fixture_is_the_full_phylacine_extract():
    frame = read_species_csv(FIXTURE)
    validate_species_frame(frame)
    assert len(frame) == 5831
    assert int(frame["iucn_category"].isin(["CR", "EN", "VU", "NT", "LC"]).sum()) == 4701
    assert int(frame["iucn_category"].isin(["EP", "EX", "EW", "DD"]).sum()) == 1130
    assert int(frame["taxonomic_order"].eq("Carnivora").sum()) == 313
    varecia = frame.loc[frame["scientific_name"].eq("Varecia rubra")].iloc[0]
    assert varecia["iucn_category"] == "CR"
    assert varecia["family"] == "Lemuridae"
    assert varecia["body_mass_g"] == 3450
