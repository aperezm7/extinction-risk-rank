"""Load a starter or the hidden solution of the same challenge."""

from __future__ import annotations

import importlib
import os

SLUGS = {
    "01": "01_iucn_label",
    "02": "02_log_body_mass",
    "03": "03_family_split",
    "04": "04_top_decile_precision",
    "05": "05_greedy_family_cover",
}


def use_hidden() -> bool:
    """Hidden solutions are the default so `pytest` passes on a fresh clone.

    Set CHALLENGE_USE_HIDDEN=0 to run the starters instead.
    """
    return os.environ.get("CHALLENGE_USE_HIDDEN", "1") != "0"


def load(number: str):
    slug = SLUGS[number.zfill(2)]
    if use_hidden():
        return importlib.import_module(f"challenges.hidden.{slug}")
    return importlib.import_module(f"challenges.{slug}.starter")
